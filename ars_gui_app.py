import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import csv
import yaml
import numpy as np

from ars_core import (
    process_multiple_dialogs,
    simulate_dialog,
    export_pcfg_to_json,
    export_pcfg_to_csv,
    export_pcfg_to_yaml
)

class ARSGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARS 3.0 – Algorithmisch Rekursive Sequenzanalyse")

        self.dialog_files = []
        self.processed_data = None

        self.build_gui()

    def build_gui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="ARS 3.0 Dialogverarbeitung", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Button(frm, text="Transkripte laden", command=self.load_dialogs).grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Button(frm, text="Verarbeiten", command=self.run_processing).grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Button(frm, text="Dialog simulieren", command=self.run_simulation).grid(row=1, column=2, sticky="ew", pady=5)

        ttk.Separator(frm).grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(frm, text="PCFG → JSON", command=lambda: self.export_pcfg("json")).grid(row=3, column=0, pady=5)
        ttk.Button(frm, text="PCFG → CSV", command=lambda: self.export_pcfg("csv")).grid(row=3, column=1, pady=5)
        ttk.Button(frm, text="PCFG → YAML", command=lambda: self.export_pcfg("yaml")).grid(row=3, column=2, pady=5)

        self.text_output = tk.Text(frm, wrap="word", height=20)
        self.text_output.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=10)

    def log(self, msg):
        self.text_output.insert(tk.END, msg + "\n")
        self.text_output.see(tk.END)

    def load_dialogs(self):
        files = filedialog.askopenfilenames(title="Transkriptdateien auswählen", filetypes=[("Textdateien", "*.txt")])
        if files:
            self.dialog_files = list(files)
            self.log(f"{len(self.dialog_files)} Dateien geladen.")

    def run_processing(self):
        if not self.dialog_files:
            messagebox.showwarning("Warnung", "Keine Dateien ausgewählt.")
            return
        self.log("Starte Verarbeitung...")
        self.processed_data = process_multiple_dialogs(self.dialog_files)
        self.log("Verarbeitung abgeschlossen.")
        self.log(f"Kategorien: {set(self.processed_data['terminal_chain'])}")

    def run_simulation(self):
        if not self.processed_data:
            messagebox.showwarning("Warnung", "Bitte zuerst Transkripte verarbeiten.")
            return
        chain = simulate_dialog(self.processed_data["pcfg"], length=6)
        self.log("Simulierter Dialog:")
        self.log(" → ".join(chain))

    def export_pcfg(self, fmt):
        if not self.processed_data:
            messagebox.showwarning("Warnung", "Bitte zuerst Transkripte verarbeiten.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=[(fmt.upper(), f"*.{fmt}")])
        if filepath:
            if fmt == "json":
                export_pcfg_to_json(self.processed_data["pcfg"], filepath)
            elif fmt == "csv":
                export_pcfg_to_csv(self.processed_data["pcfg"], filepath)
            elif fmt == "yaml":
                export_pcfg_to_yaml(self.processed_data["pcfg"], filepath)
            self.log(f"PCFG exportiert als {filepath}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ARSGUIApp(root)
    root.mainloop()

