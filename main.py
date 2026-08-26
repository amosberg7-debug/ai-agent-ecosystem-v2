"""Entry point for your AI Agent Ecosystem."""
from agents.supervisor import SupervisorAgent
from memory.store import MemoryStore
from brain_router import BrainRouter


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           🤖 AI AGENT ECOSYSTEM - v2.0.0                   ║
    ║                                                              ║
    ║  Multi-Brain • Human-in-the-Loop • Budget Protection       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    memory = MemoryStore()
    router = BrainRouter()
    agent = SupervisorAgent()

    stats = memory.get_stats()
    print(f"📊 Ecosystem Stats:")
    print(f"   Total Episodes: {stats['total_episodes']}")
    print(f"   Success Rate: {stats['success_rate']}%")
    print(f"   Skills Learned: {stats['total_skills']}")
    print(f"   Human Decisions: {stats['total_decisions']}")
    print("-" * 60)

    print(router.get_budget_report())
    print("-" * 60)

    print("\n💡 Enter tasks for your agent. Type 'quit' to exit.")
    print("   Type 'budget' to see spending.")
    print("   Type 'test' to run the test suite.")
    print("-" * 60)

    while True:
        try:
            task = input("\n🎯 Task: ").strip()
            if task.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Shutting down ecosystem. Goodbye!")
                break
            if task.lower() == 'budget':
                print("\n" + router.get_budget_report())
                continue
            if task.lower() == 'test':
                run_tests()
                continue
            if not task:
                continue

            print("\n⏳ Agent is working...")
            result = agent.run(task)
            print(f"\n✅ Result: {result.get('final_output', 'Done')}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def run_tests():
    """Quick test of the brain router."""
    print("\n🧪 RUNNING TESTS...")
    router = BrainRouter()

    test_tasks = [
        ("Write a Python script to scrape prices", "codex", "Coding task"),
        ("Analyze my competitor's strategy", "claude", "Complex reasoning"),
        ("Summarize the README file", "ollama", "Simple task"),
        ("Check my crypto wallet balance", "ollama", "Sensitive task"),
        ("Build a landing page", "codex", "Coding task"),
    ]

    passed = 0
    for task, expected_brain, reason in test_tasks:
        result = router.route(task)
        actual = result['brain']
        status = "✅" if actual == expected_brain else "⚠️ "
        print(f"{status} '{task[:40]}...' -> {actual} (expected: {expected_brain})")
        if actual == expected_brain:
            passed += 1

    print(f"\n📊 {passed}/{len(test_tasks)} tests passed")
    if passed == len(test_tasks):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check your API keys and Ollama setup.")


if __name__ == "__main__":
    main()
