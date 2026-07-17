import os
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Constants
# Support both 'wordlists' and 'wordslists' directories to be robust
WORDLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordlists')
if not os.path.exists(WORDLISTS_DIR):
    WORDLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordslists')

MAX_INPUT_LENGTH = 10000  # Prevent denial of service or overflow in rendering/handling

# Load wordlists
# Map: language_key -> list of words (index 0 corresponds to BIP39 index 1)
WORDLISTS = {}
LANGUAGES = []

def load_wordlists():
    if not os.path.exists(WORDLISTS_DIR):
        print(f"Error: wordlists directory not found at {WORDLISTS_DIR}")
        return

    # Check if there are TXT files
    for filename in sorted(os.listdir(WORDLISTS_DIR)):
        if filename.endswith('.txt'):
            lang_key = filename[:-4]  # remove '.txt'
            lang_name = lang_key.replace('_', ' ').title()
            filepath = os.path.join(WORDLISTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip()]
                if len(words) == 2048:
                    WORDLISTS[lang_key] = words
                    LANGUAGES.append({'key': lang_key, 'name': lang_name})
                    print(f"Loaded wordlist: {lang_name} ({len(words)} words)")
                else:
                    print(f"Warning: {filename} does not contain exactly 2048 words (found {len(words)})")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

load_wordlists()

def safe_to_bytearray(input_str: str) -> bytearray:
    """
    Safely converts a string to a bytearray.
    Enforces a strict length limit and strips null bytes to prevent potential
    core dumps or buffer overflows in any lower-level C libraries.
    """
    if not isinstance(input_str, str):
        return bytearray()

    # 1. Enforce strict length limit
    sanitized = input_str[:MAX_INPUT_LENGTH]

    # 2. Strip null bytes to prevent null-byte injection/C-level string termination issues
    sanitized = sanitized.replace('\x00', '')

    # 3. Convert to bytearray using UTF-8 encoding
    try:
        return bytearray(sanitized.encode('utf-8', errors='replace'))
    except Exception:
        return bytearray()

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_language = request.form.get('language', 'english')
    words_input = request.form.get('words', '')

    # Prevent extremely long inputs or invalid formats
    if len(words_input) > MAX_INPUT_LENGTH:
        words_input = words_input[:MAX_INPUT_LENGTH]

    # Clean input: replace null bytes
    words_input_clean = words_input.replace('\x00', '')

    # Split the input into words
    # Separators: spaces, commas, semicolons, tabs, newlines
    raw_words = [w for w in re.split(r'[\s,;]+', words_input_clean) if w]

    # Keep track of errors and warning messages
    error_msg = None
    results = []
    word_indices_list = []
    unmatched_words = []

    # Safe bytearray conversions
    # 1. Bytearray of the exact introduced words (space separated)
    cleaned_phrase = " ".join(raw_words)
    raw_words_bytearray = safe_to_bytearray(cleaned_phrase)
    raw_words_bytearray_hex = raw_words_bytearray.hex()
    raw_words_bytearray_list = list(raw_words_bytearray)

    wordlist = WORDLISTS.get(selected_language, [])

    # Handle the matching and validation if input is provided
    if request.method == 'POST':
        word_count = len(raw_words)

        if word_count == 0:
            error_msg = "Please enter some words."
        elif not (12 <= word_count <= 24):
            error_msg = f"You introduced {word_count} words. Please enter from 12 to 24 words (inclusive)."
        elif not wordlist:
            error_msg = f"Wordlist for language '{selected_language}' is not available."
        else:
            # Match each word with the selected wordlist
            for i, word in enumerate(raw_words, 1):
                # Normalize word for comparison
                normalized_word = word.lower().strip()

                match_index = None
                binary_str = None
                dot_map = None
                match_found = False

                # Check match in wordlist
                if normalized_word in wordlist:
                    # BIP39 indexes are 1-based (1 to 2048)
                    match_index = wordlist.index(normalized_word) + 1
                    match_found = True
                    # Convert to 12-digit binary
                    binary_str = bin(match_index)[2:].zfill(12)
                    # Convert binary string to dots: ○ for 0, ● for 1
                    dot_map = "".join('●' if char == '1' else '○' for char in binary_str)
                    word_indices_list.append(match_index)
                else:
                    unmatched_words.append(word)
                    word_indices_list.append(None)

                results.append({
                    'num': i,
                    'original': word,
                    'normalized': normalized_word,
                    'match_found': match_found,
                    'index': match_index if match_found else "NOT MATCHED / INVALID",
                    'binary': binary_str if match_found else "",
                    'dot_map': dot_map if match_found else ""
                })

            if unmatched_words:
                error_msg = f"Warning: The following word(s) did not match the '{selected_language.replace('_', ' ').title()}' wordlist: {', '.join(unmatched_words)}."

    # 2. Bytearray of the indices of the matched words (2 bytes per index, big-endian)
    indices_bytearray = bytearray()
    for idx in word_indices_list:
        if idx is not None:
            indices_bytearray.extend(idx.to_bytes(2, byteorder='big'))
    indices_bytearray_hex = indices_bytearray.hex()
    indices_bytearray_list = list(indices_bytearray)

    return render_template(
        'index.html',
        languages=LANGUAGES,
        selected_language=selected_language,
        words_input=words_input,
        results=results,
        error_msg=error_msg,
        word_count=len(raw_words),
        raw_words_bytearray_hex=raw_words_bytearray_hex,
        raw_words_bytearray_list=raw_words_bytearray_list,
        indices_bytearray_hex=indices_bytearray_hex,
        indices_bytearray_list=indices_bytearray_list,
        word_indices_list=[(idx if idx is not None else "??") for idx in word_indices_list]
    )

if __name__ == '__main__':
    # Default to port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
