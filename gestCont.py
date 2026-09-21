from customtkinter import *
import customtkinter
from PIL import Image

# Inizializzazione della finestra principale di CustomTkinter
app1 = CTk()
app1._set_appearance_mode('dark')
customtkinter.set_default_color_theme("dark-blue")
app1.title("Gestore Contatori")
app1.iconbitmap("assets/icon_titleBar.ico")

bg_img1 = CTkImage(Image.open("assets/no_bg_logo.png"), size=(304, 80))

lbl_img = CTkLabel(master=app1, image=bg_img1, text='')
lbl_img.pack(fill=BOTH, expand=True)

# Definisce Dimensione Finestra
w_px = 870
h_px = 350
# Ottieni Dimensioni Schermo
screen_width = app1.winfo_screenwidth()
screen_height = app1.winfo_screenheight()
# Calcola Posizione X & Y per Centrare Finestra
x = int((screen_width / 2) - (w_px / 2))
y = int((screen_height / 2) - (h_px / 2))
# Imposta Geometria Finestra
app1.geometry(f"{w_px}x{h_px}+{x}+{y}")

# Dizionario Importi Postazioni
importi_postazioni = {
    "PC": 0.2,
    "VR": 0.3,
    "Simulatori": 0.4
}

# Lista globale per tenere traccia di tutti i cronometri.
# Ogni elemento della lista sarà un dizionario che rappresenta un singolo cronometro.
cronometri_data = []

def nuovo_cronometro():
    """Crea un nuovo cronometro con il suo campo nome utente e display del tempo."""
    nCronom = len(cronometri_data) + 1

    # Dizionario che conterrà tutti i dati e i riferimenti ai widget di questo specifico cronometro.
    cronometro_info = {
        "nCronom": nCronom,
        "secs": 0,
        "mins": 0,
        "hrs": 0,
        "is_running": False,
        "after_id": None, # Per memorizzare l'ID delle chiamate after
        "frame": None,
        "entry_nome_utente": None, # CTkEntry per il nome utente
        "label_tempo_cronometro": None, # CTkLabel per il display del tempo
        "tastoAvvio": None,
        "tastoReset": None,
        "tastoRimuovi": None,
        "label_calcolo_importo": None, # Aggiunto per mostrare il calcolo dell'importo
        "importo_barra": None, # Riferimento all'Entry per l'importo
    }

    def updater(current_cronometro_info):
        """Aggiorna il display del cronometro ogni secondo e cambia colore."""
        if current_cronometro_info["is_running"]:
            current_cronometro_info["secs"] += 1
            if current_cronometro_info["secs"] == 60:
                current_cronometro_info["secs"] = 0
                current_cronometro_info["mins"] += 1
                if current_cronometro_info["mins"] == 60:
                    current_cronometro_info["mins"] = 0
                    current_cronometro_info["hrs"] += 1

            # Formattazione del testo del cronometro
            display_time_text = (
                f"{current_cronometro_info['hrs']:02d}:"
                f"{current_cronometro_info['mins']:02d}:"
                f"{current_cronometro_info['secs']:02d}"
            )
            
            # Calcola i minuti totali per la logica del colore
            total_minutes = (current_cronometro_info["hrs"] * 60) + current_cronometro_info["mins"]

            # Logica per cambiare il colore del testo del cronometro
            if total_minutes < 30:
                color = "green"
            elif 30 <= total_minutes < 60:
                color = "orange"
            else: # total_minutes >= 60
                color = "red"

            # Aggiornamento della CTkLabel del tempo e del suo colore
            current_cronometro_info["label_tempo_cronometro"].configure(text=display_time_text, text_color=color)
            
            current_cronometro_info["after_id"] = app1.after(
                1000, updater, current_cronometro_info
            )

    def avvio_pausa(current_cronometro_info):
        """Gestisce AVVIO, PAUSA e RIPRENDI col tasto singolo."""
        if not current_cronometro_info["is_running"]:
            # Se era in pausa o mai avviato → avvia/riprende
            current_cronometro_info["is_running"] = True
            updater(current_cronometro_info)
            current_cronometro_info["tastoAvvio"].configure(text="PAUSA")
            current_cronometro_info["tastoReset"].configure(state="normal")
            current_cronometro_info["entry_nome_utente"].configure(state="readonly")
        else:
            # Se era in esecuzione → metti in pausa
            current_cronometro_info["is_running"] = False
            if current_cronometro_info["after_id"]:
                app1.after_cancel(current_cronometro_info["after_id"])
            current_cronometro_info["tastoAvvio"].configure(text="RIPRENDI")
            current_cronometro_info["entry_nome_utente"].configure(state="normal")


    def reset(current_cronometro_info):
        """Resetta il cronometro."""
        if current_cronometro_info["is_running"]:
            current_cronometro_info["is_running"] = False
            if current_cronometro_info["after_id"]:
                app1.after_cancel(current_cronometro_info["after_id"])

        current_cronometro_info["secs"] = 0
        current_cronometro_info["mins"] = 0
        current_cronometro_info["hrs"] = 0
        reset_time_text = "00:00:00"
        
        # Aggiornamento della CTkLabel del tempo dopo il reset (colore iniziale)
        current_cronometro_info["label_tempo_cronometro"].configure(text=reset_time_text, text_color="white")
        current_cronometro_info["label_calcolo_importo"].configure(text="") # Resetta anche il campo dell'importo
        current_cronometro_info["tastoAvvio"].configure(state="normal", text="AVVIA")
        current_cronometro_info["tastoReset"].configure(state="disabled")
        # Riabilita l'editing del nome utente dopo il reset
        current_cronometro_info["entry_nome_utente"].configure(state="normal")

    def rimuovi(current_cronometro_info):
        """Rimuove il cronometro dall'interfaccia e dalla lista."""
        if current_cronometro_info["is_running"] and current_cronometro_info["after_id"]:
            app1.after_cancel(current_cronometro_info["after_id"])
        
        current_cronometro_info["frame"].destroy()
        cronometri_data.remove(current_cronometro_info)
        
    def calcola_importo_basato_su_tempo(current_cronometro_info):
        """
        Calcola l'importo totale in base al tempo trascorso, utilizzando
        il valore selezionato in 'menu_importi_postazione' come costo al minuto.
        """
        try:
            # Ottieni la postazione scelta dal menu
            postazione_scelta = current_cronometro_info["menu_importi_postazione"].get()
            costo_al_minuto = importi_postazioni.get(postazione_scelta, 0.0)

            # Calcola i minuti totali (ore * 60 + minuti + secondi / 60)
            total_minutes = (current_cronometro_info["hrs"] * 60) + \
                            current_cronometro_info["mins"] + \
                            (current_cronometro_info["secs"] / 60.0)

            risultato = total_minutes * costo_al_minuto
            current_cronometro_info["label_calcolo_importo"].configure(text=f"€{risultato:.2f}")
        except Exception as e:
            current_cronometro_info["label_calcolo_importo"].configure(text=f"Errore: {e}")

    # Creazione del frame per questo specifico cronometro
    cronometro_frame = CTkFrame(master=cronometri_scroll_frame)
    cronometro_frame.pack(pady=5, padx=5, fill="x", anchor="w")
    cronometro_info["frame"] = cronometro_frame

    # CTkEntry per il nome utente
    entry_nome = CTkEntry(
        master=cronometro_frame,
        placeholder_text="Nome...", # Testo segnaposto
        font=CTkFont('Comic Sans MS'),
        text_color="white",
        corner_radius=10,
        justify="left"
    )
    entry_nome.pack(side="left", padx=5, pady=5)
    cronometro_info["entry_nome_utente"] = entry_nome

    # CTkLabel per il display del tempo del cronometro
    label_tempo = CTkLabel(
        master=cronometro_frame,
        text="00:00:00", # Testo iniziale
        font=CTkFont('Comic Sans MS'),
        text_color="white" # Colore iniziale del testo
    )
    label_tempo.pack(side="left", padx=5, pady=5)
    cronometro_info["label_tempo_cronometro"] = label_tempo

    # Creazione dei bottoni e assegnazione delle funzioni con il passaggio del dizionario
    tastoAvvio = CTkButton(
        master=cronometro_frame,
        text="AVVIA",
        fg_color="#A00000",
        font=CTkFont('Comic Sans MS'),
        command=lambda: avvio_pausa(cronometro_info),
        width=90,
        corner_radius=10
    )
    tastoAvvio.pack(side="left", padx=5, pady=5)
    cronometro_info["tastoAvvio"] = tastoAvvio
    
    tastoReset = CTkButton(
        master=cronometro_frame,
        text="RESET",
        fg_color="#A00000",
        font=CTkFont('Comic Sans MS'),
        command=lambda: reset(cronometro_info),
        state="disabled",
        corner_radius=10,
        width=90
    )
    tastoReset.pack(side="left", padx=5, pady=5)
    cronometro_info["tastoReset"] = tastoReset

    tastoRimuovi = CTkButton(
        master=cronometro_frame,
        text="RIMUOVI",
        fg_color="#A00000",
        font=CTkFont('Comic Sans MS'),
        command=lambda: rimuovi(cronometro_info),
        corner_radius=10,
        width=90
    )
    tastoRimuovi.pack(side="left", padx=5, pady=5)
    cronometro_info["tastoRimuovi"] = tastoRimuovi
    
    # Per Sostituire l'Entry
    menu_importi_postazione = CTkOptionMenu(
        master=cronometro_frame,
        values=list(importi_postazioni.keys()),
        fg_color="#A00000",
        font=CTkFont('Comic Sans MS'),
        corner_radius=10
    )
    menu_importi_postazione.pack(side="left", padx=5, pady=5)
    cronometro_info["menu_importi_postazione"] = menu_importi_postazione

    tasto_calcola = CTkButton(
        master=cronometro_frame,
        text="CALCOLA",
        fg_color="#A00000",
        font=CTkFont('Comic Sans MS'),
        command=lambda: calcola_importo_basato_su_tempo(cronometro_info), # Collega alla funzione di calcolo
        corner_radius=10,
        width=90
    )
    tasto_calcola.pack(side="left", padx=5, pady=5)
    
    label_calcolo = CTkLabel(
        master=cronometro_frame,
        text="", # Testo iniziale vuoto
        font=CTkFont('Comic Sans MS'),
        text_color="white"
    )
    label_calcolo.pack(side="left", padx=5, pady=5)
    cronometro_info["label_calcolo_importo"] = label_calcolo # Memorizza il riferimento

    cronometri_data.append(cronometro_info)

# Bottone per aggiungere un nuovo cronometro
add_button = CTkButton(master=app1,
                       text="NUOVO",
                       fg_color="#A00000",
                       font=CTkFont('Comic Sans MS'),
                       command=nuovo_cronometro,
                       corner_radius=10)
add_button.pack(pady=10)

# Sposto la definizione del cronometri_scroll_frame qui, prima che venga usato.
cronometri_scroll_frame = CTkScrollableFrame(master=app1, width=750, height=400)
# Usa 'anchor="nw"' per allineare il contenuto in alto a sinistra del frame.
cronometri_scroll_frame.pack(pady=10, padx=(10), fill="both", expand=True, anchor="nw")

app1.mainloop()
