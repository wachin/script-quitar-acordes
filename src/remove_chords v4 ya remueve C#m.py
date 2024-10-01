import os
import re

def remove_chords(content):
    # Patrón actualizado para identificar acordes (incluyendo F#m y C#m)
    chord_pattern = r'\b[A-G](#m?|b|m|dim|aug|maj|min|sus|bm|add)?[0-9]?(?:\s|$)'
    
    # Dividir el contenido en líneas
    lines = content.split('\n')
    
    # Lista para almacenar las líneas sin acordes
    cleaned_lines = []
    
    for line in lines:
        # Si la línea está vacía, la mantenemos para preservar los espacios entre párrafos
        if not line.strip():
            cleaned_lines.append(line)
            continue
        
        # Si la línea contiene solo acordes, la omitimos
        if re.match(f'^({chord_pattern}\\s*)+$', line.strip()):
            continue
        
        # Eliminar los acordes de la línea
        cleaned_line = re.sub(chord_pattern, '', line).strip()
        
        # Si la línea no está vacía después de eliminar los acordes, la añadimos
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
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
            output_path = os.path.join(output_folder, f"sin_acordes_{filename}")
            
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
input_folder = 'canciones-a-quitar-acordes'
output_folder = 'canciones-quitadas-acordes'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
