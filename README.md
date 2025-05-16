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



## Nutzung

1. Öffne die Web-App im Browser
2. Lade `.txt`-Transkripte hoch
3. Die App clustert Äußerungen und generiert Kategorien
4. Du kannst die resultierende PCFG exportieren oder Dialoge simulieren


# Algorithmisch Rekursive Sequenzanalyse 3.0

**Algorithmisch Rekursive Sequenzanalyse (ARS 3.0)** ist ein modulares System zur Verarbeitung, Analyse und Simulation von dialogischen Transkripten. Es ermöglicht die automatische Clusterung semantisch ähnlicher Aussagen, den Aufbau probabilistischer kontextfreier Grammatiken (PCFG), sowie die Generierung synthetischer Dialoge auf Basis dieser Strukturen.

---

## 🔧 Projektstruktur




ars3/<br>
├── ars\_core.py            # Zentrale Logik: Verarbeitung, PCFG-Export, Simulation<br>
├── app.py                 # GUI (Streamlit oder tkinter)<br>
├── categories.json        # Persistente Speicherung erkannter Kategorien<br>
├── data/<br>
│   └── test\_transcript.txt # Beispielhafte Dialogdaten zur Analyse<br>
├── output/<br>
│   ├── pcfg.json          # Exportierte PCFG im JSON-Format<br>
│   ├── pcfg.csv           # Exportierte PCFG im CSV-Format<br>
│   ├── pcfg.yaml          # Exportierte PCFG im YAML-Format<br>
│   └── cluster\_plot.png   # Visualisierung der Clusterstruktur<br>
├── requirements.txt       # Abhängigkeiten<br>
├── setup.py               # Installationsskript<br>
└── README.md              # Diese Datei<br>

```

---

## 🧠 Hauptfunktionen

### `ars_core.py`

- **`process_multiple_dialogs(transcript_paths)`**  
  Lädt mehrere Transkripte, analysiert semantisch ähnliche Aussagen, clustert mit HDBSCAN und erstellt eine PCFG.

- **`simulate_dialog(pcfg, max_turns=10)`**  
  Simuliert einen plausiblen neuen Dialog basierend auf einer gegebenen PCFG.

- **`export_pcfg_to_json(pcfg, filepath)`**  
  Exportiert die PCFG in eine JSON-Datei.

- **`export_pcfg_to_csv(pcfg, filepath)`**  
  Exportiert die PCFG in eine CSV-Datei zur besseren tabellarischen Auswertung.

- **`export_pcfg_to_yaml(pcfg, filepath)`**  
  Exportiert die PCFG in das YAML-Format (z. B. für andere Tools oder manuelle Bearbeitung).

---

## 🖥️ GUI (`app.py`)

- Wähle Transkripte zur Verarbeitung
- Starte Analyse & Clustering
- Visualisiere Clusterstruktur
- Exportiere PCFG in verschiedenen Formaten
- Simuliere neue Dialoge auf Knopfdruck

Die GUI ist modular aufgebaut und kann wahlweise in Streamlit (Web) oder tkinter (lokal) betrieben werden.


## 📦 Installation

1. Klone oder entpacke das Repository:

2. Installiere alle Abhängigkeiten:

```bash
pip install -r requirements.txt
```

3. Starte die GUI (wenn `app.py` eine `main()`-Funktion enthält):

```bash
python app.py
```

Oder über den Konsolenbefehl:

```bash
ars-gui
```

---

## ⚙️ Setup für Installation

Optional kann das Projekt als Paket installiert werden:

```bash
pip install .
```

---

## 📈 Exportformate

* **JSON**: Für strukturierten maschinenlesbaren Export
* **CSV**: Zur einfachen tabellarischen Analyse (z. B. in Excel oder Pandas)
* **YAML**: Für lesbare Konfigurationen und Weiterverarbeitung in externen Tools





