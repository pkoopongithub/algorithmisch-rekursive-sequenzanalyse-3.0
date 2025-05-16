import os
import json
import csv
import yaml
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
import hdbscan
import random

# Modell laden
model = SentenceTransformer("all-MiniLM-L6-v2")

def read_transcripts(file_paths):
    utterances = []
    for file in file_paths:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    utterances.append(line)
    return utterances

def embed_utterances(utterances):
    return model.encode(utterances)

def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
    labels = clusterer.fit_predict(embeddings)
    return labels

def build_pcfg(labels, utterances):
    pcfg = {}
    terminal_chain = []
    for i in range(len(labels) - 1):
        src = str(labels[i])
        dst = str(labels[i + 1])
        terminal_chain.append(src)
        if src not in pcfg:
            pcfg[src] = {}
        pcfg[src][dst] = pcfg[src].get(dst, 0) + 1

    # Wahrscheinlichkeiten normalisieren
    for src in pcfg:
        total = sum(pcfg[src].values())
        for dst in pcfg[src]:
            pcfg[src][dst] /= total

    return pcfg, terminal_chain

def process_multiple_dialogs(file_paths):
    utterances = read_transcripts(file_paths)
    embeddings = embed_utterances(utterances)
    labels = cluster_embeddings(embeddings)
    pcfg, terminal_chain = build_pcfg(labels, utterances)
    return {
        "utterances": utterances,
        "embeddings": embeddings,
        "labels": labels,
        "pcfg": pcfg,
        "terminal_chain": terminal_chain
    }

def simulate_dialog(pcfg, length=6):
    if not pcfg:
        return []
    current = random.choice(list(pcfg.keys()))
    sequence = [current]
    for _ in range(length - 1):
        if current not in pcfg:
            break
        next_states = list(pcfg[current].keys())
        probs = list(pcfg[current].values())
        current = np.random.choice(next_states, p=probs)
        sequence.append(current)
    return sequence

def export_pcfg_to_json(pcfg, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(pcfg, f, indent=2)

def export_pcfg_to_csv(pcfg, filepath):
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "Probability"])
        for src in pcfg:
            for dst in pcfg[src]:
                writer.writerow([src, dst, pcfg[src][dst]])

def export_pcfg_to_yaml(pcfg, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(pcfg, f, sort_keys=False, allow_unicode=True)
