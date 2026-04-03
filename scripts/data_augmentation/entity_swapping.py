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
CARTELLA_JSON_MUTATO = os.path.join(BASE_DIR, "json_mutati2") 

# Parametri di Mutazione
MODEL_NAME = "gemini-2.5-pro"
NUM_MUTAZIONI_PER_ESEMPIO = 1 # Numero di varianti mutate da generare per ogni JSON originale
PAUSA_TRA_CHIAMATE_SECONDI = 1.0

# Prompt di Mutazione 
SYSTEM_INSTRUCTION_SWAP = (
    "Sei un AI specializzato in Data Augmentation per database. Il tuo compito è prendere "
    "uno schema ER in formato JSON e applicare una 'mutazione' di tipo Entity Swapping. "
    "Per ogni richiesta, devi restituire un JSON MUTATO, diverso dall'originale, "
    "che rispetti rigorosamente il seguente schema JSON (devi mantenere gli stessi campi). "
    "La mutazione DEVE riguardare entrambi le seguenti operazioni: "
    "1. SCAMBIARE L'ORDINE DEI NOMI delle entità collegate nelle relazioni "
    " (operazione DEVE essere fatta per almeno la metà delle relazioni presenti nel JSON) "
    "   e se necessario INVERTIRE la cardinalità (es. '1:N' diventa 'N:1'). "
    "2. SCAMBIARE IL NOME di due attributi che non sono chiavi primarie, mantenendoli nelle rispettive entità. "
    "Il JSON finale restituito DEVE essere perfettamente valido e contenere SOLO il blocco JSON mutato."
)


# --- FUNZIONI ---
def muta_json_con_gemini(json_content: str, indice_mutazione: int) -> str:
    """
    Invia il contenuto JSON a Gemini per la mutazione.
    """
    prompt = f"""
    Applica una mutazione di Entity Swapping al seguente schema JSON. 
    Questa è la mutazione numero {indice_mutazione}. Assicurati che il JSON mutato sia diverso 
    da quello originale e da qualsiasi altra mutazione precedente.

    --- JSON SCHEMA ORIGINALE ---
    {json_content}
    --- FINE JSON ---
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION_SWAP,
                response_mime_type="application/json", # Richiedi direttamente output JSON
                temperature=0.7, # Temperatura media per favorire la mutazione ma mantenere la coerenza
                max_output_tokens=8192
            )
        )
        # Rimuove eventuali blocchi di codice e restituisce solo il testo JSON
        return response.text.strip().replace("```json", "").replace("```", "").strip()
        
    except exceptions.ResourceExhausted:
        raise exceptions.ResourceExhausted("Limite API Quota raggiunto.")
    except Exception as e:
        raise Exception(f"Errore durante la chiamata API: {e}")


def processa_json_per_mutazione():
    """
    Funzione principale per l'elaborazione dei file JSON in batch.
    """
    print(f"Connesso al modello: **{MODEL_NAME}**")
    print(f"Cartella JSON Input: **{CARTELLA_JSON_INPUT}**")
    print(f"Cartella JSON Output: **{CARTELLA_JSON_MUTATO}**")
    
    if not os.path.exists(CARTELLA_JSON_MUTATO):
        os.makedirs(CARTELLA_JSON_MUTATO)
        print(f"Creata cartella di output: **{CARTELLA_JSON_MUTATO}**")

    if not os.path.isdir(CARTELLA_JSON_INPUT):
        print(f"ERRORE: La cartella JSON input **{CARTELLA_JSON_INPUT}** non esiste.")
        return

    # Ricerca dei file JSON
    lista_file_json = glob.glob(os.path.join(CARTELLA_JSON_INPUT, "*.json")) 
    
    if not lista_file_json:
        print(f"Nessun file JSON trovato in **{CARTELLA_JSON_INPUT}**. Esco.")
        return

    print(f"\nTrovati {len(lista_file_json)} file JSON base da mutare.")
    print(f"Obiettivo: Generare **{NUM_MUTAZIONI_PER_ESEMPIO * len(lista_file_json)}** nuovi file JSON mutati.")
    print("-" * 60)

    # Ciclo di Elaborazione
    file_processati = 0
    file_generati = 0
    
    for percorso_json_input in lista_file_json:
        nome_file_base = os.path.basename(percorso_json_input)
        
        nome_base_senza_estensione = os.path.splitext(nome_file_base)[0]
        
        print(f"Mutando JSON base: **{nome_file_base}**")
        
        try:
            with open(percorso_json_input, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                json_content_str = json.dumps(json_data, indent=2)

            # Genera le N mutazioni
            for i in range(1, NUM_MUTAZIONI_PER_ESEMPIO + 1):
                
                mutated_json_str = muta_json_con_gemini(json_content_str, i)
                
                # Validazione e salvataggio
                mutated_data = json.loads(mutated_json_str) # Verifica che sia JSON valido
                
                nome_file_output = f"{nome_base_senza_estensione}_M.json"
                percorso_output = os.path.join(CARTELLA_JSON_MUTATO, nome_file_output)
                
                with open(percorso_output, "w", encoding="utf-8") as f:
                    json.dump(mutated_data, f, indent=4) # Salva il JSON formattato
                
                print(f"   Mutazione {i} salvata come: **{nome_file_output}**")
                file_generati += 1
            
            file_processati += 1
            
            # Pausa tra le richieste base
            time.sleep(PAUSA_TRA_CHIAMATE_SECONDI)

        except exceptions.ResourceExhausted:
            print(f"   ERRORE 429 (Quota): Limite raggiunto. Interrompo il processo.")
            break
        except json.JSONDecodeError:
            print(f"   ERRORE JSON: L'output per {nome_file_base} non era JSON valido. Salto.")
        except Exception as e:
            print(f"   ERRORE non gestito durante l'elaborazione di {nome_file_base}: {e}")
            
    print("\n" + "="*60)
    print("Processo di JSON Augmentation Completato")
    print(f"File JSON base elaborati: **{file_processati}**")
    print(f"Nuovi file JSON mutati generati: **{file_generati}**")
    print("="*60)


# Esecuzione del processo
if __name__ == "__main__":
    processa_json_per_mutazione()
    