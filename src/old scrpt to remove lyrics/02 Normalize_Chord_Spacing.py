import os
import re

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
            output_path = os.path.join(output_folder, f"normalizado_{filename}")

            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Normalizar los espacios entre acordes
            normalized_content = normalize_chord_spacing(content)

            # Escribir el contenido normalizado en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(normalized_content)

            print(f"Procesado: {filename}")

# Carpetas de entrada y salida
input_folder = 'canciones-solo-acordes'
output_folder = 'canciones-normalizadas'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
import os
import re

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
            output_path = os.path.join(output_folder, f"normalizado_{filename}")

            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Normalizar los espacios entre acordes
            normalized_content = normalize_chord_spacing(content)

            # Escribir el contenido normalizado en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(normalized_content)

            print(f"Procesado: {filename}")

# Carpetas de entrada y salida
input_folder = 'canciones-solo-acordes'
output_folder = 'canciones-normalizadas'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)

