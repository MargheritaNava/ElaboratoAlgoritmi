"""
Minimal Hitting Set Calculator
===============================

Implementazione dell'algoritmo per il calcolo dei Minimal Hitting Set (MHS)
basato sul template fornito nelle specifiche dell'elaborato.

Autore: Mattia Pavlovic
Data: Luglio 2025
"""

import os
import time
import argparse
import signal
import threading
from typing import List, Set, Tuple, Dict, Optional
from collections import defaultdict


class TimeoutError(Exception):
    """Eccezione per timeout di calcolo"""
    pass


class FileSizeError(Exception):
    """Eccezione per file troppo grandi"""
    pass


class TimeoutHandler:
    """Gestisce timeout per operazioni lunghe"""
    
    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        self.timer = None
        self.timed_out = False
    
    def _timeout_handler(self):
        """Handler interno per timeout"""
        self.timed_out = True
    
    def start(self):
        """Avvia il timer di timeout"""
        if self.timeout_seconds > 0:
            self.timer = threading.Timer(self.timeout_seconds, self._timeout_handler)
            self.timer.start()
    
    def stop(self):
        """Ferma il timer di timeout"""
        if self.timer:
            self.timer.cancel()
    
    def check_timeout(self):
        """Controlla se è scaduto il timeout"""
        if self.timed_out:
            raise TimeoutError(f"Operazione interrotta per timeout ({self.timeout_seconds}s)")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class MHSCalculator:
    """
    Classe principale per il calcolo dei Minimal Hitting Set
    """
    
    def __init__(self, matrix_file: str, timeout_seconds: int = 300, max_file_size_mb: int = 50):
        """
        Inizializza il calcolatore MHS
        
        Args:
            matrix_file: Path al file .matrix di input
            timeout_seconds: Timeout massimo per il calcolo (default: 5 minuti)
            max_file_size_mb: Dimensione massima file in MB (default: 50MB)
        """
        self.matrix_file = matrix_file
        self.timeout_seconds = timeout_seconds
        self.max_file_size_mb = max_file_size_mb
        self.matrix = []  # Matrice originale
        self.n_rows = 0   # |N| - numero di insiemi
        self.n_cols = 0   # |M| - numero di elementi del dominio
        self.n_cols_reduced = 0  # |M'| - numero di colonne non vuote
        self.empty_columns = []  # Colonne vuote rimosse
        self.column_mapping = {}  # Mappatura colonne originali -> ridotte
        self.reverse_mapping = {}  # Mappatura colonne ridotte -> originali
        self.solutions = []  # MHS trovati
        self.interrupted = False  # Flag per interruzione
        self.statistics = {
            'start_time': 0,
            'end_time': 0,
            'total_time': 0,
            'hypotheses_generated': 0,
            'hypotheses_by_level': defaultdict(int),
            'solutions_found': 0,
            'max_level_reached': 0,
            'interrupted_by_timeout': False,
            'interrupted_by_size': False
        }
        
    def load_matrix(self) -> bool:
        """
        Carica la matrice dal file .matrix con controlli di dimensione
        
        Returns:
            True se caricamento riuscito, False altrimenti
        """
        try:
            # Controlla dimensione file
            file_size_mb = os.path.getsize(self.matrix_file) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise FileSizeError(f"File troppo grande: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB")
            
            print(f"📁 Caricamento file ({file_size_mb:.2f}MB): {os.path.basename(self.matrix_file)}")
            
            with open(self.matrix_file, 'r') as f:
                lines = f.readlines()
            
            # Trova l'inizio della matrice (dopo le righe di commento)
            matrix_start = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith(';;;'):
                    matrix_start = i
                    break
            
            # Carica la matrice
            self.matrix = []
            for line in lines[matrix_start:]:
                line = line.strip()
                if line and not line.startswith(';;;'):
                    # Rimuovi il terminatore "-" se presente
                    if line.endswith('-'):
                        line = line[:-1].strip()
                    
                    row = [int(x) for x in line.split() if x.isdigit()]
                    if row:
                        self.matrix.append(row)
            
            self.n_rows = len(self.matrix)
            self.n_cols = len(self.matrix[0]) if self.matrix else 0
            
            # Controllo dimensioni matrice per complessità
            matrix_complexity = self.n_rows * self.n_cols
            if matrix_complexity > 10000:  # Soglia arbitraria
                print(f"⚠️  Matrice grande ({self.n_rows}×{self.n_cols}, complessità: {matrix_complexity})")
                print(f"   Timeout impostato: {self.timeout_seconds}s")
            
            print(f"✓ Matrice caricata: {self.n_rows} righe × {self.n_cols} colonne")
            return True
            
        except FileSizeError as e:
            print(f"✗ {e}")
            self.statistics['interrupted_by_size'] = True
            return False
        except Exception as e:
            print(f"✗ Errore nel caricamento: {e}")
            return False
    
    def reduce_matrix(self):
        """
        Riduce la matrice rimuovendo le colonne vuote (tutti 0)
        """
        if not self.matrix:
            return
        
        # Trova colonne vuote
        self.empty_columns = []
        for j in range(self.n_cols):
            if all(self.matrix[i][j] == 0 for i in range(self.n_rows)):
                self.empty_columns.append(j)
        
        # Crea mappatura colonne
        reduced_col = 0
        for original_col in range(self.n_cols):
            if original_col not in self.empty_columns:
                self.column_mapping[original_col] = reduced_col
                self.reverse_mapping[reduced_col] = original_col
                reduced_col += 1
        
        self.n_cols_reduced = reduced_col
        
        # Crea matrice ridotta
        if self.empty_columns:
            reduced_matrix = []
            for i in range(self.n_rows):
                reduced_row = []
                for j in range(self.n_cols):
                    if j not in self.empty_columns:
                        reduced_row.append(self.matrix[i][j])
                reduced_matrix.append(reduced_row)
            self.matrix = reduced_matrix
        
        print(f"✓ Matrice ridotta: {self.n_rows} righe × {self.n_cols_reduced} colonne")
        if self.empty_columns:
            print(f"  Colonne vuote rimosse: {[c+1 for c in self.empty_columns]}")
    
    def binary_to_set(self, binary_repr: str) -> Set[int]:
        """
        Converte una rappresentazione binaria in un insieme di indici
        
        Args:
            binary_repr: Stringa binaria (es. "1010")
            
        Returns:
            Set degli indici dove il bit è 1
        """
        return {i for i, bit in enumerate(binary_repr) if bit == '1'}
    
    def set_to_binary(self, element_set: Set[int]) -> str:
        """
        Converte un insieme di indici in rappresentazione binaria
        
        Args:
            element_set: Set di indici
            
        Returns:
            Stringa binaria
        """
        binary = ['0'] * self.n_cols_reduced
        for i in element_set:
            if i < self.n_cols_reduced:
                binary[i] = '1'
        return ''.join(binary)
    
    def is_hitting_set(self, hypothesis: Set[int]) -> bool:
        """
        Verifica se un'ipotesi è un hitting set
        
        Args:
            hypothesis: Set di indici delle colonne
            
        Returns:
            True se è un hitting set, False altrimenti
        """
        for row in self.matrix:
            # Controlla se l'ipotesi interseca questa riga
            if not any(row[j] == 1 for j in hypothesis):
                return False
        return True
    
    def compute_vector(self, hypothesis: Set[int]) -> List[int]:
        """
        Calcola il vettore associato all'ipotesi (bitwise OR delle colonne)
        
        Args:
            hypothesis: Set di indici delle colonne
            
        Returns:
            Vettore binario di lunghezza n_rows
        """
        vector = [0] * self.n_rows
        
        for row_idx in range(self.n_rows):
            # Verifica se l'ipotesi interseca questa riga
            if any(self.matrix[row_idx][col_idx] == 1 for col_idx in hypothesis):
                vector[row_idx] = 1
        
        return vector
    
    def generate_successors_left(self, hypothesis: Set[int]) -> List[Set[int]]:
        """
        Genera i successori immediati sinistri (succL) di un'ipotesi
        
        Args:
            hypothesis: Set di indici delle colonne
            
        Returns:
            Lista dei successori sinistri
        """
        successors = []
        binary_repr = self.set_to_binary(hypothesis)
        
        # Trova il bit 1 più significativo
        most_significant_one = -1
        for i in range(len(binary_repr)):
            if binary_repr[i] == '1':
                most_significant_one = i
                break
        
        # Genera successori complementando 0 a sinistra del bit 1 più significativo
        for i in range(most_significant_one):
            if binary_repr[i] == '0':
                new_hypothesis = hypothesis.copy()
                new_hypothesis.add(i)
                successors.append(new_hypothesis)
        
        return successors
    
    def generate_immediate_successors(self, hypothesis: Set[int]) -> List[Set[int]]:
        """
        Genera tutti i successori immediati di un'ipotesi
        
        Args:
            hypothesis: Set di indici delle colonne
            
        Returns:
            Lista di tutti i successori immediati
        """
        successors = []
        
        # Genera successori aggiungendo un elemento non presente
        for i in range(self.n_cols_reduced):
            if i not in hypothesis:
                new_hypothesis = hypothesis.copy()
                new_hypothesis.add(i)
                successors.append(new_hypothesis)
        
        return successors
    
    def calculate_mhs(self) -> List[Set[int]]:
        """
        Calcola i Minimal Hitting Set usando l'algoritmo del template con timeout
        
        Returns:
            Lista dei MHS trovati
        """
        print("🔍 Inizio calcolo MHS...")
        self.statistics['start_time'] = time.time()
        
        try:
            with TimeoutHandler(self.timeout_seconds) as timeout_handler:
                # Inizializzazione
                current = []  # Livello corrente
                next_level = []  # Prossimo livello
                solutions = []  # MHS trovati
                
                # Livello 0: ipotesi vuota
                empty_hypothesis = set()
                if self.is_hitting_set(empty_hypothesis):
                    solutions.append(empty_hypothesis)
                    print("✓ Insieme vuoto è un MHS")
                    return solutions
                
                # Livello 1: singoletti
                current = [set([i]) for i in range(self.n_cols_reduced)]
                level = 1
                
                max_level = min(self.n_rows, self.n_cols_reduced)
                
                while current and level <= max_level:
                    # Controlla timeout ad ogni livello
                    timeout_handler.check_timeout()
                    
                    print(f"📊 Livello {level}: {len(current)} ipotesi")
                    self.statistics['hypotheses_by_level'][level] = len(current)
                    self.statistics['max_level_reached'] = level
                    
                    next_level = []
                    
                    for i, hypothesis in enumerate(current):
                        # Controlla timeout ogni 100 ipotesi
                        if i % 100 == 0:
                            timeout_handler.check_timeout()
                        
                        self.statistics['hypotheses_generated'] += 1
                        
                        # Verifica se è un hitting set
                        if self.is_hitting_set(hypothesis):
                            # Verifica minimalità
                            is_minimal = True
                            for solution in solutions:
                                if solution.issubset(hypothesis) and solution != hypothesis:
                                    is_minimal = False
                                    break
                            
                            if is_minimal:
                                # Rimuovi soluzioni non minimali
                                solutions = [s for s in solutions if not hypothesis.issubset(s)]
                                solutions.append(hypothesis)
                                print(f"✓ MHS trovato (cardinalità {len(hypothesis)}): {sorted(hypothesis)}")
                                continue
                        
                        # Genera successori se non è una soluzione
                        successors = self.generate_immediate_successors(hypothesis)
                        
                        for successor in successors:
                            # Evita di aggiungere successori che sono superseti di soluzioni
                            is_valid = True
                            for solution in solutions:
                                if solution.issubset(successor):
                                    is_valid = False
                                    break
                            
                            if is_valid and successor not in next_level:
                                next_level.append(successor)
                    
                    current = next_level
                    level += 1
                
                self.statistics['end_time'] = time.time()
                self.statistics['total_time'] = self.statistics['end_time'] - self.statistics['start_time']
                self.statistics['solutions_found'] = len(solutions)
                
                print(f"✅ Calcolo completato: {len(solutions)} MHS trovati")
                return solutions
                
        except TimeoutError as e:
            self.interrupted = True
            self.statistics['interrupted_by_timeout'] = True
            self.statistics['end_time'] = time.time()
            self.statistics['total_time'] = self.statistics['end_time'] - self.statistics['start_time']
            
            print(f"⏰ {e}")
            print(f"⚠️  Calcolo interrotto - risultati parziali disponibili")
            return []  # Ritorna lista vuota per timeout
        
        except Exception as e:
            self.statistics['end_time'] = time.time()
            self.statistics['total_time'] = self.statistics['end_time'] - self.statistics['start_time']
            print(f"❌ Errore durante il calcolo: {e}")
            return []
    
    def convert_to_original_format(self, mhs_list: List[Set[int]]) -> List[Set[int]]:
        """
        Converte i MHS dal formato ridotto al formato originale
        
        Args:
            mhs_list: Lista dei MHS nel formato ridotto
            
        Returns:
            Lista dei MHS nel formato originale
        """
        original_mhs = []
        
        for mhs in mhs_list:
            original_set = set()
            for reduced_col in mhs:
                original_col = self.reverse_mapping[reduced_col]
                original_set.add(original_col)
            original_mhs.append(original_set)
        
        return original_mhs
    
    def save_results(self, output_file: str, mhs_list: List[Set[int]]):
        """
        Salva i risultati in formato .mhs con informazioni su timeout e interruzioni
        
        Args:
            output_file: Path del file di output
            mhs_list: Lista dei MHS da salvare
        """
        try:
            with open(output_file, 'w') as f:
                # Header con informazioni
                f.write(";;; Minimal Hitting Set Calculator Results\n")
                f.write(f";;; Input file: {os.path.basename(self.matrix_file)}\n")
                f.write(f";;; Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f";;; Original matrix size: {self.n_rows} × {self.n_cols}\n")
                f.write(f";;; Reduced matrix size: {self.n_rows} × {self.n_cols_reduced}\n")
                
                if self.empty_columns:
                    f.write(f";;; Empty columns removed: {[c+1 for c in self.empty_columns]}\n")
                
                # Informazioni su interruzioni
                if self.statistics.get('interrupted_by_timeout', False):
                    f.write(f";;; WARNING: Computation interrupted by timeout ({self.timeout_seconds}s)\n")
                    f.write(f";;; Results are INCOMPLETE - only partial solutions found\n")
                elif self.statistics.get('interrupted_by_size', False):
                    f.write(f";;; WARNING: File too large (>{self.max_file_size_mb}MB) - computation skipped\n")
                
                f.write(f";;; Number of MHS found: {len(mhs_list)}\n")
                f.write(f";;; Computation time: {self.statistics['total_time']:.3f} seconds\n")
                f.write(f";;; Hypotheses generated: {self.statistics['hypotheses_generated']}\n")
                f.write(f";;; Max level reached: {self.statistics['max_level_reached']}\n")
                f.write(";;;\n")
                
                # Statistiche per livello
                f.write(";;; Hypotheses by level:\n")
                for level in sorted(self.statistics['hypotheses_by_level'].keys()):
                    count = self.statistics['hypotheses_by_level'][level]
                    f.write(f";;; Level {level}: {count} hypotheses\n")
                f.write(";;;\n")
                
                # Se non ci sono risultati a causa di interruzioni, scrivi comunque il file
                if not mhs_list and (self.statistics.get('interrupted_by_timeout', False) or 
                                   self.statistics.get('interrupted_by_size', False)):
                    f.write(";;; No results due to interruption\n")
                else:
                    # Converti al formato originale
                    original_mhs = self.convert_to_original_format(mhs_list)
                    
                    # Scrivi i MHS come matrice binaria
                    for mhs in original_mhs:
                        row = ['0'] * self.n_cols
                        for col_idx in mhs:
                            row[col_idx] = '1'
                        f.write(' '.join(row) + '\n')
            
            if self.statistics.get('interrupted_by_timeout', False):
                print(f"⚠️  Risultati parziali salvati in: {output_file}")
            elif self.statistics.get('interrupted_by_size', False):
                print(f"⚠️  File di stato salvato in: {output_file}")
            else:
                print(f"✅ Risultati salvati in: {output_file}")
            
        except Exception as e:
            print(f"✗ Errore nel salvataggio: {e}")
    
    def print_statistics(self):
        """
        Stampa le statistiche di esecuzione con informazioni su interruzioni
        """
        print("\n" + "="*50)
        print("📈 STATISTICHE ESECUZIONE")
        print("="*50)
        
        # Controlla se ci sono state interruzioni
        if self.statistics.get('interrupted_by_timeout', False):
            print("⚠️  CALCOLO INTERROTTO PER TIMEOUT")
            print(f"   Timeout impostato: {self.timeout_seconds}s")
        elif self.statistics.get('interrupted_by_size', False):
            print("⚠️  FILE TROPPO GRANDE - CALCOLO SALTATO")
            print(f"   Limite dimensione: {self.max_file_size_mb}MB")
        
        print(f"Tempo di calcolo: {self.statistics['total_time']:.3f} secondi")
        print(f"Ipotesi generate: {self.statistics['hypotheses_generated']}")
        print(f"MHS trovati: {self.statistics['solutions_found']}")
        print(f"Livello massimo raggiunto: {self.statistics['max_level_reached']}")
        print(f"Matrice originale: {self.n_rows} × {self.n_cols}")
        print(f"Matrice ridotta: {self.n_rows} × {self.n_cols_reduced}")
        
        if self.statistics['hypotheses_by_level']:
            print("\nIpotesi per livello:")
            for level in sorted(self.statistics['hypotheses_by_level'].keys()):
                count = self.statistics['hypotheses_by_level'][level]
                print(f"  Livello {level}: {count} ipotesi")
        
        print("="*50)
    
    def run(self, output_file: str = None):
        """
        Esegue il calcolo completo dei MHS con gestione robuста di timeout e errori
        
        Args:
            output_file: Path del file di output (opzionale)
        """
        try:
            # Carica la matrice
            if not self.load_matrix():
                if output_file:
                    # Salva file di errore anche se il caricamento fallisce
                    self.save_results(output_file, [])
                return []
            
            # Riduci la matrice
            self.reduce_matrix()
            
            # Calcola i MHS
            mhs_list = self.calculate_mhs()
            
            # Salva i risultati (anche se vuoti per timeout)
            if output_file:
                self.save_results(output_file, mhs_list)
            
            # Stampa statistiche
            self.print_statistics()
            
            return mhs_list
        
        except Exception as e:
            print(f"❌ Errore critico durante l'esecuzione: {e}")
            if output_file:
                # Salva file di errore
                try:
                    with open(output_file, 'w') as f:
                        f.write(";;; ERRORE CRITICO DURANTE L'ESECUZIONE\n")
                        f.write(f";;; Errore: {str(e)}\n")
                        f.write(f";;; File: {os.path.basename(self.matrix_file)}\n")
                        f.write(f";;; Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                except:
                    pass
            return []


def main():
    """
    Funzione principale per l'esecuzione da riga di comando
    """
    parser = argparse.ArgumentParser(
        description='Calcola i Minimal Hitting Set da un file .matrix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python mhs_calculator.py input.matrix
  python mhs_calculator.py input.matrix -o output.mhs
  python mhs_calculator.py input.matrix --timeout 600 --max-size 100
        """
    )
    parser.add_argument('input_file', help='File .matrix di input')
    parser.add_argument('-o', '--output', help='File .mhs di output')
    parser.add_argument('-v', '--verbose', action='store_true', help='Output verboso')
    parser.add_argument('--timeout', type=int, default=300, 
                       help='Timeout in secondi (default: 300)')
    parser.add_argument('--max-size', type=int, default=50,
                       help='Dimensione massima file in MB (default: 50)')
    
    args = parser.parse_args()
    
    print(f"🚀 MHS Calculator")
    print(f"📁 File input: {args.input_file}")
    print(f"⏰ Timeout: {args.timeout}s")
    print(f"📊 Limite dimensione: {args.max_size}MB")
    
    # Controlla esistenza file
    if not os.path.exists(args.input_file):
        print(f"❌ File non trovato: {args.input_file}")
        return 1
    
    # Genera nome file di output se non specificato
    if not args.output:
        # Se il file è in una cartella benchmark, salva nella sottocartella output
        input_dir = os.path.dirname(args.input_file)
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        
        if 'benchmark' in input_dir.lower():
            output_dir = os.path.join(input_dir, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            args.output = os.path.join(output_dir, f"{base_name}.mhs")
        else:
            args.output = f"{base_name}.mhs"
    
    print(f"📄 File output: {args.output}")
    print("-" * 50)
    
    # Esegui il calcolo
    calculator = MHSCalculator(
        args.input_file, 
        timeout_seconds=args.timeout,
        max_file_size_mb=args.max_size
    )
    result = calculator.run(args.output)
    
    # Codice di uscita basato sul risultato
    if calculator.statistics.get('interrupted_by_timeout', False):
        print(f"\n⚠️  Processo completato con timeout")
        return 2  # Codice speciale per timeout
    elif calculator.statistics.get('interrupted_by_size', False):
        print(f"\n⚠️  File troppo grande - elaborazione saltata")
        return 3  # Codice speciale per file troppo grande
    elif result is not None and len(result) >= 0:
        print(f"\n✅ Processo completato con successo")
        return 0
    else:
        print(f"\n❌ Processo fallito")
        return 1


if __name__ == "__main__":
    main()
