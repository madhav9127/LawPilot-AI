with open('app/core/llm_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '            "Always state the CURRENT operative BNS/BNSS/BSA provisions as primary. You may mention former IPC/CrPC/IEA sections only as historical equivalents.\\n\\n"\n'
replacement = (
    '            "Always state the CURRENT operative BNS/BNSS/BSA provisions as primary. You may mention former IPC/CrPC/IEA sections only as historical equivalents.\\n\\n"\n'
    '            "CRITICAL SCOPE RESTRICTION:\\n"\n'
    '            "You are LawPilot AI, a specialised assistant for Indian legal matters ONLY. "\n'
    '            "You must NEVER answer unrelated general-purpose questions (such as general trivia, coding/programming, general science, math puzzles, jokes, recipes, weather, workouts, sports, or general homework). "\n'
    '            "If the user asks an unrelated general topic, politely decline, explain that you specialise exclusively in Indian law, and ask if there is an Indian legal issue you can assist with.\\n\\n"\n'
)

if target in content:
    content = content.replace(target, replacement, 1)
    with open('app/core/llm_provider.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully added CRITICAL SCOPE RESTRICTION to llm_provider.py")
else:
    print("Target not found in llm_provider.py")
