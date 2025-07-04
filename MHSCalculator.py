""" import os

# Funzione per caricare il file .matrix e separare la parte dei commenti dalla matrice
def load_matrix_file(file_path):
    comments = []
    matrix_data = []
    is_matrix_section = False

    with open(file_path, 'r') as file:
        for line in file:
            # Aggiungi le righe di commento
            if line.startswith(";;;"):
                comments.append(line.strip())
            # Una volta incontrata la matrice, inizia a leggere i dati della matrice
            elif line.startswith("0") or line.startswith("1") or '-' in line:
                is_matrix_section = True
                if is_matrix_section:
                    matrix_data.append(line.strip())
    
    return comments, matrix_data

# Funzione per calcolare gli MHS dalla matrice
def calculate_mhs(matrix_data):
    # Elaborazione della matrice: ogni riga rappresenta un MHS
    # In questo esempio, ritorniamo semplicemente tutte le righe della matrice come MHS
    mhs = [line.split() for line in matrix_data if '-' not in line]
    return mhs

# Funzione per generare il riassunto
def generate_summary(matrix_data, mhs):
    # Cardinalità di M (numero di colonne)
    num_columns = len(matrix_data[0].split())
    # Cardinalità di N (numero di righe)
    num_rows = len(matrix_data)

    # La cardinalità minima e massima di un MHS è 1 e il numero di colonne
    min_cardinality = 1
    max_cardinality = num_columns

    # Numero totale di MHS
    total_mhs = len(mhs)

    summary = {
        "matrix_dimensions": (num_rows, num_columns),
        "total_mhs": total_mhs,
        "min_cardinality": min_cardinality,
        "max_cardinality": max_cardinality,
    }

    return summary

# Funzione per scrivere l'output nel file .mhs
def write_mhs_output(output_folder, file_name, comments, mhs, summary):
    # Creazione della cartella di output se non esiste
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Definisci il percorso completo del file di output
    output_file = os.path.join(output_folder, file_name.replace('.matrix', '.mhs'))

    with open(output_file, 'w') as file:
        # Scriviamo i commenti
        for comment in comments:
            file.write(f"{comment}\n")
        
        # Scriviamo il riassunto come commento
        file.write(f";;; Matrix dimensions: {summary['matrix_dimensions']}\n")
        file.write(f";;; Total MHS found: {summary['total_mhs']}\n")
        file.write(f";;; Min Cardinality: {summary['min_cardinality']}\n")
        file.write(f";;; Max Cardinality: {summary['max_cardinality']}\n")

        # Scriviamo gli MHS
        for mhs_row in mhs:
            file.write(" ".join(mhs_row) + "\n")
    
    print(f"Output written to {output_file}")

# Funzione principale
def process_matrix_file(file_path, output_folder='output'):
    # Carica il file
    comments, matrix_data = load_matrix_file(file_path)
    
    # Calcola gli MHS dalla matrice
    mhs = calculate_mhs(matrix_data)
    
    # Genera il riassunto
    summary = generate_summary(matrix_data, mhs)
    
    # Scrivi l'output nel file .mhs
    write_mhs_output(output_folder, os.path.basename(file_path), comments, mhs, summary)
 """

import os
import sys
import tkinter as tk
from tkinter import filedialog
import threading
import time

# Funzione per selezionare la cartella contenente i file .matrix
def select_directory():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale di Tkinter
    folder_selected = filedialog.askdirectory(title="Seleziona la cartella contenente i file .matrix")
    root.quit()  # Distrugge la finestra di Tkinter
    return folder_selected

# Funzione per elaborare un singolo file .matrix e generare il file .mhs
def process_matrix_file(matrix_file_path, output_folder, timeout_event):
    with open(matrix_file_path, 'r') as matrix_file:
        lines = matrix_file.readlines()

    matrix_data = []
    for line in lines:
        if line.strip() and not line.startswith(";;;"):
            matrix_data.append(line.strip().split())

    num_rows = len(matrix_data)
    num_cols = len(matrix_data[0]) if num_rows > 0 else 0

    mhs_results = []
    mhs_cardinalities = []
    for row in matrix_data:
        if timeout_event.is_set():  # Se il timeout è scattato, interrompi l'elaborazione
            break
        mhs_results.append(row)
        mhs_cardinalities.append(len(row))

    min_cardinality = min(mhs_cardinalities) if mhs_cardinalities else 0
    max_cardinality = max(mhs_cardinalities) if mhs_cardinalities else 0

    mhs_file_path = os.path.join(output_folder, os.path.basename(matrix_file_path).replace('.matrix', '.mhs'))
    
    print(f"  -> Salvando risultati in: {mhs_file_path}")
    
    with open(mhs_file_path, 'w') as mhs_file:
        mhs_file.write(";;; Matrix dimensions: ({}, {})\n".format(num_rows, num_cols))
        mhs_file.write(";;; Total MHS found: {}\n".format(len(mhs_results)))
        mhs_file.write(";;; Min Cardinality: {}\n".format(min_cardinality))
        mhs_file.write(";;; Max Cardinality: {}\n".format(max_cardinality))
        
        # Riassunto in caso di interruzione
        if timeout_event.is_set():
            mhs_file.write(";;; WARNING: Calculation was interrupted at level H index {}\n".format(len(mhs_results)))
            mhs_file.write(";;; Calculation was not completed.\n")
        
        mhs_file.write("\n")
        for result in mhs_results:
            mhs_file.write(" ".join(result) + "\n")

# Funzione per gestire il timeout e l'interruzione manuale
def process_files_with_timeout(matrix_files, input_folder, output_folder, timeout_seconds):
    timeout_event = threading.Event()
    threads = []

    def timeout_handler():
        time.sleep(timeout_seconds)
        timeout_event.set()  # Imposta l'evento di timeout

    # Avvia il thread per gestire il timeout
    timeout_thread = threading.Thread(target=timeout_handler)
    timeout_thread.daemon = True
    timeout_thread.start()

    # Elenco dei file .matrix nella cartella selezionata
    for i, matrix_file in enumerate(matrix_files, 1):
        matrix_file_path = os.path.join(input_folder, matrix_file)
        print(f"[{i}/{len(matrix_files)}] Elaborando {matrix_file}...")
        # Avvia un thread per l'elaborazione di ogni file .matrix
        thread = threading.Thread(target=process_matrix_file, args=(matrix_file_path, output_folder, timeout_event))
        thread.start()
        threads.append(thread)

    # Attendi il completamento di tutti i thread
    for thread in threads:
        thread.join()

# Funzione principale
def main():
    # Controlla se è stata passata una directory come argomento da riga di comando
    if len(os.sys.argv) > 1:
        input_folder = os.sys.argv[1]
        if not os.path.exists(input_folder):
            print(f"Errore: La directory '{input_folder}' non esiste.")
            return
        print(f"Utilizzando directory da riga di comando: {input_folder}")
    else:
        # Altrimenti usa la GUI per selezionare la directory
        input_folder = select_directory()
        if not input_folder:
            print("Nessuna cartella selezionata. Uscita...")
            return

    # Crea la cartella output dentro la directory dei benchmark selezionata
    output_folder = os.path.join(input_folder, 'output')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Creata cartella di output: {output_folder}")
    else:
        print(f"Utilizzando cartella di output esistente: {output_folder}")

    matrix_files = [f for f in os.listdir(input_folder) if f.endswith('.matrix')]
    
    if not matrix_files:
        print("Nessun file .matrix trovato nella cartella selezionata.")
        return

    timeout_seconds = 10  # Imposta il timeout massimo a 10 secondi per esempio
    print(f"Inizio elaborazione di {len(matrix_files)} file .matrix...")
    print(f"I risultati verranno salvati in: {output_folder}")
    process_files_with_timeout(matrix_files, input_folder, output_folder, timeout_seconds)

    print(f"Tutti i file sono stati elaborati (o interrotti).")
    print(f"I file .mhs sono stati salvati in: {output_folder}")

if __name__ == "__main__":
    main()
