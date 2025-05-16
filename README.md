# Algorithmisch-Rekursive Sequenzanalyse 3.0

Dieses Projekt bietet eine Webanwendung zur automatischen Analyse von dialogischen Transkripten mithilfe von Sentence-BERT, HDBSCAN-Clustering und probabilistischen kontextfreien Grammatiken (PCFG).

## Funktionen

- 📂 Mehrfacher Transkript-Upload
- 🧠 Sentence-BERT für Embedding
- 📊 HDBSCAN für Clusterbildung
- 🧾 Kategorien mit GPT oder lokal
- 📈 Visualisierung via UMAP
- 🔁 PCFG-Induktion aus Sequenzen
- 🎲 Simulation von Dialogen
- 📎 Export der PCFG als `.yaml` oder `.dot`

## Dateien

- `app.py` – Die Hauptdatei mit der Streamlit-App
- `requirements.txt` – Python-Abhängigkeiten
- `README.md` – Dieses Dokument

## Installation

```bash
git clone https://github.com/dein-nutzername/Algorithmisch-Rekursive-Sequenzanalyse-3.0.git
cd Algorithmisch-Rekursive-Sequenzanalyse-3.0
pip install -r requirements.txt
streamlit run app.py
```

## Nutzung

1. Öffne die Web-App im Browser
2. Lade `.txt`-Transkripte hoch
3. Die App clustert Äußerungen und generiert Kategorien
4. Du kannst die resultierende PCFG exportieren oder Dialoge simulieren




