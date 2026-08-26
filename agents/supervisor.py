"""The main agent with HITL, memory, learning, and dynamic brain routing."""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from config import Config
from memory.store import MemoryStore
from tools.toolkit import Toolkit
from brain_router import BrainRouter


def get_llm_for_route(route: Dict):
    """Dynamically create the right LLM based on the router's decision."""
    provider = route.get("provider", "ollama")
    try:
        if provider == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=route["model_id"],
                base_url=route.get("base_url", "http://localhost:11434"),
                temperature=0.2
            )
        elif provider == "openrouter":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=route["model_id"],
                api_key=route.get("api_key"),
                base_url=route.get("base_url"),
                temperature=0.2
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=route["model_id"],
                api_key=route.get("api_key"),
                base_url=route.get("base_url", "https://api.openai.com/v1"),
                temperature=0.2
            )
        else:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model="codestral",
                base_url="http://localhost:11434",
                temperature=0.2
            )
    except Exception as e:
        print(f"⚠️  Failed to load {provider} LLM: {e}")
        print(f"   Falling back to Ollama...")
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="codestral",
            base_url="http://localhost:11434",
            temperature=0.2
        )


def safe_llm_call(llm, prompt, max_retries=3):
    """Call LLM with retries and rate limiting."""
    for attempt in range(max_retries):
        try:
            # Rate limiting: wait at least 1 second between calls
            elapsed = time.time() - safe_llm_call.last_call_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            safe_llm_call.last_call_time = time.time()

            return llm.invoke(prompt)
        except Exception as e:
            wait_time = 2 ** attempt
            print(f"   ⚠️  API error (attempt {attempt + 1}/{max_retries}): {e}")
            print(f"   Retrying in {wait_time}s...")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise e

safe_llm_call.last_call_time = 0


class AgentState(TypedDict):
    messages: List[Any]
    task: str
    plan: List[str]
    current_step: int
    action_proposed: Dict
    human_decision: str
    memory_context: str
    skills_context: str
    final_output: str
    route: Dict


class SupervisorAgent:
    def __init__(self):
        self.memory = MemoryStore()
        self.toolkit = Toolkit()
        self.router = BrainRouter()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("load_memory", self._load_memory)
        workflow.add_node("plan_task", self._plan_task)
        workflow.add_node("propose_action", self._propose_action)
        workflow.add_node("human_review", self._human_review_gate)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("reflect", self._reflect)
        workflow.add_node("learn", self._learn)
        workflow.set_entry_point("load_memory")
        workflow.add_edge("load_memory", "plan_task")
        workflow.add_edge("plan_task", "propose_action")
        workflow.add_edge("propose_action", "human_review")
        workflow.add_edge("human_review", "execute_action")
        workflow.add_edge("execute_action", "reflect")
        workflow.add_conditional_edges(
            "reflect",
            self._should_continue,
            {"continue": "propose_action", "finish": "learn"}
        )
        workflow.add_edge("learn", END)
        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer)

    def _load_memory(self, state: AgentState):
        task = state["task"]
        episodes = self.memory.get_relevant_episodes(task, limit=3)
        memory_context = ""
        if episodes:
            memory_context = "Past similar tasks:\n"
            for ep in episodes:
                memory_context += f"- Task: {ep['task']}\n"
                memory_context += f"  Outcome: {ep['outcome']}\n"
                memory_context += f"  Lessons: {ep['lessons']}\n"
        skills = self.memory.get_skills()
        skills_context = ""
        if skills:
            skills_context = "Available skills:\n"
            for skill in skills[:5]:
                skills_context += f"- {skill['name']}: {skill['description']}\n"
        return {
            **state,
            "memory_context": memory_context,
            "skills_context": skills_context
        }

    def _plan_task(self, state: AgentState):
        # ROUTE THE TASK TO THE RIGHT BRAIN
        route = self.router.route(state["task"])
        print(f"\n🧠 Brain: {route['brain']} | Model: {route['model_id']}")
        print(f"   Why: {route['reason']}")
        print(f"   Est. Cost: ${route['estimated_cost']:.3f}")

        # Check global kill switch
        if self.router.global_kill_switch():
            print(f"   🚨 GLOBAL KILL SWITCH ACTIVE - All cloud brains disabled")

        system_prompt = f"""You are {Config.AGENT_NAME}, an AI agent with memory and learning.
You have access to these tools:
- search_web: Search the internet
- read_file: Read files from the project
- write_file: Write files (requires approval)
- execute_sandbox: Run commands in sandbox (requires approval)

{state["memory_context"]}
{state["skills_context"]}

Create a concise plan (3-5 steps) to complete the task."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Task: {state['task']}")
        ])

        llm = get_llm_for_route(route)
        try:
            response = safe_llm_call(llm, prompt.format_messages())
        except Exception as e:
            print(f"   ❌ Brain failed: {e}")
            print(f"   Falling back to Ollama...")
            route = self.router._get_brain_config("ollama", "Emergency fallback")
            llm = get_llm_for_route(route)
            response = safe_llm_call(llm, prompt.format_messages())

        plan_text = response.content
        steps = [line.strip("- \n") for line in plan_text.split("\n") if line.strip().startswith("-")]
        if not steps:
            steps = [plan_text]

        return {**state, "plan": steps, "current_step": 0, "route": route}

    def _propose_action(self, state: AgentState):
        if state["current_step"] >= len(state["plan"]):
            return {**state, "action_proposed": {"type": "finish", "details": "Task complete"}}

        step = state["plan"][state["current_step"]]
        route = state.get("route", self.router._get_brain_config("ollama", "Default"))

        system_prompt = """Convert this plan step into a concrete tool action.
Available tools: search_web, read_file, write_file, execute_sandbox
Respond in JSON format:
{"tool": "tool_name", "params": {"param1": "value"}, "rationale": "why this action"}"""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Plan step: {step}")
        ])

        llm = get_llm_for_route(route)
        try:
            response = safe_llm_call(llm, prompt.format_messages())
        except Exception as e:
            print(f"   ❌ Brain failed: {e}")
            route = self.router._get_brain_config("ollama", "Emergency fallback")
            llm = get_llm_for_route(route)
            response = safe_llm_call(llm, prompt.format_messages())

        try:
            action = json.loads(response.content)
        except:
            action = {"tool": "search_web", "params": {"query": step}, "rationale": "Fallback search"}

        return {**state, "action_proposed": action}

    def _human_review_gate(self, state: AgentState):
        action = state["action_proposed"]

        if action.get("type") == "finish":
            return {**state, "human_decision": "approve"}

        tool = action.get("tool", "")
        if tool in Config.GREEN_ACTIONS:
            risk = "GREEN - Low risk"
        elif tool in Config.YELLOW_ACTIONS:
            risk = "YELLOW - Medium risk"
        elif tool in Config.RED_ACTIONS:
            risk = "RED - High risk"
        else:
            risk = "UNKNOWN"

        print("\n" + "="*60)
        print(f"🤖 AGENT {Config.AGENT_NAME} REQUESTS APPROVAL")
        print("="*60)
        print(f"Step {state['current_step'] + 1}/{len(state['plan'])}")
        print(f"Action: {action['tool']}")
        print(f"Params: {json.dumps(action.get('params', {}), indent=2)}")
        print(f"Rationale: {action.get('rationale', 'N/A')}")
        print(f"Risk Level: {risk}")
        print("="*60)

        if not Config.HITL_ENABLED or tool in Config.GREEN_ACTIONS:
            print("✅ Auto-approved (HITL disabled or green action)")
            decision = "approve"
        else:
            decision = input("Your decision [approve/amend/skip/abort]: ").strip().lower()
            if decision not in ["approve", "amend", "skip", "abort"]:
                decision = "approve"

        self.memory.log_audit(
            agent_name=Config.AGENT_NAME,
            action_type=action["tool"],
            action_details=json.dumps(action),
            approved_by="human_operator",
            decision=decision
        )

        return {**state, "human_decision": decision}

    def _execute_action(self, state: AgentState):
        action = state["action_proposed"]
        decision = state["human_decision"]

        if decision == "abort":
            return {**state, "final_output": "Task aborted by operator"}

        if decision == "skip":
            return {**state, "current_step": state["current_step"] + 1}

        tool_name = action.get("tool", "")
        params = action.get("params", {})

        result = ""
        if tool_name == "search_web":
            result = self.toolkit.search_web(params.get("query", ""))
        elif tool_name == "read_file":
            result = self.toolkit.read_file(params.get("path", ""))
        elif tool_name == "write_file":
            result = f"[Would write to {params.get('path')}]"
        elif tool_name == "execute_sandbox":
            result = f"[Would execute: {params.get('command')}]"
        else:
            result = f"[Unknown tool: {tool_name}]"

        new_messages = state["messages"] + [
            AIMessage(content=f"Executed {tool_name}: {result[:500]}...")
        ]

        return {
            **state,
            "messages": new_messages,
            "current_step": state["current_step"] + 1
        }

    def _reflect(self, state: AgentState):
        if state["current_step"] >= len(state["plan"]):
            return {**state, "final_output": "Task completed successfully"}
        return state

    def _should_continue(self, state: AgentState):
        if state.get("human_decision") == "abort":
            return "finish"
        if state["current_step"] >= len(state["plan"]):
            return "finish"
        return "continue"

    def _learn(self, state: AgentState):
        self.memory.save_episode(
            agent_name=Config.AGENT_NAME,
            task=state["task"],
            actions=state["plan"],
            outcome=state.get("final_output", "Completed"),
            success=state.get("human_decision") != "abort",
            lessons="Task completed with human oversight"
        )
        return state

    def run(self, task: str, thread_id: str = None):
        thread_id = thread_id or f"task_{datetime.now().timestamp()}"
        initial_state = {
            "messages": [HumanMessage(content=task)],
            "task": task,
            "plan": [],
            "current_step": 0,
            "action_proposed": {},
            "human_decision": "",
            "memory_context": "",
            "skills_context": "",
            "final_output": "",
            "route": {}
        }
        result = self.graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}, "recursion_limit": 100}
        )
        return result


if __name__ == "__main__":
    print("🚀 AI Agent Ecosystem - Supervisor Agent")
    print("="*60)
    agent = SupervisorAgent()
    stats = agent.memory.get_stats()
    print(f"📊 Memory Stats: {stats}")
    print("="*60)
    task = input("\nEnter a task for the agent: ").strip()
    if not task:
        task = "Search for the latest news about AI agents in 2026"
    print(f"\n🎯 Task: {task}")
    print("-"*60)
    result = agent.run(task)
    print("\n✅ Final Result:")
    print(result.get("final_output", "No output"))
