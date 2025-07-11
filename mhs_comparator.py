#!/usr/bin/env python3
"""
MHS Results Comparator
======================

Confronta i risultati del calcolo MHS su diverse permutazioni
della stessa matrice per verificare la correttezza dell'algoritmo.
"""

import os
import time
import argparse
from typing import List, Set, Dict, Tuple
from mhs_calculator import MHSCalculator
import glob
from performance.performance_analyzer import PerformanceAnalyzer
from performance.performance_monitor import PerformanceMonitor
from performance.pattern_analyzer import PermutationPatternAnalyzer
from performance.execution_manager import ExecutionManager

class MHSComparator:
    """
    Classe per confrontare risultati MHS da diverse permutazioni
    """
    
    def __init__(self, enable_performance_monitoring=True):
        """
        Inizializza il comparatore
        
        Args:
            enable_performance_monitoring: Abilita monitoraggio prestazioni avanzato
        """
        self.results = {}  # file -> (mhs_list, statistics)
        self.permutation_info = {}  # file -> permutation_details
        self.enable_performance_monitoring = enable_performance_monitoring
        self.performance_data = {}  # file -> performance_stats
        self.performance_analyzer = PerformanceAnalyzer()  # Nuovo analizzatore prestazioni
        
        # Crea gestore per directory univoca di esecuzione
        self.execution_manager = ExecutionManager()
        
        # Inizializza pattern analyzer con gestore esecuzione
        self.pattern_analyzer = PermutationPatternAnalyzer(self.execution_manager)
    
    def print_analysis_files_summary(self):
        """
        Stampa un riepilogo dei file di analisi disponibili con directory univoca
        """
        # Stampa il riepilogo finale usando il gestore di esecuzione
        self.execution_manager.print_execution_summary()
    
    def load_mhs_from_file(self, mhs_file: str) -> List[Set[int]]:
        """
        Carica i MHS da un file .mhs
        
        Args:
            mhs_file: Path al file .mhs
            
        Returns:
            Lista dei MHS come set di indici
        """
        mhs_list = []
        
        try:
            with open(mhs_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(';;;'):
                        # Converte la riga binaria in set di indici
                        mhs_set = set()
                        bits = line.split()
                        for i, bit in enumerate(bits):
                            if bit == '1':
                                mhs_set.add(i)
                        mhs_list.append(mhs_set)
            
            return mhs_list
            
        except Exception as e:
            print(f"✗ Errore nel caricamento di {mhs_file}: {e}")
            return []
    
    def parse_permutation_info(self, matrix_file: str) -> Dict:
        """
        Estrae le informazioni sulla permutazione dall'header del file
        
        Args:
            matrix_file: Path al file .matrix
            
        Returns:
            Dizionario con le informazioni sulla permutazione
        """
        info = {
            'row_permutation': None,
            'col_permutation': None,
            'original_file': None
        }
        
        try:
            with open(matrix_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(';;; Permuted from:'):
                        info['original_file'] = line.split(':')[-1].strip()
                    elif line.startswith(';;; Row permutation:'):
                        perm_str = line.split(':')[-1].strip()
                        info['row_permutation'] = eval(perm_str)
                    elif line.startswith(';;; Column permutation:'):
                        perm_str = line.split(':')[-1].strip()
                        info['col_permutation'] = eval(perm_str)
                    elif not line.startswith(';;;'):
                        break
        
        except Exception as e:
            print(f"Errore nel parsing di {matrix_file}: {e}")
        
        return info
    
    def compute_mhs_for_matrix(self, matrix_file: str, timeout_seconds: int = 300) -> Tuple[List[Set[int]], Dict]:
        """
        Calcola i MHS per una matrice con monitoraggio prestazioni avanzato
        
        Args:
            matrix_file: Path al file .matrix
            timeout_seconds: Timeout per il calcolo
            
        Returns:
            Tupla (mhs_list, statistics)
        """
        print(f"Calcolo MHS per: {os.path.basename(matrix_file)}")
        
        # Inizializza performance monitor se abilitato
        perf_monitor = None
        if self.enable_performance_monitoring:
            perf_monitor = PerformanceMonitor(sample_interval=0.1)
            perf_monitor.start_monitoring()
        
        calculator = MHSCalculator(matrix_file, timeout_seconds=timeout_seconds)
        
        # Calcola MHS
        start_time = time.time()
        mhs_list = calculator.run()
        end_time = time.time()
        
        # Ferma il monitoraggio
        if perf_monitor:
            perf_monitor.stop_monitoring()
            self.performance_data[matrix_file] = perf_monitor.get_stats()
        
        # Raccogli statistiche estese
        statistics = {
            'computation_time': end_time - start_time,
            'num_mhs': len(mhs_list) if mhs_list else 0,
            'hypotheses_generated': calculator.statistics.get('hypotheses_generated', 0),
            'max_level_reached': calculator.statistics.get('max_level_reached', 0),
            'matrix_size': (calculator.n_rows, calculator.n_cols),
            'reduced_size': (calculator.n_rows, calculator.n_cols_reduced),
            'timeout_occurred': calculator.statistics.get('interrupted_by_timeout', False),
            'size_limit_hit': calculator.statistics.get('interrupted_by_size', False),
            # Nuove metriche di complessità
            'time_complexity_estimate': self._estimate_time_complexity(calculator.statistics),
            'space_complexity_estimate': self._estimate_space_complexity(calculator.statistics)
        }
        
        return mhs_list, statistics
    
    def convert_mhs_to_original_indices(self, mhs_list: List[Set[int]], 
                                      col_permutation: List[int]) -> List[Set[int]]:
        """
        Converte i MHS dagli indici permutati agli indici originali
        
        Args:
            mhs_list: Lista dei MHS con indici permutati
            col_permutation: Permutazione delle colonne utilizzata
            
        Returns:
            Lista dei MHS con indici originali
        """
        if col_permutation is None:
            return mhs_list
        
        # Crea la mappatura inversa
        inverse_perm = [0] * len(col_permutation)
        for i, original_idx in enumerate(col_permutation):
            inverse_perm[original_idx] = i
        
        # Converte gli MHS
        converted_mhs = []
        for mhs in mhs_list:
            converted_set = set()
            for permuted_idx in mhs:
                if permuted_idx < len(inverse_perm):
                    original_idx = inverse_perm[permuted_idx]
                    converted_set.add(original_idx)
            converted_mhs.append(converted_set)
        
        return converted_mhs
    
    def compare_mhs_sets(self, mhs1: List[Set[int]], mhs2: List[Set[int]]) -> Dict:
        """
        Confronta due set di MHS
        
        Args:
            mhs1: Prima lista di MHS
            mhs2: Seconda lista di MHS
            
        Returns:
            Dizionario con i risultati del confronto
        """
        set1 = set(frozenset(mhs) for mhs in mhs1)
        set2 = set(frozenset(mhs) for mhs in mhs2)
        
        return {
            'identical': set1 == set2,
            'num_mhs1': len(set1),
            'num_mhs2': len(set2),
            'common': len(set1.intersection(set2)),
            'only_in_1': len(set1 - set2),
            'only_in_2': len(set2 - set1),
            'jaccard_similarity': len(set1.intersection(set2)) / len(set1.union(set2)) if set1.union(set2) else 1.0
        }
    
    def run_comparison_experiment(self, matrix_files: List[str], timeout_seconds: int = 300):
        """
        Esegue l'esperimento di confronto su una lista di file
        
        Args:
            matrix_files: Lista dei file .matrix da confrontare
            timeout_seconds: Timeout per il calcolo di ogni file
        """
        print("Avvio esperimento di confronto MHS")
        print("="*60)
        
        # Calcola MHS per tutti i file
        for matrix_file in matrix_files:
            if os.path.exists(matrix_file):
                mhs_list, statistics = self.compute_mhs_for_matrix(matrix_file, timeout_seconds)
                self.results[matrix_file] = (mhs_list, statistics)
                self.permutation_info[matrix_file] = self.parse_permutation_info(matrix_file)
            else:
                print(f"File non trovato: {matrix_file}")
        
        # Confronta i risultati
        self.compare_all_results()
        
        # Analizza le prestazioni
        self.analyze_performance()
    
    def compare_all_results(self):
        """
        Confronta tutti i risultati tra loro
        """
        print("\nCONFRONTO RISULTATI")
        print("="*40)
        
        files = list(self.results.keys())
        
        if len(files) < 2:
            print("Servono almeno 2 file per il confronto")
            return
        
        # Confronta tutti contro tutti
        for i, file1 in enumerate(files):
            for j, file2 in enumerate(files[i+1:], i+1):
                mhs1, _ = self.results[file1]
                mhs2, _ = self.results[file2]
                
                # Converti agli indici originali se necessario
                perm1 = self.permutation_info[file1]
                perm2 = self.permutation_info[file2]
                
                if perm1['col_permutation'] is not None:
                    mhs1 = self.convert_mhs_to_original_indices(mhs1, perm1['col_permutation'])
                
                if perm2['col_permutation'] is not None:
                    mhs2 = self.convert_mhs_to_original_indices(mhs2, perm2['col_permutation'])
                
                # Confronta
                comparison = self.compare_mhs_sets(mhs1, mhs2)
                
                print(f"\n{os.path.basename(file1)} vs {os.path.basename(file2)}")
                print(f"   Identici: {'SI' if comparison['identical'] else 'NO'}")
                print(f"   MHS File1: {comparison['num_mhs1']}")
                print(f"   MHS File2: {comparison['num_mhs2']}")
                print(f"   Comuni: {comparison['common']}")
                print(f"   Solo in File1: {comparison['only_in_1']}")
                print(f"   Solo in File2: {comparison['only_in_2']}")
                print(f"   Similarità Jaccard: {comparison['jaccard_similarity']:.3f}")
                
                if not comparison['identical']:
                    print("ATTENZIONE: I risultati non sono identici!")
    
    def analyze_performance(self):
        """
        Analizza le prestazioni su diverse permutazioni
        """
        print("\n")
        print("="*50)
        print("ANALISI PRESTAZIONI")
        print("="*50)
        print("\n")
        
        # Ordina per tempo di calcolo
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1][1]['computation_time']
        )
        
        print(f"{'File':<25} {'Tempo (s)':<10} {'MHS':<6} {'Ipotesi':<10} {'Livelli':<8}")
        print("-" * 65)
        
        for file_path, (mhs_list, stats) in sorted_results:
            filename = os.path.basename(file_path)
            if len(filename) > 24:
                filename = filename[:21] + "..."
            
            print(f"{filename:<25} "
                  f"{stats['computation_time']:<10.3f} "
                  f"{stats['num_mhs']:<6} "
                  f"{stats['hypotheses_generated']:<10} "
                  f"{stats['max_level_reached']:<8}")
        
        # Statistiche aggregate integrate nella sezione analisi avanzate
    
    def _estimate_time_complexity(self, calculator_stats: Dict) -> str:
        """
        Stima la complessità temporale basata sulle statistiche dell'algoritmo
        
        Args:
            calculator_stats: Statistiche dal calculator
            
        Returns:
            Stima della complessità temporale
        """
        hypotheses = calculator_stats.get('hypotheses_generated', 0)
        max_level = calculator_stats.get('max_level_reached', 0)
        
        if hypotheses == 0:
            return "O(1) - trivial"
        elif hypotheses < 100:
            return "O(n) - linear"
        elif hypotheses < 1000:
            return "O(n²) - quadratic"
        elif max_level > 10:
            return "O(2^n) - exponential"
        else:
            return "O(n^k) - polynomial"
    
    def _estimate_space_complexity(self, calculator_stats: Dict) -> str:
        """
        Stima la complessità spaziale basata sulle statistiche dell'algoritmo
        
        Args:
            calculator_stats: Statistiche dal calculator
            
        Returns:
            Stima della complessità spaziale
        """
        hypotheses = calculator_stats.get('hypotheses_generated', 0)
        max_level = calculator_stats.get('max_level_reached', 0)
        
        if hypotheses == 0:
            return "O(1) - constant"
        elif max_level <= 5:
            return "O(n) - linear"
        elif max_level <= 10:
            return "O(n²) - quadratic"
        else:
            return "O(2^n) - exponential"

    def run_enhanced_comparison_experiment(self, matrix_files: List[str], timeout: int = 300):
        """
        Esegue un esperimento di confronto enhanced con analisi prestazioni avanzate
        
        Esegue il confronto standard tra permutazioni e aggiunge analisi approfondite
        delle prestazioni, complessità computazionale e generazione di report grafici.
        Questo è il metodo principale per il Task 3 dell'elaborato.
        
        Args:
            matrix_files: Lista dei file matrice da confrontare
            timeout: Timeout per il calcolo di ogni file (default: 300 secondi)
            
        Returns:
            bool - True se l'esperimento è completato con successo, False altrimenti
        """
        print(f"Avvio esperimento enhanced su {len(matrix_files)} permutazioni")
        print("="*60)
        
        # Traccia tempo totale esperimento
        total_start_time = time.time()
        
        # Esegui l'esperimento standard
        self.run_comparison_experiment(matrix_files, timeout)
        success = True
        
        if success:
            # Aggiungi analisi avanzate usando il nuovo PerformanceAnalyzer
            print(f"\nAvvio analisi avanzate...")
            
            # Genera analisi comprensiva direttamente nella directory di esecuzione
            execution_dir = self.execution_manager.get_execution_dir()
            
            # Usa il nuovo analizzatore per le prestazioni 
            json_file, csv_file, reports_dir = self.performance_analyzer.analyze_comprehensive_performance(
                self.performance_data, self.results, output_dir=execution_dir
            )
            
            # Registra i file generati nel gestore esecuzione
            if json_file:
                self.execution_manager.register_file(json_file, "json", "Report Completo Analisi Prestazioni")
            if csv_file:
                self.execution_manager.register_file(csv_file, "csv", "Riassunto Prestazioni in Formato Tabellare")
            
            # Analisi complessità
            self.performance_analyzer.analyze_complexity(self.results, self.performance_data)
            
            # 🆕 NUOVA FUNZIONALITÀ: Analisi pattern prestazionali per permutazioni
            print(f"\nAvvio analisi pattern prestazionali...")
            pattern_results = self.pattern_analyzer.analyze_performance_patterns(
                self.results, self.performance_data
            )
            
            # Genera visualizzazioni specifiche per i pattern
            pattern_graphs = self.pattern_analyzer.generate_pattern_visualizations()
            
            # Genera report completo con grafici
            report_file = self.performance_analyzer.generate_comprehensive_report(
                self.results, self.performance_data, output_dir=execution_dir
            )
            
            # Registra il report grafico
            if report_file:
                self.execution_manager.register_file(report_file, "png", "Report Grafico Completo Prestazioni")
            
            # Genera summary finale dell'esecuzione
            summary_file = self.execution_manager.generate_execution_summary()
            
        # Calcola e mostra tempo totale
        total_time = time.time() - total_start_time
        print(f"\nTempo di esecuzione compito 3: {total_time:.2f}s")
        print(f"Media per permutazione: {total_time/len(matrix_files):.2f}s")
        
        return success
    







def main():
    """
    Funzione principale
    """
    parser = argparse.ArgumentParser(
        description='Confronta risultati MHS da diverse permutazioni'
    )
    parser.add_argument('input_pattern', 
                       help='Pattern per i file da confrontare (es: permutations/*.matrix)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Output verboso')
    
    args = parser.parse_args()
    
    # Trova i file che corrispondono al pattern
    matrix_files = glob.glob(args.input_pattern)
    
    if not matrix_files:
        print(f"Nessun file trovato per il pattern: {args.input_pattern}")
        return
    
    print(f"Trovati {len(matrix_files)} file da confrontare")
    
    # Esegui il confronto
    comparator = MHSComparator()
    comparator.run_comparison_experiment(sorted(matrix_files))


if __name__ == "__main__":
    main()