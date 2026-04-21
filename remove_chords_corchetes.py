import os
import re

# ============================================================
# RECONOCIMIENTO DE ACORDES AVANZADOS
# ============================================================
#
# Ejemplos admitidos:
# C, Dm, F#, Bb, Cmaj7, F#m7, G7, Dsus4, Asus2, Cadd9,
# E/G#, D/F#, Bbmaj7, Gm11, C7#9, F#7b9, Eaug, Bdim, A6,
# Em(add9), Dmaj9/F#
#
CHORD_REGEX = r"""
^
[A-G]                    # Nota base
(?:\#|b)?                # Alteración opcional: # o b

(?:                      # Calidad/tipo opcional
    maj|min|dim|aug|sus|add|m
)?

(?:                      # Extensión numérica opcional
    2|4|5|6|7|9|11|13
)?

(?:                      # Alteraciones/extensiones extra opcionales
    (?:\#|b)?(?:5|9|11|13)
)*

(?:\([^)]+\))?           # Cosas como (add9), (no3), etc.

(?:/[A-G](?:\#|b)?)?     # Bajo opcional: /F#, /Bb
$
"""

CHORD_TOKEN = re.compile(CHORD_REGEX, re.VERBOSE | re.IGNORECASE)

# Líneas como [Intro], [Coro x2], [Puente 3]
SECTION_LINE = re.compile(r'^\s*\[[^\]]+\]\s*$')

# Líneas como: Intro, Verso 2, Coro x3, Puente, Solo, Final...
PLAIN_TITLE_LINE = re.compile(
    r'^\s*(Intro|Verso|Coro|Puente|Solo|Pre[- ]?Coro|Final|Outro|Interludio|Instrumental)(\s+\d+|\s+x\d+)?\s*$',
    re.IGNORECASE
)

def normalize_token(token):
    """
    Limpia puntuación al inicio/final que a veces aparece pegada.
    """
    return token.strip().strip('.,;:¡!¿?"\'`´')

def is_chord_token(token):
    token = normalize_token(token)
    if not token:
        return False
    return bool(CHORD_TOKEN.match(token))

def is_chord_only_line(line):
    """
    Devuelve True si la línea contiene únicamente acordes.
    Ejemplos:
        D A F#m E
        D/F#   G   A   Bm7
        Cmaj7  G/B  Am7  F
    """
    stripped = line.strip()
    if not stripped:
        return False

    tokens = stripped.split()
    if not tokens:
        return False

    return all(is_chord_token(token) for token in tokens)

def remove_inline_chords(line):
    """
    Elimina acordes dentro de una línea.
    Conserva el texto normal.
    """
    tokens = re.split(r'(\s+)', line)  # conserva espacios
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

        # Si es una línea solo de acordes, omitirla
        if is_chord_only_line(line):
            continue

        # Quitar acordes incrustados
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

# Carpetas
input_folder = 'canciones-a-remover-acordes'
output_folder = 'canciones-quitados-acordes'

# Ejecutar
process_files(input_folder, output_folder)
