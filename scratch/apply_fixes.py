# 1. Update CaseBuilder FAMILY_KEYWORDS to include Marathi 'घटस्फोट' and 'पोटगी'
with open('app/core/case_builder.py', 'r', encoding='utf-8') as f:
    cb_code = f.read()

old_fam = r'(છૂટાછેડા|પેટાભથ્થું|ઘરેલું\s*હિંસા|તલાક|तलाक|गुज़ारा\s*भत्ता|घरेलू\s*हिंसा|कस्टडी|വിവാഹമോചനം|ഡൊമസ്റ്റിക്\s*വയലൻസ്|விவாகரத்து|ஜீவனாம்சம்|విడాకులు|భరణం|বিবাহবিচ্ছেদ|খোরপোশ)'
new_fam = r'(છૂટાછેડા|પેટાભથ્થું|ઘરેલું\s*હિંસા|તલાક|तलाक|गुज़ारा\s*भत्ता|घरेलू\s*हिंसा|कस्टडी|घटस्फोट|पोटगी|विवाह|വിവാഹമോചനം|ഡൊമസ്റ്റിക്\s*വയലൻസ്|விவாகரத்து|ஜீவனாம்சம்|విడాకులు|భరణం|বিবাহবিচ্ছেদ|খোরপোশ)'

cb_code = cb_code.replace(old_fam, new_fam)

with open('app/core/case_builder.py', 'w', encoding='utf-8') as f:
    f.write(cb_code)
print("Updated case_builder.py")

# 2. Update KnowledgeBase HMA keywords to include vernacular terms
with open('app/core/knowledge_base.py', 'r', encoding='utf-8') as f:
    kb_code = f.read()

old_hma = '"keywords": ["divorce", "mutual consent divorce", "13b hma", "cruelty", "desertion", "alimony", "interim maintenance", "section 24"],'
new_hma = '"keywords": ["divorce", "mutual consent divorce", "13b hma", "cruelty", "desertion", "alimony", "interim maintenance", "section 24", "घटस्फोट", "तलाक", "છૂટાછેડા", "विवाह", "വിവാഹമോചനം", "விவாகரத்து"],'

kb_code = kb_code.replace(old_hma, new_hma)

with open('app/core/knowledge_base.py', 'w', encoding='utf-8') as f:
    f.write(kb_code)
print("Updated knowledge_base.py")

# 3. Update llm_provider.py: ensure _check_fast_track is bypassed if is_mixed is True and restrict joke/math to <= 8 words
with open('app/core/llm_provider.py', 'r', encoding='utf-8') as f:
    llm_code = f.read()

# Make sure fast-track only intercepts pure short non-legal jokes/math, not mixed legal queries
old_ft_joke = 'if any(p in lower_msg for p in ["what is 2 + 2", "what is 2+2", "2 + 2", "2+2", "tell me a joke"]):'
new_ft_joke = 'if len(lower_msg.split()) <= 6 and any(p in lower_msg for p in ["what is 2 + 2", "what is 2+2", "2 + 2", "2+2", "tell me a joke"]):'

llm_code = llm_code.replace(old_ft_joke, new_ft_joke)

# Also check line 1684 and 1832 for fast_reply
old_call1 = 'fast_reply = self._check_fast_track(lower_msg, lang_str)'
new_call1 = 'fast_reply = self._check_fast_track(lower_msg, lang_str) if not is_mixed else None'

llm_code = llm_code.replace(old_call1, new_call1)

with open('app/core/llm_provider.py', 'w', encoding='utf-8') as f:
    f.write(llm_code)
print("Updated llm_provider.py")
