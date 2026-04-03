# 📊 LLM-Database-Engineering-Benchmark

This repository contains the official benchmark and data augmentation pipeline developed for my **Master's Thesis in Computer Engineering** at Roma Tre University.

## 🌟 Project Purpose
The goal of this project was to investigate how **Large Language Models (LLMs)** can automate the database design lifecycle. This benchmark provides a structured path to test if an AI can consistently transform a messy, natural language description into a perfect, executable SQL database.

---

## 🛠️ How it was created

### 1. Starting Point: Data Extraction
Everything started from the [Roma Tre University Database Course](https://bd.inf.uniroma3.it/). I extracted **108 initial examples** of database exams and exercises. These were "raw" academic requirements that represent real-world logic complexity.

### 2. The Transformation Workflow
For each example, I structured the data into three progressive layers to simulate a real engineer's workflow:
* **Requirements**: The problem description in plain text.
* **Conceptual Model**: The logic translated into structured **JSON** (representing Entities and Relationships).
* **Logical Model**: The final **DDL (SQL)** script ready to be executed on a DBMS.

### 3. Data Augmentation & Localization
To make the benchmark more robust and accessible for international research, I developed a series of Python scripts (found in the `/Scripts` folder) to:
* **Translate & Adapt**: Every requirement was translated from Italian to English, ensuring technical terminology remained accurate.
* **Augment**: I applied techniques to expand the dataset, creating variations of the initial 108 cases to test the LLMs' consistency across different phrasing and languages.
