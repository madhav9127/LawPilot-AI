with open('app/core/intent_classifier.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace bare 'act' in LEGAL_KEYWORDS_BROAD
old_sec = r'r"\b(?:fir|police|complaint|arrest|bail|anticipatory|warrant|summons|charge\s*sheet|magistrate|court|judge|advocate|lawyer|bns|bnss|bsa|ipc|crpc|evidence|section|act|statute|offence|crime|cheating|fraud|theft|assault|extortion|defamation|contempt|habeas\s*corpus|mandamus|writ|appeal|revision|tribunal|quash)\b"'
new_sec = r'r"\b(?:fir|police|complaint|arrest|bail|anticipatory|warrant|summons|charge\s*sheet|magistrate|court|judge|advocate|lawyer|bns|bnss|bsa|ipc|crpc|evidence|statute|statutory|offence|crime|cheating|fraud|theft|assault|extortion|defamation|contempt|habeas\s*corpus|mandamus|writ|appeal|revision|tribunal|quash)\b"'
content = content.replace(old_sec, new_sec)

# Also check for specific Acts
old_kw = r'r"\b(?:trademark|copyright|patent|infringement|piracy|intellectual\s*property|rti|right\s*to\s*information|pio|first\s*appeal|mact|motor\s*accident|accident\s*claim|pollution|ngt|citizenship|passport\s*impounded)\b",'
new_kw = (
    r'r"\b(?:trademark|copyright|patent|infringement|piracy|intellectual\s*property|rti|right\s*to\s*information|pio|first\s*appeal|mact|motor\s*accident|accident\s*claim|pollution|ngt|citizenship|passport\s*impounded)\b",' + "\n" +
    r'        r"\b(?:section\s+\d+|order\s+\d+|article\s+\d+|rule\s+\d+|act\s+of\s+\d{4}|tenancy\s+act|consumer\s+protection\s+act|penal\s+code|civil\s+procedure|criminal\s+procedure)\b",'
)
content = content.replace(old_kw, new_kw)

# Replace indic joke pattern to include જોક / જોક્સ
old_joke = r'r"(?:चुटकुला\s*सुनाओ|जोक\s*कहो|विनोद\s*सांगा|തമാശ\s*പറയൂ|நகைச்சுவை\s*சொல்லுங்கள்|ఒక\s*జోక్\s*చెప్పండి|কৌতুক\s*বলুন)"'
new_joke = r'r"(?:चुटकुला|जोक|विनोद|જોક|જોક્સ|ચુટકલો|തമാശ|நகைச்சுவை|జోక్|কৌতুক)"'
content = content.replace(old_joke, new_joke)

with open('app/core/intent_classifier.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated intent_classifier.py successfully')
