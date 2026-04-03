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
CARTELLA_JSON_INPUT = os.path.join(BASE_DIR, "json_semantico") 
CARTELLA_TESTO_OUTPUT = os.path.join(BASE_DIR, "testo_toni_mutaz") 

# Parametri di Generazione
MODEL_NAME = "gemini-2.5-pro"
TONI = {
    "formale": "Descrizione formale, tecnica e concisa, come una specifica di progetto. Usa abbreviazioni comuni (PK, FK) solo se sono naturali nel contesto.",
    "narrativo": "Descrizione narrativa, discorsiva e orientata all'utente. Spiega lo scopo del sistema in modo coinvolgente.",
    "ambiguo": "Descrizione informale con terminologia vaga, leggermente imprecisa o con gergo quotidiano. Rendi il testo meno pulito e più colloquiale."
}
PAUSA_TRA_CHIAMATE_SECONDI = 2.0


def genera_variante_tono(json_content: str, tono: str, istruzione_tono: str) -> str:
    """
    Invia il contenuto JSON a Gemini per generare una variante testuale con un tono specifico.
    Include la gestione robusta dell'output per evitare 'NoneType' object has no attribute 'strip'.
    """
    SYSTEM_INSTRUCTION = (
        "Sei un assistente AI specializzato nella modellazione di dati. Il tuo compito è prendere "
        "la struttura di un database in formato JSON e GENERARE una descrizione testuale "
        "che mantenga fedelmente tutte le entità e le relazioni del JSON. "
        f"Requisito aggiuntivo: {istruzione_tono} "
        "La descrizione DEVE essere un testo completo e coerente, MAI vuoto, "
        "e deve essere l'unico contenuto della risposta, senza JSON, intestazioni, o liste."
    )
    
    prompt = f"""
    Genera una descrizione testuale dettagliata e completa basata sul seguente schema JSON. 
    Applica rigorosamente lo stile di tono '{tono}'.

    --- JSON SCHEMA ---
    {json_content}
    --- FINE JSON ---
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7, # Temperatura media per permettere la variazione di tono
                max_output_tokens=8192 
            )
        )        
        output_text = response.text
        
        if output_text is None or not output_text.strip():
            raise ValueError("Il modello ha restituito un testo vuoto (None o stringa bianca).")
            
        return output_text.strip()
        
    except exceptions.ResourceExhausted:
        raise exceptions.ResourceExhausted("Limite API Quota raggiunto.")
    except Exception as e:
        raise Exception(f"Errore durante la chiamata API per il tono {tono}: {e}")


def elabora_batch_variazione_tono():
    """
    Funzione principale per l'elaborazione dei file JSON e la generazione di varianti di tono.
    Ora implementa una gestione degli errori a livello di tono.
    """
    print(f"Connesso al modello: **{MODEL_NAME}**")
    print(f"Cartella JSON Input: **{os.path.basename(CARTELLA_JSON_INPUT)}**")
    print(f"Cartella Testo Output: **{os.path.basename(CARTELLA_TESTO_OUTPUT)}**")
    
    if not os.path.exists(CARTELLA_TESTO_OUTPUT):
        os.makedirs(CARTELLA_TESTO_OUTPUT)
        print(f"Creata cartella di output: **{os.path.basename(CARTELLA_TESTO_OUTPUT)}**")

    if not os.path.isdir(CARTELLA_JSON_INPUT):
        print(f"ERRORE: La cartella JSON input **{CARTELLA_JSON_INPUT}** non esiste.")
        return

    # Ricerca dei file JSON
    lista_file_json = glob.glob(os.path.join(CARTELLA_JSON_INPUT, "*.json")) 
    
    if not lista_file_json:
        print(f"Nessun file JSON trovato in **{CARTELLA_JSON_INPUT}**. Esco.")
        return

    num_varianti_totali = len(lista_file_json) * len(TONI)
    print(f"\nTrovati {len(lista_file_json)} file JSON base.")
    print(f"Obiettivo: Generare **{num_varianti_totali}** nuovi file di testo (uno per tono).")
    print("-" * 60)

    # Ciclo di elaborazione
    file_processati = 0
    file_generati = 0
    
    for percorso_json_input in lista_file_json:
        nome_file_base = os.path.basename(percorso_json_input)
        nome_base_senza_estensione = os.path.splitext(nome_file_base)[0]
        print(f"Elaborando JSON base: **{nome_file_base}**")
        
        try:
            with open(percorso_json_input, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                json_content_str = json.dumps(json_data, indent=2)

            for tono_key, istruzione in TONI.items():
                print(f"   -> Generando variante: {tono_key.capitalize()}...")
                try:
                    variante_testuale = genera_variante_tono(json_content_str, tono_key, istruzione)
                    nome_file_output = f"{nome_base_senza_estensione}_{tono_key}.txt"
                    percorso_output = os.path.join(CARTELLA_TESTO_OUTPUT, nome_file_output)
                    
                    with open(percorso_output, "w", encoding="utf-8") as f:
                        f.write(variante_testuale)
                    
                    print(f"      Salvato con successo: **{nome_file_output}**")
                    file_generati += 1
                    
                except exceptions.ResourceExhausted:
                    raise 
                except Exception as e:
                    print(f"      ERRORE di Generazione ({tono_key.upper()}): {e}")
                
                time.sleep(PAUSA_TRA_CHIAMATE_SECONDI)
            file_processati += 1
            
        except exceptions.ResourceExhausted:
            print(f"   ERRORE 429 (Quota): Limite raggiunto. Interrompo il processo.")
            break 
        except Exception as e:
            print(f"   ERRORE critico non gestito durante l'elaborazione di {nome_file_base}: {e}. Salto il file.")
            
    print("\n" + "="*60)
    print("Processo di Variazione di Tono Completato")
    print(f"File JSON base elaborati: **{file_processati}**")
    print(f"Nuovi file di testo generati: **{file_generati}**")
    print("="*60)


if __name__ == "__main__":
    elabora_batch_variazione_tono()
    