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
    lines = content.splitlines()

    # Lista para almacenar las líneas sin acordes
    cleaned_lines = []

    for line in lines:
        # Si la línea está vacía, la mantenemos para preservar los espacios entre párrafos
        if not line.strip():
            cleaned_lines.append("")
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
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"sin_acordes {filename}")

            # Leer el contenido del archivo
            content, encoding = read_text_file(input_path)

            # Eliminar los acordes
            cleaned_content = remove_chords(content)

            # Escribir el contenido limpio en un nuevo archivo
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)

            print(f"Procesado: {filename} ({encoding})")

# Carpetas de entrada y salida
input_folder = 'canciones-a-remover-acordes'
output_folder = 'canciones-solo-letras'

# Ejecutar el procesamiento
process_files(input_folder, output_folder)
