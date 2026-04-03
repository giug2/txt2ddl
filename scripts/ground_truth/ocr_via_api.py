import google.generativeai as genai
import os
import glob 
from PIL import Image 
import time 
from google.api_core import exceptions  


# Sostituisci con la chiave API di Google
GOOGLE_API_KEY = 'CHIAVE'
genai.configure(api_key=GOOGLE_API_KEY)

# Percorsi delle cartelle
cartella_immagini = "dataset/png"
cartella_output = "dataset/json"

if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)


# Prompt di analisi
prompt_per_analisi_er = """
Sei un assistente AI specializzato nell'analisi di diagrammi Entità-Relazione (ERD) per database.

Analizza l'immagine ERD fornita e identifica:
1.  Tutte le entità.
2.  Per ogni entità, i suoi attributi. Specifica quale attributo è la Chiave Primaria (PK).
3.  Tutte le relazioni tra le entità.
4.  Le cardinalità per ogni relazione (es. 1:N, N:N, 1:1).

Restituisci l'analisi ESCLUSIVAMENTE in formato JSON valido. Non aggiungere testo, spiegazioni o ```json``` prima o dopo il blocco JSON.

Ecco lo schema JSON che devi seguire:
{
  "entities": [
    {
      "name": "NomeEntita",
      "attributes": [
        { "name": "id_attributo", "is_pk": true },
        { "name": "altro_attributo", "is_pk": false }
      ]
    }
  ],
  "relationships": [
    {
      "entity1": "NomeEntitaA",
      "entity2": "NomeEntitaB",
      "cardinality": "1:N"
    }
  ]
}
"""

# Modello visivo
model = genai.GenerativeModel('gemini-2.5-pro') 

lista_file_png = glob.glob(os.path.join(cartella_immagini, "*.png"))

print(f"Trovati {len(lista_file_png)} file PNG da analizzare.")

for percorso_immagine in lista_file_png:
    print(f"Sto analizzando: {percorso_immagine}...")
    try:
        img = Image.open(percorso_immagine)
        response = model.generate_content([prompt_per_analisi_er, img])

        # Estrai il testo della risposta
        output_json = response.text

        nome_base = os.path.basename(percorso_immagine)
        nome_file_output = os.path.splitext(nome_base)[0] + ".json"
        percorso_output = os.path.join(cartella_output, nome_file_output)

        # Salva il JSON su file
        with open(percorso_output, "w", encoding="utf-8") as f:
            f.write(output_json)
        
        print(f"Salvataggio riuscito in: {percorso_output}")
        time.sleep(2)

    except exceptions.ResourceExhausted as e:
        print(f"ERRORE 429 (Quota): Limite raggiunto.")
        print("Attendo 60 secondi come richiesto dall'API prima di riprovare...")
        time.sleep(60) 
        print("...Riprovo.")

    except Exception as e:
        print(f"ERRORE (Altro) durante l'analisi di {percorso_immagine}: {e}")
        i += 1

print("Processo completato.")
