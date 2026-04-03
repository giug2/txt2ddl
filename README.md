# 📊 LLM-Database-Engineering-Benchmark

This repository contains the **benchmark dataset** developed for my Master's Thesis in Computer Engineering. It is designed to evaluate the impact of Large Language Models (LLMs) on the database design lifecycle, specifically focusing on the transformation of natural language requirements into structured DDL.

## 📌 Project Overview

The core objective of this research was to create a structured workflow where LLMs process business requirements to generate architectural outputs. The benchmark tracks the transition across three main stages:
1. **Requirements**: Natural language descriptions of the domain.
2. **Conceptual Models**: Structured representations (JSON).
3. **Logical Models**: Executable SQL (DDL) scripts.

## 📁 Repository Structure

The dataset is mirrored in two languages (**Italian** and **English**) and includes a dedicated section for data processing scripts.

```text
├── 🇮🇹 Italian/
│   ├── txt/                # Natural language texts (TXT)
│   ├── json/               # Conceptual models (JSON)
│   └── sql/                # Data Definition Language scripts (SQL)
│
├── 🇬🇧 English/
│   ├── txt/                # Translated & adapted texts (TXT)
│   ├── json/               # Conceptual models (JSON)
│   └── sql/                # Data Definition Language scripts (SQL)
│
└── Scripts/                # Data augmentation and processing tools
