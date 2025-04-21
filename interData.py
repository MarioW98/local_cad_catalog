import tkinter as tk
from tkinter import messagebox, ttk
import os # Aggiunto
import subprocess # Aggiunto
import sys # Aggiunto

from database import *


class GestoreComponentiGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gestore Componenti")
        self.database = load_database()

        self.crea_interfaccia_principale()
    def apri_file_info(self):
        """Apre il file messaggio.txt con l'applicazione predefinita."""
        file_path = "messaggio.txt" # Assicurati che questo percorso sia corretto
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin": # macOS
                subprocess.call(["open", file_path])
            else: # linux variants
                subprocess.call(["xdg-open", file_path])
        except FileNotFoundError:
            messagebox.showerror("Errore", f"File non trovato: {file_path}\nAssicurati che il file esista nella directory corretta.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")

    def mostra_info(self, titolo, messaggio):
        """Mostra una finestra informativa con titolo e messaggio."""
        # Questo metodo rimane, potrebbe servire altrove
        messagebox.showinfo(titolo, messaggio)

    def crea_interfaccia_principale(self):
        """Crea l'interfaccia principale con i bottoni per le azioni."""
        btn_aggiungi = ttk.Button(self.master, text="Aggiungi Componente", command=self.apri_finestra_aggiungi)
        btn_aggiungi.pack(pady=10)

        btn_visualizza = ttk.Button(self.master, text="Visualizza Componente", command=self.apri_finestra_visualizza)
        btn_visualizza.pack(pady=10)

        btn_elenca = ttk.Button(self.master, text="Elenca Componenti", command=self.apri_finestra_elenca)
        btn_elenca.pack(pady=10)

    def apri_finestra_aggiungi(self):
        """Apre una finestra per aggiungere un nuovo componente."""
        aggiungi_finestra = tk.Toplevel(self.master)
        aggiungi_finestra.title("Aggiungi Nuovo Componente")

        tk.Label(aggiungi_finestra, text="Codice:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_codice_aggiungi = ttk.Entry(aggiungi_finestra)
        self.entry_codice_aggiungi.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(aggiungi_finestra, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nome_aggiungi = ttk.Entry(aggiungi_finestra)
        self.entry_nome_aggiungi.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(aggiungi_finestra, text="Descrizione:").grid(row=2, column=0, padx=5, pady=5)
        self.text_descrizione_aggiungi = tk.Text(aggiungi_finestra, height=3, width=30)
        self.text_descrizione_aggiungi.grid(row=2, column=1, padx=5, pady=5)

        # --- Modifica per Tipologia ---
        tk.Label(aggiungi_finestra, text="Tipologia:").grid(row=3, column=0, padx=5, pady=5)
        # Estrai le tipologie uniche esistenti dal database
        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente")))) # Filtra valori vuoti/None
        self.combo_tipologia_aggiungi = ttk.Combobox(aggiungi_finestra, values=tipologie_esistenti)
        self.combo_tipologia_aggiungi.grid(row=3, column=1, padx=5, pady=5, sticky="ew") # sticky="ew" per allargare
        # --- Fine Modifica ---

        tk.Label(aggiungi_finestra, text="Link (opzionale):").grid(row=4, column=0, padx=5, pady=5)
        self.entry_link_aggiungi = ttk.Entry(aggiungi_finestra)
        self.entry_link_aggiungi.grid(row=4, column=1, padx=5, pady=5)

        btn_salva = ttk.Button(aggiungi_finestra, text="Salva Componente", command=self.salva_nuovo_componente)
        btn_salva.grid(row=5, column=0, columnspan=2, pady=10)

    def salva_nuovo_componente(self):
        """Salva un nuovo componente nel database."""
        codice = self.entry_codice_aggiungi.get().strip().upper()
        if not codice: # Aggiunto controllo per codice vuoto
             messagebox.showerror("Errore", "Il codice non può essere vuoto.")
             return
        if codice in self.database:
            messagebox.showerror("Errore", f"Il codice '{codice}' esiste già.")
            return

        nome = self.entry_nome_aggiungi.get().strip()
        descrizione = self.text_descrizione_aggiungi.get("1.0", tk.END).strip()
        # --- Modifica per leggere dal Combobox ---
        tipologia = self.combo_tipologia_aggiungi.get().strip()
        # --- Fine Modifica ---
        link = self.entry_link_aggiungi.get().strip() or None

        # Aggiunto controllo per campi obbligatori (es. Nome, Tipologia) se necessario
        if not nome:
            messagebox.showerror("Errore", "Il nome non può essere vuoto.")
            return
        if not tipologia:
             messagebox.showerror("Errore", "La tipologia non può essere vuota.")
             return

        self.database[codice] = {
            "Nome": nome,
            "Descrizione": descrizione,
            "Componenti che lo compongono": [],
            "Componenti che lo usano": [],
            "Tipologia di Componente": tipologia,
            "Link al componente per il download": link
        }
        save_database(self.database)
        messagebox.showinfo("Successo", f"Componente '{nome}' con codice '{codice}' aggiunto.")
        self.entry_codice_aggiungi.delete(0, tk.END)
        self.entry_nome_aggiungi.delete(0, tk.END)
        self.text_descrizione_aggiungi.delete("1.0", tk.END)
        # --- Modifica per pulire il Combobox ---
        self.combo_tipologia_aggiungi.set('') # Pulisce il valore selezionato/inserito
        # Aggiorna anche i valori del combobox nel caso sia stata inserita una nuova tipologia
        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente"))))
        self.combo_tipologia_aggiungi['values'] = tipologie_esistenti
        # --- Fine Modifica ---
        self.entry_link_aggiungi.delete(0, tk.END)

    def apri_finestra_visualizza(self):
        """Apre una finestra per visualizzare i dettagli di un componente."""
        visualizza_finestra = tk.Toplevel(self.master)
        visualizza_finestra.title("Visualizza Componente")

        tk.Label(visualizza_finestra, text="Inserisci il codice del componente:").pack(pady=5)
        self.entry_codice_visualizza = ttk.Entry(visualizza_finestra)
        self.entry_codice_visualizza.pack(pady=5)

        btn_cerca = ttk.Button(visualizza_finestra, text="Cerca", command=self.mostra_dettagli_componente)
        btn_cerca.pack(pady=10)

        self.text_dettagli = tk.Text(visualizza_finestra, height=10, width=40)
        self.text_dettagli.pack(padx=5, pady=5)
        self.text_dettagli.config(state=tk.DISABLED) # Rende il text widget di sola lettura

    def mostra_dettagli_componente(self):
        """Mostra i dettagli del componente nel text widget."""
        codice = self.entry_codice_visualizza.get().strip().upper()
        self.text_dettagli.config(state=tk.NORMAL) # Abilita la modifica temporaneamente
        self.text_dettagli.delete("1.0", tk.END) # Pulisce il text widget
        if codice in self.database:
            componente = self.database[codice]
            dettagli = f"Codice: {codice}\n"
            for chiave, valore in componente.items():
                dettagli += f"{chiave}: {valore}\n"
            self.text_dettagli.insert(tk.END, dettagli)
        else:
            self.text_dettagli.insert(tk.END, f"Errore: Il codice '{codice}' non trovato.")
        self.text_dettagli.config(state=tk.DISABLED) # Riabilita la sola lettura

    def mostra_dettagli_da_lista(self):
        """Mostra i dettagli del componente selezionato dalla lista."""
        selected_iid = self.tree_componenti.focus() # Ottiene l'iid dell'item selezionato
        if not selected_iid:
            messagebox.showinfo("Attenzione", "Seleziona un componente dalla tabella per vederne i dettagli.")
            return

        codice = selected_iid # L'iid corrisponde al codice del componente
        if codice in self.database:
            componente = self.database[codice]
            dettagli_str = f"Dettagli Componente - Codice: {codice}\n\n"
            for chiave, valore in componente.items():
                # Formatta liste in modo più leggibile
                if isinstance(valore, list):
                    valore_str = ", ".join(valore) if valore else "Nessuno"
                else:
                    valore_str = valore if valore is not None else "N/D"
                dettagli_str += f"{chiave}: {valore_str}\n"

            # Mostra i dettagli in una finestra di messaggio
            messagebox.showinfo(f"Dettagli - {componente.get('Nome', codice)}", dettagli_str)
        else:
            messagebox.showerror("Errore", f"Il codice '{codice}' non trovato nel database.")
            # Potrebbe essere utile ricaricare la vista se c'è discrepanza
            try:
                self.tree_componenti.delete(selected_iid)
            except tk.TclError:
                pass # L'elemento potrebbe essere già stato rimosso

    def apri_finestra_elenca(self):
        """Apre una finestra per elencare e rimuovere i componenti in una tabella."""
        elenca_finestra = tk.Toplevel(self.master)
        elenca_finestra.title("Elenco Componenti")
        elenca_finestra.geometry("600x400")

        # Frame per il Treeview
        tree_frame = ttk.Frame(elenca_finestra)
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar per il Treeview
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Crea il Treeview
        columns = ("Codice", "Nome", "Tipologia")
        self.tree_componenti = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_componenti.yview)

        # Definisci gli header
        self.tree_componenti.heading("Codice", text="Codice")
        self.tree_componenti.heading("Nome", text="Nome")
        self.tree_componenti.heading("Tipologia", text="Tipologia")
        self.tree_componenti.column("Codice", width=100, anchor=tk.W)
        self.tree_componenti.column("Nome", width=250, anchor=tk.W)
        self.tree_componenti.column("Tipologia", width=150, anchor=tk.W)

        # Popola il Treeview con i dati
        if self.database:
            # Svuota prima di ripopolare (se la finestra può essere riaperta)
            for i in self.tree_componenti.get_children():
                self.tree_componenti.delete(i)
            # Popola
            for codice, dettagli in sorted(self.database.items()): # Ordina per codice
                nome = dettagli.get('Nome', 'N/A')
                tipologia = dettagli.get('Tipologia di Componente', 'N/A')
                self.tree_componenti.insert("", tk.END, values=(codice, nome, tipologia), iid=codice) # Usa codice come iid
        else:
             pass # Tabella vuota

        self.tree_componenti.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame per i bottoni in basso
        button_frame = ttk.Frame(elenca_finestra)
        button_frame.pack(pady=10, fill=tk.X, padx=10)

        btn_rimuovi_selezionato = ttk.Button(button_frame, text="Rimuovi Selezionato", command=self.rimuovi_componente_da_lista)
        btn_rimuovi_selezionato.pack(side=tk.LEFT, padx=5)

        btn_mostra_dettagli = ttk.Button(button_frame, text="Mostra Dettagli", command=self.mostra_dettagli_da_lista)
        btn_mostra_dettagli.pack(side=tk.LEFT, padx=5)

        # --- Modifica Bottone Info ---
        # Ora chiama il nuovo metodo per aprire il file
        btn_info = ttk.Button(button_frame, text="Info", command=self.apri_file_info)
        # --- Fine Modifica ---
        btn_info.pack(side=tk.LEFT, padx=5)


    def rimuovi_componente_da_lista(self):
        """Rimuove il componente selezionato dalla tabella."""
        selected_iid = self.tree_componenti.focus() # Ottiene l'iid dell'item selezionato
        if selected_iid:
            # Non è più necessario estrarre dai 'values' se usiamo l'iid come codice
            codice = selected_iid

            risposta = messagebox.askyesno("Conferma", f"Sei sicuro di voler rimuovere il componente con codice '{codice}'?")
            if risposta:
                if codice in self.database:
                    # Rimuovi anche dai componenti che lo usano/compongono altri
                    componente_da_rimuovere = self.database[codice]
                    componenti_che_lo_compongono = componente_da_rimuovere.get("Componenti che lo compongono", [])
                    componenti_che_lo_usano = componente_da_rimuovere.get("Componenti che lo usano", [])

                    # Rimuovi riferimenti da altri componenti
                    for comp_codice in list(componenti_che_lo_compongono): # Itera su una copia
                        if comp_codice in self.database and codice in self.database[comp_codice].get("Componenti che lo usano", []):
                            self.database[comp_codice]["Componenti che lo usano"].remove(codice)
                    for comp_codice in list(componenti_che_lo_usano): # Itera su una copia
                         if comp_codice in self.database and codice in self.database[comp_codice].get("Componenti che lo compongono", []):
                            self.database[comp_codice]["Componenti che lo compongono"].remove(codice)

                    # Rimuovi il componente stesso
                    del self.database[codice]
                    save_database(self.database)
                    messagebox.showinfo("Successo", f"Componente con codice '{codice}' rimosso.")

                    # Rimuovi l'item dal Treeview usando l'iid
                    self.tree_componenti.delete(selected_iid)
                else:
                    messagebox.showerror("Errore", f"Il codice '{codice}' non trovato nel database (potrebbe essere stato rimosso).")
                    # Potrebbe essere utile ricaricare la vista se c'è discrepanza
                    self.tree_componenti.delete(selected_item) # Rimuovi comunque dalla vista
        else:
            messagebox.showinfo("Attenzione", "Seleziona un componente dalla tabella per rimuoverlo.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GestoreComponentiGUI(root)
    root.mainloop()