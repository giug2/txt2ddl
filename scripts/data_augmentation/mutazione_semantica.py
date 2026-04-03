import os
import glob
import json
import time
from google import genai
from google.api_core import exceptions
from google.genai import types


# Sostituisci con la chiave API di Google
GOOGLE_API_KEY = 'CHIAVE' 

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    print("Errore nell'inizializzazione del client GenAI.")
    print(f"Dettagli: {e}")
    exit()


# Percorsi delle cartelle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARTELLA_JSON_INPUT = os.path.join(BASE_DIR, "json") 
CARTELLA_TESTO_INPUT = os.path.join(BASE_DIR, "txt") 

# Nuove cartelle di output per i file mutati
CARTELLA_JSON_MUTATO = os.path.join(BASE_DIR, "json_semantico") 
CARTELLA_TESTO_MUTATO = os.path.join(BASE_DIR, "testo_semantico")

# Parametri di Mutazione
MODEL_NAME = "gemini-2.5-pro"
NUM_MUTAZIONI_PER_ESEMPIO = 1 
PAUSA_TRA_CHIAMATE_SECONDI = 1.5

# Istruzioni chiare per il modello 
SYSTEM_INSTRUCTION_SEMANTICA = (
    "Sei un AI esperto in modellazione di dati e riscrittura coerente. "
    "Ti verranno forniti uno schema JSON (ERD) e la sua descrizione testuale. "
    "Il tuo compito è applicare una MUTAZIONE SEMANTICA: devi cambiare il DOMINIO di applicazione "
    "dello schema mantenendo intatta la sua STRUTTURA LOGICA (stesse relazioni e cardinalità). "
    "Ad esempio, uno schema 'Biblioteca' deve diventare 'Negozio Online', 'Ospedale' o 'Gestione Eventi'. "
    "Devi restituire SOLO due blocchi di testo separati dal delimitatore <SEPARATOR>: "
    "1. Il JSON MUTATO (con i nomi aggiornati). NON usare ```json```. "
    "2. La NUOVA DESCRIZIONE TESTUALE che riflette lo schema mutato. "
    "Il tuo output deve essere ESATTAMENTE: [JSON MUTATO]<SEPARATOR>[TESTO NARRATIVO MUTATO]."
)


def muta_semantica_con_gemini(json_content: str, text_content: str) -> tuple[str, str]:
    """
    Invia il JSON e il Testo a Gemini per la mutazione semantica e restituisce la coppia mutata.
    """
    prompt = f"""
    Applica una mutazione semantica al seguente schema e alla sua descrizione testuale. 
    Mantieni intatta la struttura e le relazioni, ma cambia i nomi per rappresentare un DOMINIO DIVERSO.

    --- JSON ORIGINALE ---
    {json_content}
    --- TESTO ORIGINALE ---
    {text_content}
    ---
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION_SEMANTICA,
                temperature=0.8, # Temperatura alta per creatività sui nomi
                max_output_tokens=8192
            )
        )
        
        # Suddividi l'output in base al delimitatore <SEPARATOR>
        output_parts = response.text.split("<SEPARATOR>")
        if len(output_parts) != 2:
            raise ValueError("L'output di Gemini non contiene esattamente due parti separate dal delimitatore <SEPARATOR>.")
        
        json_mutato = output_parts[0].strip()
        testo_mutato = output_parts[1].strip()
        
        return json_mutato, testo_mutato
        
    except exceptions.ResourceExhausted:
        raise exceptions.ResourceExhausted("Limite API Quota raggiunto.")
    except Exception as e:
        raise Exception(f"Errore durante la chiamata API: {e}")


def elabora_batch_mutazione_semantica():
    """
    Funzione principale per l'elaborazione delle coppie JSON/Testo in batch.
    """
    print(f"Connesso al modello: **{MODEL_NAME}**")
    print(f"JSON Input: **{CARTELLA_JSON_INPUT}** | Testo Input: **{CARTELLA_TESTO_INPUT}**")
    
    for cartella in [CARTELLA_JSON_MUTATO, CARTELLA_TESTO_MUTATO]:
        if not os.path.exists(cartella):
            os.makedirs(cartella)
            print(f"Creata cartella di output: **{os.path.basename(cartella)}**")

    if not os.path.isdir(CARTELLA_JSON_INPUT) or not os.path.isdir(CARTELLA_TESTO_INPUT):
        print("ERRORE: Una o entrambe le cartelle di input non esistono.")
        return

    # Ricerca e corrispondenza dei file
    json_files = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob(os.path.join(CARTELLA_JSON_INPUT, "*.json"))}
    text_files = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob(os.path.join(CARTELLA_TESTO_INPUT, "*.txt"))}
    chiavi_comuni = set(json_files.keys()) & set(text_files.keys())
    
    if not chiavi_comuni:
        print(f"Nessuna coppia JSON/Testo trovata con nomi base corrispondenti nelle cartelle specificate.")
        return

    print(f"\nTrovate {len(chiavi_comuni)} coppie da mutare.")
    print(f"Obiettivo: Generare **{NUM_MUTAZIONI_PER_ESEMPIO * len(chiavi_comuni)}** nuovi file.")
    print("-" * 60)

    # Ciclo di elaborazione
    coppie_processate = 0
    file_generati = 0
    
    for nome_base in chiavi_comuni:
        percorso_json_originale = json_files[nome_base]
        percorso_testo_originale = text_files[nome_base]
        print(f"Mutando coppia base: **{nome_base}**")
        
        try:
            with open(percorso_json_originale, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                json_content_str = json.dumps(json_data, indent=2)

            with open(percorso_testo_originale, "r", encoding="utf-8") as f:
                text_content_str = f.read()

            # Genera le N mutazioni
            for i in range(1, NUM_MUTAZIONI_PER_ESEMPIO + 1):
                
                json_mutato_str, testo_mutato_str = muta_semantica_con_gemini(json_content_str, text_content_str)
                json_data_mutato = json.loads(json_mutato_str)
                nome_file_output = f"{nome_base}_{i}"
                
                percorso_json_output = os.path.join(CARTELLA_JSON_MUTATO, f"{nome_file_output}.json")
                with open(percorso_json_output, "w", encoding="utf-8") as f:
                    json.dump(json_data_mutato, f, indent=4)
                    
                percorso_testo_output = os.path.join(CARTELLA_TESTO_MUTATO, f"{nome_file_output}.txt")
                with open(percorso_testo_output, "w", encoding="utf-8") as f:
                    f.write(testo_mutato_str)
                
                print(f"   Generato set {i}: **{nome_file_output}.json / .txt**")
                file_generati += 2
            
            coppie_processate += 1
            time.sleep(PAUSA_TRA_CHIAMATE_SECONDI)

        except exceptions.ResourceExhausted:
            print(f"   ERRORE 429 (Quota): Limite raggiunto. Interrompo il processo.")
            break
        except json.JSONDecodeError:
            print(f"   ERRORE JSON: L'output per {nome_base} non era JSON valido. Salto.")
        except Exception as e:
            print(f"   ERRORE non gestito durante l'elaborazione di {nome_base}: {e}")
            
    print("\n" + "="*60)
    print("Processo di Mutazione Semantica Coerente Completato")
    print(f"Coppie base elaborate: **{coppie_processate}**")
    print(f"Totale file generati: **{file_generati}**")
    print("="*60)


if __name__ == "__main__":
    elabora_batch_mutazione_semantica()
    