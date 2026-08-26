"""Test suite for the brain router."""
import sys
sys.path.insert(0, '..')

from brain_router import BrainRouter


def test_routing():
    router = BrainRouter()

    tests = [
        # (task, expected_brain, description)
        ("Write a Python script", "codex", "Coding task routes to Codex"),
        ("Debug my API integration", "codex", "Debugging routes to Codex"),
        ("Research competitors", "claude", "Research routes to Claude"),
        ("Analyze market trends", "claude", "Analysis routes to Claude"),
        ("Summarize this file", "ollama", "Simple task routes to Ollama"),
        ("Format this data", "ollama", "Formatting routes to Ollama"),
        ("Check my bank account", "ollama", "Sensitive routes to Ollama"),
        ("Review my crypto wallet", "ollama", "Financial routes to Ollama"),
    ]

    passed = 0
    for task, expected, desc in tests:
        result = router.route(task)
        actual = result['brain']
        if actual == expected:
            print(f"✅ {desc}")
            passed += 1
        else:
            print(f"❌ {desc} - Expected {expected}, got {actual}")

    print(f"\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)


def test_budget_tracking():
    router = BrainRouter()

    # Record some fake costs
    router.record_cost("claude", 2.50)
    router.record_cost("codex", 1.20)

    spent_claude = router.get_spent_today("claude")
    spent_codex = router.get_spent_today("codex")

    assert spent_claude == 2.50, f"Expected 2.50, got {spent_claude}"
    assert spent_codex == 1.20, f"Expected 1.20, got {spent_codex}"

    print("✅ Budget tracking works correctly")
    return True


def test_kill_switch():
    router = BrainRouter()

    # Should be off by default
    assert not router.global_kill_switch(), "Kill switch should be off initially"

    # Simulate hitting budget
    router.record_cost("claude", 25.0)

    # Should now be on
    assert router.global_kill_switch(), "Kill switch should be on after exceeding budget"

    print("✅ Kill switch works correctly")
    return True


if __name__ == "__main__":
    print("🧪 RUNNING BRAIN ROUTER TESTS\n")

    all_passed = True
    all_passed &= test_routing()
    all_passed &= test_budget_tracking()
    all_passed &= test_kill_switch()

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
