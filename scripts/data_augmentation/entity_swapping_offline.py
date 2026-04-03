import os
import glob
import json
import time


# Percorsi delle cartelle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARTELLA_JSON_INPUT = os.path.join(BASE_DIR, "dataset/json") 
CARTELLA_JSON_MUTATO = os.path.join(BASE_DIR, "json_mutati")

# Parametri di Mutazione
NUM_MUTAZIONI_PER_ESEMPIO = 1 
PAUSA_TRA_CHIAMATE_SECONDI = 0.1


# --- FUNZIONI ---
def swap_cardinality(cardinality: str) -> str:
    """Inverte la cardinalità principale (solo 1:N <-> N:1)."""
    if cardinality == '1:N':
        return 'N:1'
    if cardinality == 'N:1':
        return '1:N'
    return cardinality


def muta_json_offline(json_data: dict) -> dict:
    """
    Applica Entity Swapping (scambio entity1 <-> entity2 + inversione cardinalità)
    per il formato JSON fornito.
    """
    # Crea una copia profonda dei dati per la mutazione
    mutated_data = json.loads(json.dumps(json_data))
    if 'relationships' in mutated_data:
        new_relationships = []
        
        for rel in mutated_data['relationships']:
            # Verifichiamo che i campi essenziali per la mutazione esistano
            if 'entity1' not in rel or 'entity2' not in rel or 'cardinality' not in rel:
                print(f"   [AVVISO] Saltata relazione con dati incompleti.")
                new_relationships.append(rel)
                continue

            # Implementa lo scambio di entità
            entity1_name = rel['entity1']
            entity2_name = rel['entity2']
            
            # Scambia i nomi delle entità
            rel['entity1'] = entity2_name
            rel['entity2'] = entity1_name
            
            # inversione della cardinalità
            current_cardinality = rel['cardinality']
            rel['cardinality'] = swap_cardinality(current_cardinality)
            
            new_relationships.append(rel)
        
        mutated_data['relationships'] = new_relationships
    return mutated_data


# --- FUNZIONE DI ELABORAZIONE PRINCIPALE ---
def processa_json_per_mutazione():
    """
    Funzione principale per l'elaborazione dei file JSON in batch (OFFLINE).
    """
    print(f"Modalità: **OFFLINE - Mutazione Binaria (entity1/entity2)**")
    print(f"Cartella JSON Input: **{CARTELLA_JSON_INPUT}**")
    print(f"Cartella JSON Output: **{CARTELLA_JSON_MUTATO}**")
    
    # Preparazione delle cartelle
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

            # Genera le mutazioni 
            for i in range(1, NUM_MUTAZIONI_PER_ESEMPIO + 1): 
                mutated_data = muta_json_offline(json_data) 
                
                # Formato: ID_DATA_i.json
                suffix = f"_{i}" if NUM_MUTAZIONI_PER_ESEMPIO > 1 else ""
                nome_file_output = f"{nome_base_senza_estensione}{suffix}_MT.json"
                percorso_output = os.path.join(CARTELLA_JSON_MUTATO, nome_file_output)
                
                with open(percorso_output, "w", encoding="utf-8") as f:
                    json.dump(mutated_data, f, indent=4) 
                
                print(f"   Mutazione {i} salvata come: **{nome_file_output}**")
                file_generati += 1
            
            file_processati += 1
            time.sleep(PAUSA_TRA_CHIAMATE_SECONDI)

        except json.JSONDecodeError:
            print(f"   ERRORE JSON: Il file {nome_file_base} non era JSON valido. Salto.")
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
    