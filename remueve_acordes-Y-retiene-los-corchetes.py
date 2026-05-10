import os
import re

# ============================================================
# RECONOCIMIENTO DE ACORDES
# ============================================================
# Patrón de acordes para detectar líneas de acordes (usando la lógica de chord_autoscroll.py)
CHORD_PATTERN = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)'

# Líneas como [Intro], [Coro x2], [Puente 3]
SECTION_LINE = re.compile(r'^\s*\[[^\]]+\]\s*$')

# Líneas como: Intro, Verso 2, Coro x3, Puente, Solo, Final...
PLAIN_TITLE_LINE = re.compile(
    r'^\s*(Intro|Verso|Coro|Puente|Solo|Pre[- ]?Coro|Final|Outro|Interludio|Instrumental)(\s+\d+|\s+x\d+)?\s*$',
    re.IGNORECASE
)

def is_chord_line(line):
    """
    Determina si una línea es una línea de acordes.
    Usa la lógica de chord_autoscroll.py: considera la línea como acorde si más del 50% de las palabras coinciden con el patrón de acordes.
    """
    words = line.split()
    if not words:
        return False
    matches = [bool(re.fullmatch(CHORD_PATTERN, word)) for word in words]
    # Considera la línea como acorde si más del 50% de las palabras coinciden con el patrón de acordes
    return sum(matches) > len(words) / 2

def remove_chords(content):
    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Mantener líneas vacías
        if not stripped:
            cleaned_lines.append("")
            continue

        # Mantener encabezados entre corchetes
        if SECTION_LINE.match(line):
            cleaned_lines.append(stripped)
            continue

        # Mantener encabezados simples
        if PLAIN_TITLE_LINE.match(line):
            cleaned_lines.append(stripped)
            continue

        # Si es una línea de acordes, omitirla
        if is_chord_line(stripped):
            continue

        # Mantener la línea tal como está
        cleaned_lines.append(stripped)

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

# Carpetas
input_folder = 'canciones-a-remover-acordes'
output_folder = 'canciones-solo-letras-con-corchetes'

# Ejecutar
process_files(input_folder, output_folder)
