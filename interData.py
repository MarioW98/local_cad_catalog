import tkinter as tk
from tkinter import messagebox, ttk
import os # Aggiunto
import subprocess # Aggiunto
import sys # Aggiunto

from database import *


class GestoreComponentiGUI:
    def __init__(self, master):
        self.master = master
        master.title("Componenti")
        self.database = load_database()

        self.crea_interfaccia_principale()
    def apri_file_info(self):
        
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

    def crea_interfaccia_principale(self):
        
        btn_aggiungi = ttk.Button(self.master, text="Aggiungi Componente", command=self.apri_finestra_aggiungi)
        btn_aggiungi.pack(pady=10)

        btn_visualizza = ttk.Button(self.master, text="Visualizza Componente", command=self.apri_finestra_visualizza)
        btn_visualizza.pack(pady=10)

        btn_elenca = ttk.Button(self.master, text="Elenca Componenti", command=self.apri_finestra_elenca)
        btn_elenca.pack(pady=10)

    def apri_finestra_aggiungi(self):
        #nuovo componente
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

        tk.Label(aggiungi_finestra, text="Tipologia:").grid(row=3, column=0, padx=5, pady=5)

        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente")))) # Filtra valori vuoti/None
        self.combo_tipologia_aggiungi = ttk.Combobox(aggiungi_finestra, values=tipologie_esistenti)
        self.combo_tipologia_aggiungi.grid(row=3, column=1, padx=5, pady=5, sticky="ew") # sticky="ew" per allargare


        tk.Label(aggiungi_finestra, text="Link (opzionale):").grid(row=4, column=0, padx=5, pady=5)
        self.entry_link_aggiungi = ttk.Entry(aggiungi_finestra)
        self.entry_link_aggiungi.grid(row=4, column=1, padx=5, pady=5)

        btn_salva = ttk.Button(aggiungi_finestra, text="Salva Componente", command=self.salva_nuovo_componente)
        btn_salva.grid(row=5, column=0, columnspan=2, pady=10)

    def salva_nuovo_componente(self):
        #salvataggio nuovo componente 
        codice = self.entry_codice_aggiungi.get().strip().upper()
        if not codice: # il codice non può essere vuoto
             messagebox.showerror("Errore", "Il codice non può essere vuoto.")
             return
        if codice in self.database:
            messagebox.showerror("Errore", f"Il codice '{codice}' esiste già.")
            return

        nome = self.entry_nome_aggiungi.get().strip()
        descrizione = self.text_descrizione_aggiungi.get("1.0", tk.END).strip()
        tipologia = self.combo_tipologia_aggiungi.get().strip()
        link = self.entry_link_aggiungi.get().strip() or None

        # campi obbligatori
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

        self.combo_tipologia_aggiungi.set('') # Pulisce il valore selezionato/inserito

        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente"))))
        self.combo_tipologia_aggiungi['values'] = tipologie_esistenti

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

        codice = selected_iid
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

        tree_frame = ttk.Frame(elenca_finestra)
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("Codice", "Nome", "Tipologia")
        self.tree_componenti = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_componenti.yview)

        self.tree_componenti.heading("Codice", text="Codice")
        self.tree_componenti.heading("Nome", text="Nome")
        self.tree_componenti.heading("Tipologia", text="Tipologia")
        self.tree_componenti.column("Codice", width=100, anchor=tk.W)
        self.tree_componenti.column("Nome", width=250, anchor=tk.W)
        self.tree_componenti.column("Tipologia", width=150, anchor=tk.W)

        if self.database:
            for i in self.tree_componenti.get_children():
                self.tree_componenti.delete(i)
            for codice, dettagli in sorted(self.database.items()): # Ordina per codice
                nome = dettagli.get('Nome', 'N/A')
                tipologia = dettagli.get('Tipologia di Componente', 'N/A')
                self.tree_componenti.insert("", tk.END, values=(codice, nome, tipologia), iid=codice) # Usa codice come iid
        else:
             pass # Tabella vuota

        self.tree_componenti.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(elenca_finestra)
        button_frame.pack(pady=10, fill=tk.X, padx=10)

        btn_rimuovi_selezionato = ttk.Button(button_frame, text="Rimuovi Selezionato", command=self.rimuovi_componente_da_lista)
        btn_rimuovi_selezionato.pack(side=tk.LEFT, padx=5)

        btn_mostra_dettagli = ttk.Button(button_frame, text="Mostra Dettagli", command=self.mostra_dettagli_da_lista)
        btn_mostra_dettagli.pack(side=tk.LEFT, padx=5)

        btn_modifica_selezionato = ttk.Button(button_frame, text="Modifica Selezionato", command=self.apri_finestra_modifica)
        btn_modifica_selezionato.pack(side=tk.LEFT, padx=5)

        btn_info = ttk.Button(button_frame, text="Info", command=self.apri_file_info)
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

    def apri_finestra_modifica(self):
        """Apre una finestra per modificare il componente selezionato."""
        selected_iid = self.tree_componenti.focus()
        if not selected_iid:
            messagebox.showinfo("Attenzione", "Seleziona un componente dalla tabella per modificarlo.")
            return

        codice = selected_iid
        if codice not in self.database:
            messagebox.showerror("Errore", f"Componente con codice '{codice}' non trovato. Potrebbe essere stato rimosso.")
            # Rimuovi dalla vista se non esiste più
            try:
                self.tree_componenti.delete(selected_iid)
            except tk.TclError:
                pass
            return

        componente = self.database[codice]

        # Crea la finestra di modifica (simile a quella di aggiunta)
        modifica_finestra = tk.Toplevel(self.master)
        modifica_finestra.title(f"Modifica Componente - {codice}")

        # Campi (Codice è read-only)
        tk.Label(modifica_finestra, text="Codice:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(modifica_finestra, text=codice).grid(row=0, column=1, padx=5, pady=5, sticky="w") # Mostra codice come label

        tk.Label(modifica_finestra, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_nome_modifica = ttk.Entry(modifica_finestra, width=30)
        entry_nome_modifica.grid(row=1, column=1, padx=5, pady=5)
        entry_nome_modifica.insert(0, componente.get("Nome", ""))

        tk.Label(modifica_finestra, text="Descrizione:").grid(row=2, column=0, padx=5, pady=5, sticky="nw") # sticky nw per allineare label in alto
        text_descrizione_modifica = tk.Text(modifica_finestra, height=3, width=30)
        text_descrizione_modifica.grid(row=2, column=1, padx=5, pady=5)
        text_descrizione_modifica.insert("1.0", componente.get("Descrizione", ""))

        tk.Label(modifica_finestra, text="Tipologia:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente"))))
        combo_tipologia_modifica = ttk.Combobox(modifica_finestra, values=tipologie_esistenti, width=28)
        combo_tipologia_modifica.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        combo_tipologia_modifica.set(componente.get("Tipologia di Componente", ""))

        tk.Label(modifica_finestra, text="Link:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        entry_link_modifica = ttk.Entry(modifica_finestra, width=30)
        entry_link_modifica.grid(row=4, column=1, padx=5, pady=5)
        entry_link_modifica.insert(0, componente.get("Link al componente per il download", "") or "") # Gestisce None

        # Bottone Salva Modifiche
        # Passiamo i widget e il codice alla funzione salva
        btn_salva_modifiche = ttk.Button(modifica_finestra, text="Salva Modifiche",
                                         command=lambda: self.salva_modifiche_componente(
                                             codice,
                                             entry_nome_modifica,
                                             text_descrizione_modifica,
                                             combo_tipologia_modifica,
                                             entry_link_modifica,
                                             modifica_finestra # Passa la finestra per chiuderla
                                         ))
        btn_salva_modifiche.grid(row=5, column=0, columnspan=2, pady=10)

    # --- Fine Modifica ---
        self.combo_tipologia_aggiungi.set('') # Pulisce il valore selezionato/inserito

        tipologie_esistenti = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                             for dettagli in self.database.values()
                                             if dettagli.get("Tipologia di Componente"))))
        self.combo_tipologia_aggiungi['values'] = tipologie_esistenti
        # --- Fine Modifica ---
        self.entry_link_aggiungi.delete(0, tk.END)

    def salva_modifiche_componente(self, codice, entry_nome, text_descrizione, combo_tipologia, entry_link, finestra):
        """Salva le modifiche apportate a un componente."""
        nome = entry_nome.get().strip()
        descrizione = text_descrizione.get("1.0", tk.END).strip()
        tipologia = combo_tipologia.get().strip()
        link = entry_link.get().strip() or None

        # Validazione campi obbligatori
        if not nome:
            messagebox.showerror("Errore", "Il nome non può essere vuoto.", parent=finestra) # parent per mostrare sopra la finestra modale
            return
        if not tipologia:
             messagebox.showerror("Errore", "La tipologia non può essere vuota.", parent=finestra)
             return

        # Aggiorna il database
        if codice in self.database:
            self.database[codice]["Nome"] = nome
            self.database[codice]["Descrizione"] = descrizione
            self.database[codice]["Tipologia di Componente"] = tipologia
            self.database[codice]["Link al componente per il download"] = link
            save_database(self.database)

            # Aggiorna la riga nel Treeview nella finestra Elenca
            self.tree_componenti.item(codice, values=(codice, nome, tipologia))

            # Aggiorna le tipologie disponibili nel Combobox Aggiungi (se aperto o alla prossima apertura)
            tipologie_esistenti_aggiornate = sorted(list(set(dettagli.get("Tipologia di Componente", "")
                                                          for dettagli in self.database.values()
                                                          if dettagli.get("Tipologia di Componente"))))
            # Se la finestra aggiungi è stata creata, aggiorna il suo combobox
            if hasattr(self, 'combo_tipologia_aggiungi') and self.combo_tipologia_aggiungi.winfo_exists():
                 self.combo_tipologia_aggiungi['values'] = tipologie_esistenti_aggiornate
            # Aggiorna anche il combobox della finestra di modifica stessa (se si vuole aggiungere un'altra tipologia e salvare di nuovo)
            if combo_tipologia.winfo_exists():
                 combo_tipologia['values'] = tipologie_esistenti_aggiornate


            messagebox.showinfo("Successo", f"Componente '{nome}' (Codice: {codice}) aggiornato.", parent=finestra)
            finestra.destroy() # Chiude la finestra di modifica
        else:
             messagebox.showerror("Errore", f"Errore durante il salvataggio: Componente con codice '{codice}' non trovato.", parent=finestra)

if __name__ == "__main__":
    root = tk.Tk()
    app = GestoreComponentiGUI(root)
    root.mainloop()