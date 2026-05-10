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

def remove_chords(content):
    # Dividir el contenido en líneas
    lines = content.split('\n')

    # Lista para almacenar las líneas sin acordes
    cleaned_lines = []

    for line in lines:
        # Si la línea está vacía, la mantenemos para preservar los espacios entre párrafos
        if not line.strip():
            cleaned_lines.append(line)
            continue

        # Si la línea es una línea de acordes, la omitimos
        if is_chord_line(line.strip()):
            continue

        # Mantener la línea tal como está
        cleaned_lines.append(line.strip())

    # Unir las líneas limpias en un solo string
    return '\n'.join(cleaned_lines)

def process_files(input_folder, output_folder):
    # Asegurarse de que la carpeta de salida existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Procesar cada archivo en la carpeta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"sin_acordes {filename}")

            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Eliminar los acordes
            cleaned_content = remove_chords(content)

            # Escribir el contenido limpio en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)

            print(f"Procesado: {filename}")

# Carpetas de entrada y salida
input_folder = 'canciones-a-remover-acordes'
output_folder = 'canciones-solo-letras'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
