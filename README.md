# 🤖 AI Agent Ecosystem v2.0 — Bulletproof Starter

A self-hosted, multi-brain AI agent system with **human-in-the-loop control**, **automatic cost protection**, and **privacy-first architecture**.

## What This Is (In Plain English)

This is your AI workforce. Instead of one chatbot, you get a **team of specialized AI brains** that:
- **Claude** handles strategy, research, and complex thinking
- **Codex** writes code, builds tools, and debugs scripts  
- **Ollama** (free, local) handles simple tasks and sensitive data
- **You** approve every important decision from your phone or computer
- **The system** automatically picks the cheapest brain for each job and stops spending if you hit your daily limit

## What Makes It "Bulletproof"

| Feature | What It Protects You From |
|---------|--------------------------|
| **Brain Router** | Wasting money on expensive AI for simple tasks |
| **Cost Kill Switch** | A bug burning through your $50 credit in 20 minutes |
| **Error Retries** | One failed API call killing your entire task |
| **Rate Limiting** | Getting banned by OpenRouter for too many requests |
| **Ollama Fallback** | Your agent crashing when cloud APIs go down |
| **HITL Approval** | Your agent doing something destructive while you sleep |
| **Audit Logging** | Having no record of what your agent did |
| **SQLite Memory** | Your agent forgetting everything it learned |

## What You Need Before Starting

| Requirement | Why | Cost |
|-------------|-----|------|
| **VS Code** | A proper code editor that catches syntax errors before you run them | **Free** |
| **Python 3.9+** | The programming language your agent runs on | **Free** |
| **OpenRouter API Key** | Access to Claude and 200+ models | **Pay-as-you-go (~$5-20/mo)** |
| **OpenAI API Key** (optional) | Access to Codex for coding | **Pay-as-you-go or $20/mo** |
| **Ollama** (optional) | Free local AI for privacy and fallback | **Free** |

## STEP 0: Install VS Code (Your Most Important Tool)

**Stop using TextEdit and nano.** They don't catch errors. VS Code does.

1. Go to https://code.visualstudio.com
2. Click the big blue **"Download"** button
3. Open the downloaded file and drag VS Code to your Applications folder
4. Open VS Code

**Why this matters:** When you open a Python file in VS Code, it will:
- Show syntax errors in **red** before you run anything
- Auto-indent your code so you never get `IndentationError` again
- Highlight matching brackets and quotes
- Let you edit multiple files in tabs

## STEP 1: Get This Project

### Option A: Download the Zip
1. Download `ai-agent-ecosystem-v2.zip`
2. Double-click it to extract
3. Move the folder to your Desktop (or wherever you want it)

### Option B: Open in VS Code
1. Open VS Code
2. Click **File → Open Folder**
3. Select the `ai-agent-ecosystem-v2` folder
4. You should see the file explorer on the left showing all the files

## STEP 2: Set Up Your Environment

**Open VS Code's built-in terminal:**
- Press `` Ctrl + ` `` (that's the backtick key, above Tab)
- A terminal panel opens at the bottom

**Run these commands one at a time** (copy each line, paste into terminal, press Enter):

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

```bash
pip install -r requirements.txt
```

This downloads all the libraries. It takes 2-5 minutes.

## STEP 3: Configure Your API Keys

**Create your `.env` file:**

1. In VS Code, find the file `.env.example` in the left sidebar
2. Right-click it → **"Copy"**
3. Right-click in empty space → **"Paste"**
4. Right-click the new file → **"Rename"** → type `.env` (remove `.example`)

**Get your OpenRouter key:**
1. Go to https://openrouter.ai/keys
2. Sign up (free)
3. Click **"Create Key"**
4. Copy the long string of letters/numbers

**Add it to your `.env` file:**
1. Click `.env` in VS Code's sidebar to open it
2. Find the line: `OPENROUTER_API_KEY=your_openrouter_key_here`
3. Delete `your_openrouter_key_here`
4. Paste your actual key
5. Press **Cmd + S** to save

**Optional: Add OpenAI key for Codex:**
1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Add it to `.env` on the `OPENAI_API_KEY=` line

## STEP 4: Test the Brain Router

In VS Code's terminal (make sure you see `(venv)`):

```bash
python3 tests/test_router.py
```

You should see:
```
🧪 RUNNING BRAIN ROUTER TESTS

✅ Coding task routes to Codex
✅ Debugging routes to Codex
✅ Research routes to Claude
...
🎉 ALL TESTS PASSED!
```

If tests fail, it usually means:
- Your `.env` file is missing or has the wrong key
- Ollama isn't running (that's OK for now)

## STEP 5: Run Your Agent

```bash
python3 main.py
```

Try these tasks and watch which brain gets picked:

| Task | Expected Brain | Why |
|------|---------------|-----|
| `Write a Python script to scrape prices` | **Codex** | It's coding |
| `Research my competitor's strategy` | **Claude** | It's complex analysis |
| `Summarize the README file` | **Ollama** | It's simple (if Ollama is running) |
| `Check my bank account balance` | **Ollama** | It's sensitive/private |

## STEP 6: Install Ollama (Free Local Brain)

**Why:** When Claude/Codex are down, over budget, or you want privacy, Ollama handles it for **$0**.

```bash
brew install ollama
```

```bash
ollama pull codestral
```

```bash
ollama serve
```

Leave `ollama serve` running in a separate terminal window.

**Test it:**
```bash
python3 -c "from brain_router import BrainRouter; r = BrainRouter(); print(r.route('Summarize this'))"
```

You should see `brain: ollama`.

## Understanding the File Structure

```
ai-agent-ecosystem-v2/
├── main.py                 # Your mission control dashboard
├── config.py               # All settings (budgets, keys, risk tiers)
├── brain_router.py         # The air traffic controller (picks the brain)
├── agents/
│   └── supervisor.py       # The boss agent (plans, approves, learns)
├── memory/
│   └── store.py            # SQLite database (episodes, skills, audit log)
├── tools/
│   └── toolkit.py          # What your agent can do (search, read, write)
├── tests/
│   └── test_router.py      # Verify everything works
├── sandbox/
│   └── Dockerfile          # Safe prison for running agent code
└── .env                    # Your secret keys (never share this)
```

## How the Brain Router Works

When you give your agent a task, the router asks:

1. **Is this sensitive?** (passwords, money, private data) → **Ollama** (local, free, private)
2. **Is this coding?** (scripts, APIs, debugging) → **Codex** (best coder)
3. **Is this complex strategy?** (research, analysis, planning) → **Claude** (smartest thinker)
4. **Is this simple?** (summarize, format, list) → **Ollama** (fast, free)
5. **Everything else** → **Claude** (reliable default)

**If a brain is over budget or broken:** Automatic fallback to the next best option.

## Your Roadmap (The 10 Layers)

### ✅ DONE (This Starter Kit)
- [x] Brain Router (picks the right AI for each task)
- [x] Dynamic LLM Switching (actually uses the brain the router picked)
- [x] Error Handling & Retries (survives API failures)
- [x] Rate Limiting (won't get you banned)
- [x] Cost Tracking (knows how much you spent)
- [x] Budget Kill Switch (stops spending if you hit $20/day)
- [x] HITL Approval (you approve important actions)
- [x] Audit Logging (records every decision)
- [x] Episodic Memory (remembers past tasks)
- [x] SQLite Storage (persistent, local database)

### 🔜 NEXT (Build These Next)
- [ ] **Ollama Setup** (free local fallback — do this today)
- [ ] **Telegram Notifications** (approve actions from your phone)
- [ ] **Docker Sandbox** (safe place for agent-written code)
- [ ] **VPS Deployment** (24/7 server that never sleeps)
- [ ] **Morning Digest** (wake up to a summary of what happened)
- [ ] **Health Monitor** (alerts if agent gets stuck or crashes)
- [ ] **Auto-Restart** (agent restarts itself if it dies)
- [ ] **Skill Extraction** (agent auto-creates reusable skills)
- [ ] **Multi-Agent Fleet** (specialist agents working together)
- [ ] **Revenue Tracking** (connect to your actual income sources)

## Troubleshooting

**"No module named langgraph"**
→ You forgot to activate the virtual environment. Type: `source venv/bin/activate`

**"API key error"**
→ Your `.env` file is wrong. Open it in VS Code and check the key is pasted correctly (no extra spaces).

**"IndentationError"**
→ You edited a file outside VS Code or mixed tabs and spaces. Open the file in VS Code, select all (Cmd+A), and run **Format Document** (Shift+Option+F on Mac).

**"Connection refused"**
→ The router tried to use Ollama but it's not running. Start it: `ollama serve`

**"Insufficient credits"**
→ Add money to your OpenRouter account at https://openrouter.ai/settings/credits (start with $5).

**Agent picks the wrong brain**
→ The router uses keyword matching. Try rephrasing your task with clearer words ("write code" instead of "create").

## Safety Rules (Read This)

1. **Never let an agent move money without your approval.** Keep `send_money` in RED_ACTIONS.
2. **Always review code before running it.** The agent writes in a sandbox, but you approve execution.
3. **Set your daily budget low at first.** Start with $5/day. Increase only when you're making money.
4. **Check your audit log weekly.** `memory/agent_memory.db` — make sure nothing weird happened.
5. **Back up your memory database.** It's your agent's brain. If it corrupts, you start from zero.

## Cost Reality

| Scenario | Monthly Cost |
|----------|-------------|
| Light testing (10 tasks/day) | ~$5-10 |
| Active building (50 tasks/day) | ~$15-30 |
| 24/7 passive operation | ~$45-100 |
| With Ollama fallback (recommended) | ~$20-50 |

**The goal:** Your agents should earn more than they cost. If they don't, adjust your tasks or add more Ollama fallback.

---

**Built for builders who want control.** Your agents, your rules, your infrastructure, your money.
