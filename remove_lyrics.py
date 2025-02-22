import os
import re

def extract_chords(content):
    # Patrón para identificar acordes (incluyendo notaciones complejas)
    chord_pattern = r'[A-G](#|b|m|dim|aug|maj|min|sus|add|m)?[0-9]?(/[A-G](#|b)?)?(?=\s|$)'

    # Dividir el contenido en líneas
    lines = content.split('\n')

    # Lista para almacenar las líneas que contienen mayoritariamente acordes
    chord_lines = []

    for line in lines:
        # Si la línea está vacía, la ignoramos
        if not line.strip():
            continue

        # Contar los caracteres que coinciden con el patrón de acordes
        matches = re.findall(chord_pattern, line)
        total_chord_chars = sum(len(match) for match in matches)  # match contiene el texto del acorde

        # Si más del 50% de la línea corresponde a acordes, conservarla
        if total_chord_chars >= 0.5 * len(line.replace(' ', '')):  # Ignorar espacios para el cálculo
            chord_lines.append(line)

    # Unir las líneas de acordes en un solo string
    return '\n'.join(chord_lines)

def normalize_chord_spacing(content):
    # Dividir el contenido en líneas
    lines = content.split('\n')

    # Lista para almacenar las líneas normalizadas
    normalized_lines = []

    for line in lines:
        # Quitar espacios al inicio y reducir múltiples espacios entre acordes a uno solo
        normalized_line = re.sub(r'\s+', ' ', line.strip())
        normalized_lines.append(normalized_line)

    # Unir las líneas normalizadas en un solo string
    return '\n'.join(normalized_lines)

def process_files(input_folder, output_folder):
    # Asegurarse de que la carpeta de salida existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Procesar cada archivo en la carpeta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"solo_acordes_normalizados_{filename}")

            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extraer solo los acordes
            chord_content = extract_chords(content)

            # Normalizar los espacios entre acordes
            normalized_content = normalize_chord_spacing(chord_content)

            # Escribir el contenido con solo acordes normalizados en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(normalized_content)

            print(f"Procesado: {filename}")

# Carpetas de entrada y salida
input_folder = 'canciones-a-extraer-acordes'
output_folder = 'canciones-solo-acordes'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
