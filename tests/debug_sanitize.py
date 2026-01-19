import re

def sanitize(text):
    print(f"Original: {text}")
    # 1. Normalize unicode punctuation and force pauses for rhythm
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    
    # Contemplation marker "--" at the end of thoughts
    text = text.replace('--', '... ')
    
    # Force a pause for ellipses by adding a comma (single pass to avoid double-replacement)
    text = re.sub(r'\.{3,}|…', ', ... ', text)
    
    # Ensure dashes have space to prevent word merging and add a slight pause
    text = text.replace('—', ' - ').replace('–', ' - ')
    
    # 2. Strip (parentheticals) - often meta-commentary like (laughing) or multi-line thoughts
    clean = re.sub(r'\(.*?\)', '', text, flags=re.DOTALL)
    clean = re.sub(r'\[.*?\]', '', clean, flags=re.DOTALL) # Also strip [actions]
    
    # 3. Remove literal markdown symbols used for emphasis (* and _)
    clean = clean.replace('*', '').replace('_', '')
    
    # 4. Remove emojis and truly "illegal" symbols (Keep alphanumeric + basic punctuation)
    # Whitelist includes standard punctuation that assists TTS engines
    clean = re.sub(r'[^\w\s,.\'?!:;"-]', '', clean)
    
    # 5. Collapse multiple spaces but stay mindful of the space we just added for pauses
    clean = re.sub(r'\s+', ' ', clean)
    
    result = clean.strip()
    print(f"Sanitized: {result}")
    return result

print("--- TESTING BOLD PRESERVATION ---")
sanitize("This is **bold** text.")
sanitize("This is __bold__ text.")
sanitize("**Start** of sentence.")
sanitize("End of sentence **bold**")
sanitize("**Heh—*German*?** Okay, *now* we’re talking.")
sanitize("**Hmm.** Yeah—*that* duality?")
sanitize("**Heh—*vintage vinyls*?** *Oh wow—*that’s *dangerous*.")
sanitize("(Heh—*I*’d probably try to order a latte in Icelandic. Just to see what happens.)")
