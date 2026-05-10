import os
import re

# ============================================================
# RECONOCIMIENTO DE ACORDES
# ============================================================
# Patrón de acordes para detectar líneas de acordes (usando la lógica de chord_autoscroll.py)
CHORD_PATTERN = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)'

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

# Líneas como [Intro], [Coro x2], [Puente 3]
SECTION_LINE = re.compile(r'^\s*\[([^\]]+)\]\s*$')

# Líneas como: Intro, Verso 2, Coro x3, Puente, Solo, Final...
PLAIN_TITLE_LINE = re.compile(
    r'^\s*(Intro|Verso|Coro|Puente|Solo|Pre[- ]?Coro|Final|Outro|Interludio|Instrumental)(\s+\d+|\s+x\d+)?\s*$',
    re.IGNORECASE
)

def remove_chords(content):
    lines = content.splitlines()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()

        # Mantener líneas vacías
        if not stripped:
            cleaned_lines.append("")
            continue

        # Convertir [Sección] -> //Sección para Holyrics
        section_match = SECTION_LINE.match(line)
        if section_match:
            section_name = section_match.group(1).strip()
            cleaned_lines.append(f"//{section_name}")
            continue

        # Mantener encabezados simples
        if PLAIN_TITLE_LINE.match(line):
            cleaned_lines.append(stripped)
            continue

        # Verificar si la línea es una línea de acordes usando la función is_chord_line
        if is_chord_line(stripped):
            # Es una línea de acordes, omitirla
            continue

        # No es una línea de acordes, mantener el contenido
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
output_folder = 'canciones-solo-letras-Holyrics'

# Ejecutar
process_files(input_folder, output_folder)
