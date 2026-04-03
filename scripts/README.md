# 🛠️ Data Augmentation & Processing Scripts

This folder contains the Python suite developed to generate, translate, and augment the benchmark dataset. These scripts leverage LLMs (Google Gemini) and automated translation tools to expand the initial 108 examples.

## 📝 Script Descriptions

| Script Name | Purpose |
| :--- | :--- |
| **`ocr_via_api.py`** | Used to extract text from image-based sources (like old exam PDF screenshots) using Gemini capabilities. |
| **`json_to_ddl.py`** | The core utility that automates the transformation of Conceptual Models (JSON) into executable Logical Models (SQL/DDL). |
| **`mutazione_semantica.py`** | Uses LLMs to perform semantic paraphrasing of the requirements, generating variations that maintain the same logical meaning but use different terminology. |
| **`entity_swapping.py`** | An augmentation script that modifies the order of entities within relationships. This tests if the LLM's understanding is biased by the sequence of elements in the requirements. |
| **`entity_swapping_offline.py`** | Similar to entity swapping, but performs the modifications on the provided text (offline) to test structural robustness without further AI generation. |
| **`reverse_generation.py`** | Given a conceptual schema, this script uses Gemini to generate **three different natural language descriptions** with varying tones, providing multiple linguistic perspectives for the same database logic. |
| **`translate.py`** | Handles the automated translation of requirements and documentation from Italian to English using the `deep-translator` library. |
---

## ⚙️ Setup and Usage

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

> [!IMPORTANT]
> **API Configuration Required**
> Most scripts in this folder require a **Google Gemini API Key** to function. 
> You must either:
> 1. Set your API key as an environment variable (recommended).
> 2. Update the `genai.configure()` section directly within each script before execution.
