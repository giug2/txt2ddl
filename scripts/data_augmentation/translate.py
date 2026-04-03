import os
import json
import re
from deep_translator import GoogleTranslator
from tqdm import tqdm


# --- CONFIGURAZIONE ---
SOURCE_DIR = 'dataset'
TARGET_DIR = 'dataset_en'
LANG_TARGET = 'en'

translator = GoogleTranslator(source='auto', target=LANG_TARGET)


def translate_text(text):
    if not text or len(text.strip()) == 0: return text
    try:
        # Google Translate ha un limite di caratteri per chiamata
        if len(text) > 4500:
            return text # Per sicurezza su file enormi
        return translator.translate(text)
    except Exception as e:
        print(f"Errore traduzione: {e}")
        return text


def translate_json(data):
    """Traduce ricorsivamente i valori di un JSON senza toccare le chiavi"""
    if isinstance(data, dict):
        return {k: translate_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_json(i) for i in data]
    elif isinstance(data, str):
        if len(data) > 1 and not data.isnumeric():
            return translate_text(data)
    return data


def process_dataset():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    # Conta i file per la barra di progresso
    files_to_process = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    print(f"Inizio traduzione di {len(files_to_process)} file...")

    for file_path in tqdm(files_to_process):
        # Crea sottocartelle
        rel_path = os.path.relpath(file_path, SOURCE_DIR)
        dest_path = os.path.join(TARGET_DIR, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                translated_data = translate_json(data)
                with open(dest_path, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, indent=4, ensure_ascii=False)

            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                translated_content = translate_text(content)
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)

            else:
                # Copia file non supportati così come sono
                import shutil
                shutil.copy2(file_path, dest_path)

        except Exception as e:
            print(f"Errore su {file_path}: {e}")


if __name__ == "__main__":
    process_dataset()
    print(f"\nTraduzione completata! Trovi tutto in: {TARGET_DIR}")
    