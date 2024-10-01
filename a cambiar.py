 
import os
import re

def remove_chords(content):
    # Patrón actualizado para identificar acordes (incluyendo F#m y C#m)
    chord_pattern = r'\b[A-G](#m?|b|m|dim|aug|maj|min|sus|bm|add)?[0-9]?(?:\s|$)'

    # El resto de la función permanece igual
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue

        if re.match(f'^({chord_pattern}\\s*)+$', line.strip()):
            continue

        cleaned_line = re.sub(chord_pattern, '', line).strip()

        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)

# El resto del código (process_files y la ejecución) permanece igual
