import os
import re

# Patrón de acordes más flexible:
# A, Am, A#, Bb, F#m, Cmaj7, Dsus4, G/B, etc.
CHORD_REGEX = re.compile(
    r'\b([A-G](?:#|b)?(?:maj|min|m|dim|aug|sus|add)?\d*(?:/[A-G](?:#|b)?)?)\b'
)

# Una línea se considera "línea de acordes o línea mixta con acordes"
# si comienza (ignorando espacios) con un acorde.
LINE_STARTS_WITH_CHORD = re.compile(
    r'^\s*[A-G](?:#|b)?(?:maj|min|m|dim|aug|sus|add)?\d*(?:/[A-G](?:#|b)?)?(?=\s|$)'
)

# Conserva textos como [Intro], [Verso], [Coro x2], etc.
BRACKET_LINE = re.compile(r'^\s*\[.*\]\s*$')


def extract_chords_from_line(line: str) -> str:
    """Extrae todos los acordes de una línea y los devuelve separados por un espacio."""
    chords = CHORD_REGEX.findall(line)
    return ' '.join(chords)


def process_content(content: str) -> str:
    lines = content.splitlines()
    output_lines = []

    for line in lines:
        stripped = line.strip()

        # 1) Conservar líneas vacías
        if stripped == '':
            output_lines.append('')
            continue

        # 2) Conservar líneas entre corchetes
        if BRACKET_LINE.match(line):
            output_lines.append(stripped)
            continue

        # 3) Si la línea empieza con acorde, extraer solo los acordes
        #    Esto permite convertir:
        #    "A             F#m"
        #    "    Bm A    E"
        #    " F#m      E  A"
        #    etc.
        if LINE_STARTS_WITH_CHORD.match(line):
            chord_line = extract_chords_from_line(line)
            if chord_line:
                output_lines.append(chord_line)
            continue

        # 4) Cualquier otra línea se descarta
        #    (título, autor, letra sin acordes, etc.)

    return '\n'.join(output_lines)


def process_files(input_folder: str, output_folder: str):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"solo_acordes_{filename}")

            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            processed_content = process_content(content)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(processed_content)

            print(f"Procesado: {filename}")


# Carpetas de entrada y salida
input_folder = 'canciones-a-remover-letras'
output_folder = 'canciones-solo-acordes'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
