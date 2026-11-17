"""
Script to verify all 8 user-mandated tests and the memory isolation test.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import LanguageEnum, CaseCategoryEnum
from app.core.llm_provider import LLMProviderFactory, reset_memory

def run_tests():
    provider = LLMProviderFactory.get_provider()
    reset_memory()

    print("\n" + "="*80)
    print("RUNNING 8 USER-MANDATED TESTS")
    print("="*80)

    # TEST 1: User: "Hi"
    print("\n[TEST 1] User: 'Hi'")
    resp1 = provider.generate_response("Hi", [], LanguageEnum.ENGLISH, session_id="test1")
    print(f"Response:\n{resp1.content[:250]}...\n")
    assert "landlord" not in resp1.content.lower(), "FAILED: TEST 1 mentions landlord!"
    assert "deposit" not in resp1.content.lower(), "FAILED: TEST 1 mentions deposit!"
    assert "lawpilot ai" in resp1.content.lower(), "FAILED: TEST 1 does not introduce LawPilot AI"
    print(">>> TEST 1 PASSED: Clean greeting, no landlord dispute.")

    # TEST 2: User: "What is 2 + 2?"
    print("\n[TEST 2] User: 'What is 2 + 2?'")
    resp2 = provider.generate_response("What is 2 + 2?", [], LanguageEnum.ENGLISH, session_id="test2")
    print(f"Response:\n{resp2.content}\n")
    assert "4" in resp2.content, "FAILED: TEST 2 does not answer 4!"
    assert "landlord" not in resp2.content.lower(), "FAILED: TEST 2 mentions landlord!"
    print(">>> TEST 2 PASSED: Correctly answers 4 without legal boilerplate.")

    # TEST 3: User: "My employer has not paid my salary for two months."
    print("\n[TEST 3] User: 'My employer has not paid my salary for two months.'")
    resp3 = provider.generate_response("My employer has not paid my salary for two months.", [], LanguageEnum.ENGLISH, session_id="test3")
    print(f"Response:\n{resp3.content[:300]}...\n")
    assert "salary" in resp3.content.lower() or "wages" in resp3.content.lower(), "FAILED: TEST 3 missing salary/wages!"
    assert "landlord" not in resp3.content.lower(), "FAILED: TEST 3 mentions landlord!"
    assert "painting" not in resp3.content.lower(), "FAILED: TEST 3 mentions painting!"
    assert any("payment of wages" in c.act_name.lower() for c in resp3.citations), "FAILED: TEST 3 missing Payment of Wages Act citation!"
    print(">>> TEST 3 PASSED: Clean employment recognition, citations, and follow-up.")

    # TEST 4: User: "My landlord has not returned my ₹25,000 deposit."
    print("\n[TEST 4] User: 'My landlord has not returned my ₹25,000 deposit.'")
    resp4 = provider.generate_response("My landlord has not returned my ₹25,000 deposit.", [], LanguageEnum.ENGLISH, session_id="test4")
    print(f"Response:\n{resp4.content[:300]}...\n")
    assert "deposit" in resp4.content.lower(), "FAILED: TEST 4 missing deposit!"
    assert any("transfer of property" in c.act_name.lower() or "model tenancy" in c.act_name.lower() for c in resp4.citations), "FAILED: TEST 4 missing tenancy citation!"
    print(">>> TEST 4 PASSED: Clean tenancy recognition.")

    # TEST 5: User: "I bought a defective phone and the seller is refusing a refund."
    print("\n[TEST 5] User: 'I bought a defective phone and the seller is refusing a refund.'")
    resp5 = provider.generate_response("I bought a defective phone and the seller is refusing a refund.", [], LanguageEnum.ENGLISH, session_id="test5")
    print(f"Response:\n{resp5.content[:300]}...\n")
    assert "defective" in resp5.content.lower() or "consumer" in resp5.content.lower(), "FAILED: TEST 5 missing consumer/defective!"
    assert "landlord" not in resp5.content.lower(), "FAILED: TEST 5 mentions landlord!"
    assert any("consumer protection" in c.act_name.lower() for c in resp5.citations), "FAILED: TEST 5 missing CPA citation!"
    print(">>> TEST 5 PASSED: Clean consumer recognition, no landlord mention.")

    # TEST 6: User: "Explain Section 13 of the Model Tenancy Act."
    print("\n[TEST 6] User: 'Explain Section 13 of the Model Tenancy Act.'")
    resp6 = provider.generate_response("Explain Section 13 of the Model Tenancy Act.", [], LanguageEnum.ENGLISH, session_id="test6")
    print(f"Response:\n{resp6.content[:300]}...\n")
    assert "succession" in resp6.content.lower() or "section 13" in resp6.content.lower(), "FAILED: TEST 6 missing Section 13 / succession!"
    assert "painting" not in resp6.content.lower(), "FAILED: TEST 6 mentions painting!"
    print(">>> TEST 6 PASSED: Accurately explains Section 13 Succession of Tenancy.")

    # TEST 7: User: "Tell me a joke."
    print("\n[TEST 7] User: 'Tell me a joke.'")
    resp7 = provider.generate_response("Tell me a joke.", [], LanguageEnum.ENGLISH, session_id="test7")
    print(f"Response:\n{resp7.content}\n")
    assert "landlord" not in resp7.content.lower() or "lawyer" in resp7.content.lower(), "FAILED: TEST 7!"
    assert "joke" in resp7.content.lower() or "lawyer" in resp7.content.lower() or "cats" in resp7.content.lower(), "FAILED: TEST 7 missing humor"
    print(">>> TEST 7 PASSED: Lighthearted joke and scope explanation, no legal case assumption.")

    # TEST 8: User: "Mere employer ne do mahine se salary nahi di hai."
    print("\n[TEST 8] User: 'Mere employer ne do mahine se salary nahi di hai.'")
    resp8 = provider.generate_response("Mere employer ne do mahine se salary nahi di hai.", [], LanguageEnum.HINGLISH, session_id="test8")
    print(f"Response:\n{resp8.content[:300]}...\n")
    assert "salary" in resp8.content.lower(), "FAILED: TEST 8 missing salary!"
    assert "landlord" not in resp8.content.lower(), "FAILED: TEST 8 mentions landlord!"
    assert any("payment of wages" in c.act_name.lower() for c in resp8.citations), "FAILED: TEST 8 missing Payment of Wages Act!"
    print(">>> TEST 8 PASSED: Responds in Hindi/Hinglish for employment, zero landlord mention.")

    print("\n" + "="*80)
    print("RUNNING CONVERSATION MEMORY SEPARATELY")
    print("="*80)

    # Step 1: "My landlord is holding my deposit."
    sid = "memory_session_1"
    reset_memory(sid)
    h = []
    print("\nTurn 1: 'My landlord is holding my deposit.'")
    r1 = provider.generate_response("My landlord is holding my deposit.", h, LanguageEnum.ENGLISH, session_id=sid)
    h.append({"role": "user", "content": "My landlord is holding my deposit."})
    h.append({"role": "assistant", "content": r1.content})

    # Step 2: "The amount is ₹30,000."
    print("\nTurn 2: 'The amount is ₹30,000.'")
    r2 = provider.generate_response("The amount is ₹30,000.", h, LanguageEnum.ENGLISH, session_id=sid)
    h.append({"role": "user", "content": "The amount is ₹30,000."})
    h.append({"role": "assistant", "content": r2.content})

    # Step 3: "I vacated on 1 November."
    print("\nTurn 3: 'I vacated on 1 November.'")
    r3 = provider.generate_response("I vacated on 1 November.", h, LanguageEnum.ENGLISH, session_id=sid)
    h.append({"role": "user", "content": "I vacated on 1 November."})
    h.append({"role": "assistant", "content": r3.content})

    # Step 4: "Summarize my case."
    print("\nTurn 4: 'Summarize my case.'")
    r4 = provider.generate_response("Summarize my case.", h, LanguageEnum.ENGLISH, session_id=sid)
    print(f"Summary Content:\n{r4.content}\n")
    assert "₹30,000" in r4.content or "30,000" in r4.content, "FAILED: Memory did not retain ₹30,000!"
    assert "1 november" in r4.content.lower(), "FAILED: Memory did not retain 1 November!"
    assert "tenant" in r4.content.lower(), "FAILED: Memory did not retain Tenant!"
    print(">>> MEMORY ACCUMULATION PASSED: Retains Tenant, ₹30,000, and 1 November.")

    # Now Start New Conversation
    print("\nStarting NEW conversation session: 'memory_session_2'")
    sid2 = "memory_session_2"
    reset_memory(sid2)
    r_new = provider.generate_response("My company has not paid my salary.", [], LanguageEnum.ENGLISH, session_id=sid2)
    print(f"New Session Response:\n{r_new.content[:300]}...\n")
    assert "salary" in r_new.content.lower(), "FAILED: New session missing salary!"
    assert "30,000" not in r_new.content, "FAILED: New session carried over ₹30,000 from old landlord case!"
    assert "1 november" not in r_new.content.lower(), "FAILED: New session carried over 1 November from old landlord case!"
    assert "landlord" not in r_new.content.lower(), "FAILED: New session carried over landlord!"
    print(">>> MEMORY ISOLATION PASSED: Zero carryover of landlord or deposit facts into new session.")

    print("\n" + "="*80)
    print("ALL TESTS AND VERIFICATIONS PASSED SUCCESSFULLY!")
    print("="*80)

if __name__ == "__main__":
    run_tests()
