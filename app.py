import streamlit as st
import os
import json
import yaml
import numpy as np
import hdbscan
import umap
import matplotlib.pyplot as plt
from collections import defaultdict
from sentence_transformers import SentenceTransformer
import openai
import random

# === Konfiguration ===
USE_GPT = st.sidebar.checkbox("GPT zur Clusterbenennung verwenden?", value=False)
openai.api_key = st.sidebar.text_input("OpenAI API-Key", type="password")

@st.cache_data(show_spinner=False)
def embed_utterances(utterances, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(utterances, show_progress_bar=False)

def cluster_utterances(embeddings):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, prediction_data=True)
    return clusterer.fit_predict(embeddings)

def gpt_category(samples):
    prompt = "Gib eine knappe Kategorienbezeichnung (1–2 Wörter) für folgende Aussagen:
" + "\n".join(f"- {s}" for s in samples[:5])
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception:
        return local_category(samples)

def local_category(samples):
    fallback = ["Frage", "Antwort", "Befehl", "Hinweis", "Ironie", "Zweifel"]
    return random.choice(fallback)

def assign_categories(utterances, labels):
    clusters = defaultdict(list)
    for u, l in zip(utterances, labels):
        clusters[l].append(u)
    label_to_name = {}
    for l, samples in clusters.items():
        label_to_name[l] = gpt_category(samples) if USE_GPT else local_category(samples)
    return [label_to_name[l] for l in labels], label_to_name

def induce_pcfg(sequence):
    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(sequence) - 1):
        transitions[sequence[i]][sequence[i + 1]] += 1
    return {k: {kk: vv / sum(v.values()) for kk, vv in v.items()} for k, v in transitions.items()}

def simulate_dialog(pcfg, start=None, maxlen=15):
    if not pcfg: return []
    if not start:
        start = random.choice(list(pcfg.keys()))
    result = [start]
    for _ in range(maxlen - 1):
        if start not in pcfg:
            break
        next_items = list(pcfg[start].items())
        next_tokens, probs = zip(*next_items)
        start = random.choices(next_tokens, probs)[0]
        result.append(start)
    return result

def render_umap(embeddings, labels):
    reducer = umap.UMAP(random_state=42)
    reduced = reducer.fit_transform(embeddings)
    fig, ax = plt.subplots()
    unique_labels = set(labels)
    for label in unique_labels:
        mask = labels == label
        ax.scatter(reduced[mask, 0], reduced[mask, 1], label=f"Cluster {label}", alpha=0.6)
    ax.set_title("UMAP + HDBSCAN-Cluster")
    ax.legend()
    return fig

def pcfg_to_dot(pcfg):
    lines = ["digraph PCFG {"]
    for src, dsts in pcfg.items():
        for dst, prob in dsts.items():
            lines.append(f'"{src}" -> "{dst}" [label="{prob:.2f}"];')
    lines.append("}")
    return "\n".join(lines)

st.title("🗣️ Algorithmisch-Rekursive Sequenzanalyse 3.0")

uploaded_files = st.file_uploader("Lade Transkripte hoch (.txt)", type="txt", accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        st.subheader(f"📄 Datei: {file.name}")
        raw_text = file.read().decode("utf-8")
        utterances = [line.split(":", 1)[1].strip() for line in raw_text.splitlines() if ":" in line]

        if not utterances:
            st.warning("Keine dialogischen Äußerungen gefunden.")
            continue

        embeddings = embed_utterances(utterances)
        labels = cluster_utterances(embeddings)
        categories, label_map = assign_categories(utterances, labels)
        pcfg = induce_pcfg(categories)

        st.markdown("### 🔖 Kategorien")
        for cluster, name in label_map.items():
            st.write(f"**Cluster {cluster}** → {name}")

        st.markdown("### 🧠 PCFG-Simulation")
        if st.button(f"🎲 Simuliere Dialog ({file.name})"):
            dialog = simulate_dialog(pcfg)
            st.write(" → ".join(dialog))

        st.markdown("### 📊 Cluster-Visualisierung")
        st.pyplot(render_umap(embeddings, labels))

        st.markdown("### 📥 Export")
        col1, col2 = st.columns(2)

        with col1:
            st.download_button("📎 PCFG als YAML", yaml.dump(pcfg, allow_unicode=True), file_name=f"{file.name}_pcfg.yaml")
        with col2:
            st.download_button("📎 PCFG als DOT", pcfg_to_dot(pcfg), file_name=f"{file.name}_pcfg.dot")
