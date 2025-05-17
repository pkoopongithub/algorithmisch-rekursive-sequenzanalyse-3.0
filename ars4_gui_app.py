import os
import json
import numpy as np
from sklearn.cluster import HDBSCAN
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from scipy.stats import pearsonr
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# Modell für Embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

class ARSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-PCFG Generator")
        self.transcripts = []
        self.terminal_symbols = []
        self.pcfg = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Button(main_frame, text="Load Transcripts", command=self.load_transcripts).grid(row=0, column=0, pady=5)
        ttk.Button(main_frame, text="Generate Grammar", command=self.generate_grammar).grid(row=0, column=1, pady=5)
        ttk.Button(main_frame, text="Optimize Grammar", command=self.optimize_grammar).grid(row=0, column=2, pady=5)
        ttk.Button(main_frame, text="Simulate Dialog", command=self.simulate_dialog).grid(row=0, column=3, pady=5)
        
        self.output_text = tk.Text(main_frame, height=20, width=80)
        self.output_text.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(main_frame, text="Export JSON", command=lambda: self.export_grammar("json")).grid(row=2, column=0)
        ttk.Button(main_frame, text="Export YAML", command=lambda: self.export_grammar("yaml")).grid(row=2, column=1)
    
    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
    
    def load_transcripts(self):
        files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if not files:
            return
            
        self.transcripts = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                self.transcripts.extend([line.strip() for line in f if line.strip()])
        
        self.log(f"Loaded {len(self.transcripts)} utterances from {len(files)} files.")
    
    def generate_grammar(self):
        if not self.transcripts:
            messagebox.showwarning("Warning", "No transcripts loaded!")
            return
            
        # Schritt 1: Terminalzeichen generieren
        embeddings = model.encode(self.transcripts)
        
        # KORREKTUR: Parameter gen_min_span_tree entfernt
        clusterer = HDBSCAN(min_cluster_size=3)
        clusters = clusterer.fit_predict(embeddings)
        
        # Unique Terminalzeichen erstellen
        self.terminal_symbols = [f"T_{c+1}" for c in clusters]
        unique_terminals = list(set(self.terminal_symbols))
        
        self.log(f"Generated {len(unique_terminals)} terminal symbols: {unique_terminals}")
        
        # Schritt 2: Nonterminale und Regeln ableiten
        self.pcfg = self.induce_grammar_rules(self.terminal_symbols)
        self.log("\nGenerated PCFG rules:")
        for nt, rules in self.pcfg.items():
            self.log(f"{nt} → {rules}")
    
    def induce_grammar_rules(self, terminals, n=3):
        rules = defaultdict(dict)
        
        # Einfache Übergänge zwischen Terminalzeichen
        for i in range(len(terminals)-1):
            src = terminals[i]
            dst = terminals[i+1]
            rules[src][dst] = rules[src].get(dst, 0) + 1
        
        # Nonterminale für häufige N-Gramme
        ngram_counts = defaultdict(int)
        for i in range(len(terminals)-n+1):
            ngram = " ".join(terminals[i:i+n])
            ngram_counts[ngram] += 1
        
        # Füge Nonterminale für häufige N-Gramme hinzu
        for ngram, count in ngram_counts.items():
            if count > 1:
                nt = f"NT_{ngram.replace(' ', '_')}"
                rules[nt] = {ngram: 1.0}
                
                # Ersetze Vorkommen im Haupt-PCFG
                for src in list(rules.keys()):
                    if ngram in rules[src]:
                        rules[src][nt] = rules[src].pop(ngram)
        
        # Normalisiere Wahrscheinlichkeiten
        for src in rules:
            total = sum(rules[src].values())
            rules[src] = {dst: cnt/total for dst, cnt in rules[src].items()}
        
        return dict(rules)
    
    def optimize_grammar(self, iterations=10):
        if not self.pcfg:
            messagebox.showwarning("Warning", "Generate grammar first!")
            return
            
        empirical_freq = self.calculate_frequencies([self.terminal_symbols])
        
        for i in range(iterations):
            generated_chains = []
            for _ in range(5):
                chain = self.simulate_chain(max_length=len(self.terminal_symbols))
                generated_chains.append(chain)
            
            gen_freq = self.calculate_frequencies(generated_chains)
            corr, p_value = pearsonr(empirical_freq, gen_freq)
            
            self.log(f"Iteration {i+1}: Correlation = {corr:.3f}, p = {p_value:.3f}")
            
            if corr > 0.9:
                break
                
            self.adjust_probabilities(empirical_freq, gen_freq)
    
    def calculate_frequencies(self, chains):
        all_terminals = sorted(set(self.terminal_symbols))
        freq = np.zeros(len(all_terminals))
        term_to_idx = {t: i for i, t in enumerate(all_terminals)}
        
        for chain in chains:
            for term in chain:
                if term in term_to_idx:
                    freq[term_to_idx[term]] += 1
        
        return freq / freq.sum() if freq.sum() > 0 else freq
    
    def adjust_probabilities(self, empirical_freq, gen_freq):
        all_terminals = sorted(set(self.terminal_symbols))
        adjustment = empirical_freq - gen_freq
        
        for src in self.pcfg:
            new_rules = {}
            for dst in self.pcfg[src]:
                if dst in all_terminals:
                    idx = all_terminals.index(dst)
                    new_prob = max(0.01, min(0.99, self.pcfg[src][dst] + 0.1 * adjustment[idx]))
                    new_rules[dst] = new_prob
                else:
                    new_rules[dst] = self.pcfg[src][dst]
            
            total = sum(new_rules.values())
            self.pcfg[src] = {k: v/total for k, v in new_rules.items()}
    
    def simulate_chain(self, max_length=10):
        chain = []
        current = np.random.choice(list(self.pcfg.keys()))
        
        for _ in range(max_length):
            if current not in self.pcfg:
                break
                
            next_options = list(self.pcfg[current].keys())
            probs = list(self.pcfg[current].values())
            next_item = np.random.choice(next_options, p=probs)
            
            if next_item.startswith("NT_"):
                expanded = next_item[3:].replace("_", " ").split()
                chain.extend(expanded)
                current = expanded[-1] if expanded else None
            else:
                chain.append(next_item)
                current = next_item
        
        return chain
    
    def simulate_dialog(self):
        if not self.pcfg:
            messagebox.showwarning("Warning", "Generate grammar first!")
            return
            
        chain = self.simulate_chain()
        self.log("\nSimulated dialog sequence:")
        self.log(" → ".join(chain))
    
    def export_grammar(self, format):
        if not self.pcfg:
            messagebox.showwarning("Warning", "No grammar to export!")
            return
            
        file = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )
        
        if not file:
            return
            
        if format == "json":
            with open(file, 'w') as f:
                json.dump(self.pcfg, f, indent=2)
        elif format == "yaml":
            import yaml
            with open(file, 'w') as f:
                yaml.dump(self.pcfg, f)
        
        self.log(f"Grammar exported to {file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ARSGUI(root)
    root.mainloop()
