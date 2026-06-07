import os
import re
import codecs

try:
    import chardet
except ImportError:
    chardet = None

MIN_CHARDET_CONFIDENCE = 0.20

BOM_ENCODINGS = (
    (codecs.BOM_UTF8, 'utf-8-sig'),
    (codecs.BOM_UTF32_LE, 'utf-32'),
    (codecs.BOM_UTF32_BE, 'utf-32'),
    (codecs.BOM_UTF16_LE, 'utf-16'),
    (codecs.BOM_UTF16_BE, 'utf-16'),
)

FALLBACK_ENCODINGS = (
    'utf-8-sig',
    'utf-8',
    'cp1252',
    'iso-8859-1',
)

def normalize_encoding_name(encoding):
    if not encoding:
        return None

    normalized = encoding.replace('_', '-').lower()
    if normalized == 'ascii':
        return 'utf-8'
    if normalized in ('iso-8859-1', 'latin-1', 'windows-1252'):
        return 'cp1252'

    return encoding

def add_encoding(candidate_encodings, encoding):
    encoding = normalize_encoding_name(encoding)
    if not encoding:
        return

    normalized = encoding.replace('_', '-').lower()
    existing = [item.replace('_', '-').lower() for item in candidate_encodings]
    if normalized not in existing:
        candidate_encodings.append(encoding)

def guess_utf16_encodings(raw_data):
    sample = raw_data[:2000]
    if len(sample) < 4:
        return []

    even_bytes = sample[0::2]
    odd_bytes = sample[1::2]
    even_null_ratio = even_bytes.count(0) / len(even_bytes)
    odd_null_ratio = odd_bytes.count(0) / len(odd_bytes)

    if odd_null_ratio > 0.25 and even_null_ratio < 0.05:
        return ['utf-16-le']
    if even_null_ratio > 0.25 and odd_null_ratio < 0.05:
        return ['utf-16-be']

    return []

def detect_text_encoding(raw_data):
    if not raw_data:
        return 'utf-8'

    for signature, encoding in BOM_ENCODINGS:
        if raw_data.startswith(signature):
            return encoding

    candidate_encodings = []
    add_encoding(candidate_encodings, 'utf-8-sig')
    add_encoding(candidate_encodings, 'utf-8')
    for encoding in guess_utf16_encodings(raw_data):
        add_encoding(candidate_encodings, encoding)

    if chardet is not None:
        detected = chardet.detect(raw_data)
        if detected.get('confidence', 0) >= MIN_CHARDET_CONFIDENCE:
            add_encoding(candidate_encodings, detected.get('encoding'))

    for encoding in FALLBACK_ENCODINGS:
        add_encoding(candidate_encodings, encoding)

    for encoding in candidate_encodings:
        try:
            raw_data.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue

    return 'iso-8859-1'

def read_text_file(path):
    with open(path, 'rb') as file:
        raw_data = file.read()

    encoding = detect_text_encoding(raw_data)
    return raw_data.decode(encoding), encoding

def extract_chords(content):
    # Patrón para identificar acordes (incluyendo notaciones complejas)
    chord_pattern = r'[A-G](#|b|m|dim|aug|maj|min|sus|add|m)?[0-9]?(/[A-G](#|b)?)?(?=\s|$)'

    # Dividir el contenido en líneas
    lines = content.splitlines()

    # Lista para almacenar las líneas procesadas
    result_lines = []

    for line in lines:
        # Si la línea está vacía, la conservamos (preserva saltos de línea entre secciones)
        if not line.strip():
            result_lines.append("")
            continue

        # Si la línea contiene un encabezado de sección entre corchetes, la conservamos intacta
        if re.match(r'^\s*\[.*?\]\s*$', line):
            result_lines.append(line)
            continue

        # Contar los caracteres que coinciden con el patrón de acordes
        matches = re.findall(chord_pattern, line)
        total_chord_chars = sum(len(match) for match in matches)

        # Si más del 50% de la línea corresponde a acordes, conservarla
        if total_chord_chars >= 0.5 * len(line.replace(' ', '')):
            result_lines.append(line)

    # Unir las líneas procesadas en un solo string
    return '\n'.join(result_lines)

def normalize_chord_spacing(content):
    # Dividir el contenido en líneas
    lines = content.splitlines()

    # Lista para almacenar las líneas normalizadas
    normalized_lines = []

    for line in lines:
        # Si la línea es un encabezado de sección entre corchetes, la dejamos intacta
        if re.match(r'^\s*\[.*?\]\s*$', line):
            normalized_lines.append(line)
            continue

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
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"solo_acordes_normalizados_{filename}")

            # Leer el contenido del archivo
            content, encoding = read_text_file(input_path)

            # Extraer solo los acordes
            chord_content = extract_chords(content)

            # Normalizar los espacios entre acordes
            normalized_content = normalize_chord_spacing(chord_content)

            # Escribir el contenido con solo acordes normalizados en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(normalized_content)

            print(f"Procesado: {filename} ({encoding})")

# Carpetas de entrada y salida
input_folder = 'canciones-a-remover-letras'
output_folder = 'canciones-solo-acordes'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
