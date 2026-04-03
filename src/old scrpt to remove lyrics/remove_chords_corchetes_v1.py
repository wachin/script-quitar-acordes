import os
import re

CHORD_TOKEN = re.compile(
    r"""
    ^[A-G]                    # nota base
    (?:\#|b)?                # alteración opcional
    (?:
        m|maj|min|dim|aug|sus|add
    )?
    (?:\d+)?                 # número opcional: 7, 9, 11, etc.
    (?:/[A-G](?:\#|b)?)?     # bajo opcional: D/F#, C/E
    $
    """,
    re.VERBOSE
)

SECTION_LINE = re.compile(r'^\s*\[[^\]]+\]\s*$')

PLAIN_TITLE_LINE = re.compile(
    r'^\s*(Intro|Verso|Coro|Puente|Solo|Pre[- ]?Coro|Final|Outro)(\s+\d+|\s+x\d+)?\s*$',
    re.IGNORECASE
)

def is_chord_token(token):
    return bool(CHORD_TOKEN.match(token))

def is_chord_only_line(line):
    stripped = line.strip()
    if not stripped:
        return False

    tokens = stripped.split()
    return all(is_chord_token(token) for token in tokens)

def remove_inline_chords(line):
    tokens = re.split(r'(\s+)', line)
    cleaned = []

    for token in tokens:
        if token.isspace():
            cleaned.append(token)
            continue

        if is_chord_token(token):
            continue

        cleaned.append(token)

    result = ''.join(cleaned).strip()
    result = re.sub(r'[ \t]+', ' ', result)
    return result

def remove_chords(content):
    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        if SECTION_LINE.match(line):
            cleaned_lines.append(stripped)
            continue

        if PLAIN_TITLE_LINE.match(line):
            cleaned_lines.append(stripped)
            continue

        if is_chord_only_line(line):
            continue

        cleaned_line = remove_inline_chords(line)

        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)

def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"sin_acordes {filename}")

            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            cleaned_content = remove_chords(content)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)

            print(f"Procesado: {filename}")

input_folder = 'canciones-a-quitar-acordes'
output_folder = 'canciones-quitados-acordes'

process_files(input_folder, output_folder)