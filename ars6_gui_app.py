import os
import json
import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from scipy.stats import pearsonr
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nltk import ngrams
from langdetect import detect
from transformers import pipeline
import threading
from copy import deepcopy

class EnhancedDialogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM-enhanced Dialog Analyzer")
        
        # Modelle initialisieren
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        self.llm = pipeline("text2text-generation", model="google/flan-t5-base")
        
        # Datenstrukturen
        self.transcripts = []
        self.interacts = []
        self.pcfg = {}
        self.empirical_chain = []
        
        # GUI
        self.setup_ui()
        self.setup_visualization()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Button(main_frame, text="1. Load & Preprocess", 
                  command=self.load_and_preprocess).grid(row=0, column=0, pady=5)
        ttk.Button(main_frame, text="2. Analyze Meanings", 
                  command=self.analyze_meanings).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="3. Build Semantic PCFG", 
                  command=self.build_semantic_pcfg).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="4. Optimize", 
                  command=self.optimize_grammar).grid(row=3, column=0, pady=5)
        ttk.Button(main_frame, text="5. Visualize", 
                  command=self.visualize_grammar).grid(row=4, column=0, pady=5)
        
        self.output_text = tk.Text(main_frame, height=20, width=80)
        self.output_text.grid(row=0, column=1, rowspan=5, padx=10)
        
    def setup_visualization(self):
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=5, padx=10)
        
    def load_and_preprocess(self):
        files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if not files:
            return
            
        self.transcripts = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                self.transcripts.extend([line.strip() for line in f if line.strip()])
        
        self.log(f"Loaded {len(self.transcripts)} utterances")
        threading.Thread(target=self._preprocess).start()
    
    def _preprocess(self):
        self.root.after(0, lambda: self.log("Detecting languages..."))
        languages = set()
        for utterance in self.transcripts:
            try:
                lang = detect(utterance)
                languages.add(lang)
            except:
                pass
        self.root.after(0, lambda: self.log(f"Detected languages: {', '.join(languages)}"))
        
        self.root.after(0, lambda: self.log("Creating embeddings..."))
        self.embeddings = self.embedding_model.encode(self.transcripts)
        
    def analyze_meanings(self):
        if not self.transcripts:
            messagebox.showwarning("Warning", "Load transcripts first!")
            return
            
        self.interacts = []
        for i, utterance in enumerate(self.transcripts):
            # Zuerst manuelle Klassifikation versuchen
            manual_meaning = self._preprocess_utterance(utterance)
            if manual_meaning:
                self.interacts.append({
                    "utterance": utterance,
                    "meanings": [manual_meaning],
                    "selected_meaning": manual_meaning
                })
                continue
                
            context = " | ".join([u["utterance"] for u in self.interacts[-3:]]) if i > 0 else ""
            meanings = self._generate_meanings(utterance, context)
            filtered_meanings = self._filter_meanings(meanings, i)
            
            self.interacts.append({
                "utterance": utterance,
                "meanings": meanings,
                "selected_meaning": filtered_meanings[0] if filtered_meanings else "UNK"
            })
            
            self.log(f"Utterance {i+1}: {utterance[:50]}...")
            self.log(f"  Selected meaning: {filtered_meanings[0] if filtered_meanings else 'UNK'}")
    
    def _preprocess_utterance(self, utterance):
        # Kürzen und Normalisieren
        utterance = utterance[:100].lower().replace('\n', ' ')
        
        # Erweiterte Mustererkennung
        patterns = {
            'order': ['bitte', 'nehme', 'hätte', 'kaufen', 'gramm', 'kilo'],
            'question': ['?', 'wie', 'was', 'wo '],
            'confirmation': ['ja', 'okay', 'genau', 'richtig'],
            'greeting': ['guten tag', 'hallo', 'guten morgen'],
            'thanks': ['danke', 'vielen dank', 'dankeschön']
        }
        
        for category, keywords in patterns.items():
            if any(kw in utterance for kw in keywords):
                return f"{category.upper()}"
        
        return None
    
    def _generate_meanings(self, utterance, context):
        manual_meaning = self._preprocess_utterance(utterance)
        if manual_meaning:
            return [manual_meaning]
            
        prompt = f"""Generate a SINGLE, concise interpretation for this dialog utterance in German:
        Context: '{context}'
        Utterance: '{utterance}'
        Interpretation: The speaker"""
        try:
            output = self.llm(prompt, max_length=50, num_return_sequences=1)
            return [output[0]["generated_text"].strip()]
        except Exception as e:
            return ["UNK"]
    
    def _filter_meanings(self, meanings, index):
        if index == 0 or not meanings:
            return meanings
        return [meanings[0]]  # Immer erste Bedeutung akzeptieren
    
    def build_semantic_pcfg(self):
        if not self.interacts:
            messagebox.showwarning("Warning", "Analyze meanings first!")
            return
            
        meaning_embeddings = self.embedding_model.encode(
            [i["selected_meaning"] for i in self.interacts]
        )
        
        clusterer = HDBSCAN(min_cluster_size=3, metric='cosine')
        clusters = clusterer.fit_predict(meaning_embeddings)
        
        terminal_symbols = []
        for i, cluster_id in enumerate(clusters):
            if cluster_id == -1:
                terminal_symbols.append(f"T_{i}")
            else:
                terminal_symbols.append(f"C_{cluster_id}")
        
        self.pcfg = defaultdict(dict)
        self.empirical_chain = terminal_symbols
        
        # Stärkere Gewichtung häufiger Übergänge mit exponentieller Gewichtung
        for i in range(len(terminal_symbols)-1):
            src = terminal_symbols[i]
            dst = terminal_symbols[i+1]
            src_nt = f"NT_{src}"
            
            weight = np.exp(-0.1 * i)  # Exponentielle Gewichtung für nahe Übergänge
            self.pcfg[src][src_nt] = 1.0
            self.pcfg[src_nt][dst] = self.pcfg[src_nt].get(dst, 0) + weight
        
        # Normalisierung der Wahrscheinlichkeiten
        for src in self.pcfg:
            total = sum(self.pcfg[src].values())
            self.pcfg[src] = {dst: count/total for dst, count in self.pcfg[src].items()}
        
        self.log("\nGenerated Semantic PCFG:")
        for src in list(self.pcfg.keys())[:5]:
            for dst, prob in list(self.pcfg[src].items())[:3]:
                self.log(f"  {src.ljust(10)} → {dst.ljust(15)} [{prob:.2f}]")
    
    def _calculate_frequencies(self, chains):
        freq_dict = defaultdict(lambda: defaultdict(int))
        
        for chain in chains:
            for i in range(len(chain)-1):
                current = chain[i]
                next_symbol = chain[i+1]
                freq_dict[current][next_symbol] += 1
        
        all_transitions = []
        for src in freq_dict:
            for dst in freq_dict[src]:
                all_transitions.append(freq_dict[src][dst])
        
        return np.array(all_transitions)

    def _simulate_chain(self, max_length):
        if not self.pcfg:
            return []
        
        chain = []
        current = np.random.choice(list(self.pcfg.keys()))
        chain.append(current)
        
        while len(chain) < max_length:
            if current not in self.pcfg:
                break
                
            next_symbols = list(self.pcfg[current].keys())
            probs = list(self.pcfg[current].values())
            next_symbol = np.random.choice(next_symbols, p=probs)
            
            chain.append(next_symbol)
            current = next_symbol
            
        return chain

    def _adjust_probabilities(self, empirical, generated):
        # Dynamische Lernrate basierend auf Datensatzgröße
        adjustment_factor = max(0.01, 0.2 * (1 - np.exp(-len(self.empirical_chain)/100)))
        
        temp_freq = defaultdict(lambda: defaultdict(float))
        
        for i in range(len(self.empirical_chain)-1):
            src = self.empirical_chain[i]
            dst = self.empirical_chain[i+1]
            temp_freq[src][dst] += 1
        
        for src in self.pcfg:
            for dst in self.pcfg[src]:
                base_prob = temp_freq[src].get(dst, 0)
                smoothed_prob = (base_prob + 0.1) / (sum(temp_freq[src].values()) + 0.1 * len(self.pcfg[src]))
                self.pcfg[src][dst] = (1 - adjustment_factor) * self.pcfg[src][dst] + \
                                      adjustment_factor * smoothed_prob
        
        for src in self.pcfg:
            total = sum(self.pcfg[src].values())
            if total > 0:
                for dst in self.pcfg[src]:
                    self.pcfg[src][dst] /= total
    
    def optimize_grammar(self, iterations=20):
        if not self.pcfg:
            messagebox.showwarning("Warning", "Build PCFG first!")
            return
            
        empirical_freq = self._calculate_frequencies([self.empirical_chain])
        best_corr = -1
        best_pcfg = deepcopy(self.pcfg)
        
        for i in range(iterations):
            generated_chains = [
                self._simulate_chain(max_length=len(self.empirical_chain)) 
                for _ in range(5)
            ]
            
            gen_freq = self._calculate_frequencies(generated_chains)
            
            min_length = min(len(empirical_freq), len(gen_freq))
            empirical = empirical_freq[:min_length]
            generated = gen_freq[:min_length]
            
            try:
                if len(empirical) > 1 and len(generated) > 1:
                    corr, p_value = pearsonr(empirical, generated)
                    self.log(f"Iteration {i+1}: r = {corr:.3f}, p = {p_value:.3f}")
                    
                    if abs(corr) > 0.3 and p_value < 0.1:  # Nur signifikante Anpassungen
                        if corr > best_corr:
                            best_corr = corr
                            best_pcfg = deepcopy(self.pcfg)
                        
                        self._adjust_probabilities(empirical_freq, gen_freq)
                    
                    if corr > 0.9:
                        break
                else:
                    self.log(f"Iteration {i+1}: Not enough data for correlation")
                    break
                    
            except Exception as e:
                self.log(f"Error in iteration {i+1}: {str(e)}")
                break
        
        self.pcfg = best_pcfg  # Restore best version
        self.log(f"Optimization finished. Best r = {best_corr:.3f}")
        self.evaluate_grammar()

    def evaluate_grammar(self):
        # Berechne Konsistenz der generierten Dialoge
        test_chains = [self._simulate_chain(10) for _ in range(10)]
        coherence_scores = [self._calculate_coherence(chain) for chain in test_chains]
        self.log(f"Average coherence: {np.mean(coherence_scores):.2f}")

    def _calculate_coherence(self, chain):
        # Einfache Kohärenzmetrik: Anteil gültiger Übergänge
        valid_transitions = 0
        for i in range(len(chain)-1):
            if chain[i] in self.pcfg and chain[i+1] in self.pcfg[chain[i]]:
                valid_transitions += 1
        return valid_transitions / max(1, len(chain)-1)

    def visualize_grammar(self):
        if not self.pcfg:
            messagebox.showwarning("Warning", "Build PCFG first!")
            return

        self.figure.clf()
        G = nx.DiGraph()
        
        for src, transitions in self.pcfg.items():
            for dst, prob in transitions.items():
                G.add_edge(src, dst, weight=prob)
        
        pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)
        
        node_size = 1200
        font_size = 8
        edge_width_scale = 2.5
        
        ax = self.figure.add_subplot(111)
        
        nx.draw_networkx_nodes(
            G, pos, 
            node_size=node_size,
            node_color='skyblue',
            alpha=0.9,
            ax=ax
        )
        
        edges = nx.draw_networkx_edges(
            G, pos,
            width=[d['weight']*edge_width_scale for (_, _, d) in G.edges(data=True)],
            edge_color='gray',
            alpha=0.7,
            arrowstyle='->',
            arrowsize=15,
            ax=ax
        )
        
        nx.draw_networkx_labels(
            G, pos,
            font_size=font_size,
            font_family='sans-serif',
            ax=ax
        )
        
        edge_labels = {
            (u, v): f"{d['weight']:.2f}" 
            for u, v, d in G.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_size=font_size-1,
            label_pos=0.5,
            ax=ax
        )
        
        ax.set_title("Probabilistic Context-Free Grammar (PCFG)")
        ax.axis('off')
        plt.tight_layout()
        self.canvas.draw()
    
    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedDialogAnalyzer(root)
    root.mainloop()
