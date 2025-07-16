#!/usr/bin/env python3
"""
Batch Performance Analyzer
==========================

Modulo unificato per l'analisi delle prestazioni sui batch di file MHS.
Integra le funzionalità di analisi critica, complessità teorica e report.
"""

import os
import time
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from .performance_analyzer import PerformanceAnalyzer
from .performance_reporter import PerformanceReporter
from .performance_monitor import PerformanceMonitor

class BatchPerformanceAnalyzer:
    """
    Analizzatore unificato per le prestazioni dei batch MHS
    """
    
    def __init__(self, output_dir: str = "results"):
        """
        Inizializza l'analizzatore batch
        
        Args:
            output_dir: Directory per i report e i grafici
        """
        self.output_dir = output_dir
        self.performance_analyzer = PerformanceAnalyzer()
        self.performance_reporter = PerformanceReporter()
        
        # Assicurati che la directory esista
        os.makedirs(output_dir, exist_ok=True)
    
    def analyze_batch_results(self, results_summary: List[Dict]) -> Tuple[str, str, str]:
        """
        Analizza i risultati di un batch di calcoli MHS
        
        Args:
            results_summary: Lista dei risultati del batch
            
        Returns:
            Tuple: (json_file, csv_file, plots_dir)
        """
        print(f"\nAVVIO ANALISI BATCH UNIFICATA")
        print("=" * 50)
        
        # Filtra risultati validi
        valid_results = [r for r in results_summary if 'error' not in r]
        
        if not valid_results:
            print("Nessun risultato valido per l'analisi")
            return None, None, None
        
        # Esegui analisi critica
        self._analyze_performance_critically(valid_results)
        
        # Genera grafici
        plots_dir = self._generate_analysis_plots(valid_results)
        
        # Analizza complessità teorica
        self._analyze_theoretical_complexity(valid_results)
        
        # Salva report
        json_file, csv_file = self._save_performance_reports(valid_results)
        
        return json_file, csv_file, plots_dir
    
    def _analyze_performance_critically(self, results: List[Dict]):
        """
        Analisi critica delle prestazioni spaziali e temporali
        """
        print(f"\nVALUTAZIONE CRITICA DELLE PRESTAZIONI")
        print("=" * 80)
        
        # Estrai dati per analisi
        times = [r['computation_time'] for r in results]
        mhs_counts = [r['mhs_count'] for r in results]
        hypotheses = [r.get('hypotheses_generated', 0) for r in results]
        matrix_sizes = self._extract_matrix_sizes(results)
        
        # 1. ANALISI TEMPORALE
        self._print_temporal_analysis(times, results)
        
        # 2. ANALISI SPAZIALE
        self._print_spatial_analysis(hypotheses, times, results)
        
        # 3. CORRELAZIONI
        self._print_correlation_analysis(matrix_sizes, times, mhs_counts, hypotheses)
        
        # 4. CLASSIFICAZIONE
        self._print_complexity_classification(times, hypotheses, results)
    
    def _print_temporal_analysis(self, times: List[float], results: List[Dict]):
        """Stampa analisi temporale dettagliata"""
        print(f"\nANALISI PRESTAZIONI TEMPORALI")
        print("-" * 60)
        print(f"Tempo medio di calcolo: {np.mean(times):.3f}s")
        print(f"Tempo mediano: {np.median(times):.3f}s")
        print(f"Deviazione standard: {np.std(times):.3f}s")
        print(f"Tempo minimo: {min(times):.3f}s")
        print(f"Tempo massimo: {max(times):.3f}s")
        print(f"Range temporale: {max(times) - min(times):.3f}s")
        
        # Classificazione prestazioni temporali
        fast_files = [r for r in results if r['computation_time'] < np.mean(times) - np.std(times)]
        slow_files = [r for r in results if r['computation_time'] > np.mean(times) + np.std(times)]
        
        print(f"\nFile elaborati VELOCEMENTE ({len(fast_files)}):")
        for f in fast_files[:5]:  # Top 5
            print(f"   • {f['file']}: {f['computation_time']:.3f}s ({f['mhs_count']} MHS)")
        
        print(f"\nFile elaborati LENTAMENTE ({len(slow_files)}):")
        for f in slow_files[:5]:  # Top 5
            print(f"   • {f['file']}: {f['computation_time']:.3f}s ({f['mhs_count']} MHS)")
    
    def _print_spatial_analysis(self, hypotheses: List[int], times: List[float], results: List[Dict]):
        """Stampa analisi spaziale dettagliata"""
        print(f"\nANALISI PRESTAZIONI SPAZIALI")
        print("-" * 60)
        print(f"Ipotesi medie generate: {np.mean(hypotheses):.0f}")
        print(f"Ipotesi mediane: {np.median(hypotheses):.0f}")
        print(f"Deviazione standard ipotesi: {np.std(hypotheses):.0f}")
        print(f"Minime ipotesi: {min(hypotheses)}")
        print(f"Massime ipotesi: {max(hypotheses)}")
        
        # Stima uso memoria (approssimativo)
        estimated_memory = [h * 0.001 for h in hypotheses]  # Stima: 1KB per ipotesi
        print(f"Uso memoria stimato medio: {np.mean(estimated_memory):.2f}MB")
        print(f"Uso memoria stimato massimo: {max(estimated_memory):.2f}MB")
    
    def _print_correlation_analysis(self, matrix_sizes: List[int], times: List[float], 
                                   mhs_counts: List[int], hypotheses: List[int]):
        """Stampa analisi delle correlazioni"""
        print(f"\nANALISI CORRELAZIONI")
        print("-" * 60)
        
        # Correlazione dimensione matrice vs tempo
        if matrix_sizes and len(set(matrix_sizes)) > 1:
            corr_size_time = np.corrcoef(matrix_sizes, times)[0,1]
            print(f"Correlazione dimensione-tempo: {corr_size_time:.3f}")
            
            if corr_size_time > 0.7:
                print("   → FORTE correlazione positiva: matrici grandi = tempi lunghi")
            elif corr_size_time > 0.3:
                print("   → MODERATA correlazione positiva")
            elif corr_size_time < -0.3:
                print("   → Correlazione negativa (inaspettata)")
            else:
                print("   → DEBOLE correlazione: dimensione non predice tempo")
        
        # Correlazione numero MHS vs tempo
        if len(set(mhs_counts)) > 1:
            corr_mhs_time = np.corrcoef(mhs_counts, times)[0,1]
            print(f"Correlazione MHS-tempo: {corr_mhs_time:.3f}")
            
            if corr_mhs_time > 0.5:
                print("   → Più MHS trovati = tempi più lunghi")
            else:
                print("   → Numero MHS non correla direttamente con tempo")
    
    def _print_complexity_classification(self, times: List[float], hypotheses: List[int], 
                                       results: List[Dict]):
        """Stampa classificazione per complessità"""
        print(f"\nCLASSIFICAZIONE PER COMPLESSITÀ")
        print("-" * 60)
        
        # Definisci soglie
        time_threshold_fast = np.percentile(times, 25)
        time_threshold_slow = np.percentile(times, 75)
        hyp_threshold_simple = np.percentile(hypotheses, 25)
        hyp_threshold_complex = np.percentile(hypotheses, 75)
        
        categories = {
            'semplici_veloci': [],
            'semplici_lenti': [],
            'complessi_veloci': [],
            'complessi_lenti': []
        }
        
        for r in results:
            time = r['computation_time']
            hyp = r.get('hypotheses_generated', 0)
            
            if hyp <= hyp_threshold_simple and time <= time_threshold_fast:
                categories['semplici_veloci'].append(r)
            elif hyp <= hyp_threshold_simple and time > time_threshold_slow:
                categories['semplici_lenti'].append(r)
            elif hyp > hyp_threshold_complex and time <= time_threshold_fast:
                categories['complessi_veloci'].append(r)
            elif hyp > hyp_threshold_complex and time > time_threshold_slow:
                categories['complessi_lenti'].append(r)
        
        for category, files in categories.items():
            if files:
                print(f"{category.upper().replace('_', ' ')}: {len(files)} file")
    
    def _extract_matrix_sizes(self, results: List[Dict]) -> List[int]:
        """Estrae le dimensioni delle matrici dai risultati"""
        matrix_sizes = []
        for r in results:
            size_str = r['matrix_size']
            if '×' in size_str:
                rows, cols = map(int, size_str.split('×'))
                matrix_sizes.append(rows * cols)
            else:
                matrix_sizes.append(0)
        return matrix_sizes
    
    def _extract_rows_and_cols(self, results: List[Dict]) -> Tuple[List[int], List[int]]:
        """Estrae le righe e le colonne dalle dimensioni delle matrici"""
        rows, cols = [], []
        for r in results:
            size_str = r['matrix_size']
            if '×' in size_str:
                row, col = map(int, size_str.split('×'))
                rows.append(row)
                cols.append(col)
            else:
                rows.append(0)
                cols.append(0)
        return rows, cols

    def _extract_matrix_sizes_optimized(self, results: List[Dict]) -> List[int]:
        """Estrae le dimensioni delle matrici ottimizzate dai risultati"""
        matrix_sizes = []
        for r in results:
            size_str = r['reduced_size']
            if '×' in size_str:
                rows, cols = map(int, size_str.split('×'))
                matrix_sizes.append(rows * cols)
            else:
                matrix_sizes.append(0)
        return matrix_sizes
    
    def _extract_rows_and_cols_optimized(self, results: List[Dict]) -> Tuple[List[int], List[int]]:
        """Estrae le righe e le colonne dalle dimensioni delle matrici ottimizzate"""
        rows, cols = [], []
        for r in results:
            size_str = r['reduced_size']
            if '×' in size_str:
                row, col = map(int, size_str.split('×'))
                rows.append(row)
                cols.append(col)
            else:
                rows.append(0)
                cols.append(0)
        return rows, cols
    
    def _generate_analysis_plots(self, results: List[Dict]) -> str:
        """Genera grafici di analisi"""
        print(f"\nGENERAZIONE GRAFICI ANALITICI")
        print("-" * 60)
        
        times = [r['computation_time'] for r in results]
        mhs_counts = [r['mhs_count'] for r in results]
        hypotheses = [r.get('hypotheses_generated', 0) for r in results]
        matrix_sizes = self._extract_matrix_sizes(results)
        rows, cols = self._extract_rows_and_cols(results)
        matrix_sizes_opt = self._extract_matrix_sizes_optimized(results)
        rows_opt, cols_opt = self._extract_rows_and_cols_optimized(results)
        ones, ones_opt = [], []
        file_sizes = [r.get('file_size_mb', 0) for r in results]
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Grafico 1: Distribuzione tempi
            ax1.hist(times, bins=20, alpha=0.7, color='blue', edgecolor='black')
            ax1.axvline(np.mean(times), color='red', linestyle='--', label=f'Media: {np.mean(times):.3f}s')
            ax1.axvline(np.median(times), color='green', linestyle='--', label=f'Mediana: {np.median(times):.3f}s')
            ax1.set_xlabel('Tempo di calcolo (s)')
            ax1.set_ylabel('Frequenza')
            ax1.set_title('Distribuzione Tempi di Calcolo')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Grafico 2: Scatter dimensione vs tempo
            if matrix_sizes:
                ax2.scatter(matrix_sizes, times, alpha=0.6, color='orange')
                ax2.set_xlabel('Dimensione matrice (righe × colonne)')
                ax2.set_ylabel('Tempo di calcolo (s)')
                ax2.set_title('Relazione Dimensione-Tempo')
                ax2.grid(True, alpha=0.3)
            
            # Grafico 3: MHS trovati vs tempo
            ax3.scatter(mhs_counts, times, alpha=0.6, color='green')
            ax3.set_xlabel('Numero MHS trovati')
            ax3.set_ylabel('Tempo di calcolo (s)')
            ax3.set_title('Relazione MHS-Tempo')
            ax3.grid(True, alpha=0.3)
            
            # Grafico 4: Distribuzione ipotesi generate
            ax4.hist(hypotheses, bins=20, alpha=0.7, color='purple', edgecolor='black')
            ax4.axvline(np.mean(hypotheses), color='red', linestyle='--', label=f'Media: {np.mean(hypotheses):.0f}')
            ax4.set_xlabel('Ipotesi generate')
            ax4.set_ylabel('Frequenza')
            ax4.set_title('Distribuzione Complessità Computazionale')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salva grafici
            plot_path = os.path.join(self.output_dir, 'performance_analysis.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"Grafici salvati in: {plot_path}")
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Errore nella generazione dei grafici: {e}")
            return None
    
    def _analyze_theoretical_complexity(self, results: List[Dict]):
        """Analisi della complessità teorica (Big O)"""
        print(f"\nANALISI COMPLESSITÀ TEORICA (BIG O)")
        print("=" * 80)
        
        times = [r['computation_time'] for r in results]
        hypotheses = [r.get('hypotheses_generated', 0) for r in results]
        matrix_sizes = self._extract_matrix_sizes(results)
        
        # Analisi tempo vs dimensione matrice
        self._analyze_time_complexity(matrix_sizes, times)
        
        # Analisi spazio vs dimensione matrice
        self._analyze_space_complexity(matrix_sizes, hypotheses)
        
        # Genera grafico log-log per complessità
        self._generate_complexity_plots(matrix_sizes, times, hypotheses)
    
    def _analyze_time_complexity(self, matrix_sizes: List[int], times: List[float]):
        """Analizza la complessità temporale"""
        print(f"\nCOMPLESSITÀ TEMPORALE")
        print("-" * 40)
        
        # Filtra punti validi
        valid_data = [(s, t) for s, t in zip(matrix_sizes, times) if s > 0 and t > 0]
        
        if len(valid_data) < 3:
            print("Dati insufficienti per l'analisi della complessità temporale")
            return
        
        sizes, times_filtered = zip(*valid_data)
        
        # Calcola coefficienti di correlazione per diverse funzioni
        log_sizes = [np.log(s) for s in sizes]
        log_times = [np.log(t) for t in times_filtered]
        
        # Correlazione lineare (O(n))
        corr_linear = np.corrcoef(sizes, times_filtered)[0, 1] if len(set(sizes)) > 1 else 0
        
        # Correlazione quadratica (O(n²))
        sizes_squared = [s**2 for s in sizes]
        corr_quadratic = np.corrcoef(sizes_squared, times_filtered)[0, 1] if len(set(sizes_squared)) > 1 else 0
        
        # Correlazione esponenziale (O(2^n)) - usando logaritmo
        corr_exponential = np.corrcoef(log_sizes, log_times)[0, 1] if len(set(log_sizes)) > 1 else 0
        
        print(f"Correlazione O(n): {corr_linear:.3f}")
        print(f"Correlazione O(n²): {corr_quadratic:.3f}")
        print(f"Correlazione O(2^n): {corr_exponential:.3f}")
        
        # Stima la complessità più probabile
        complexities = {
            'O(n)': corr_linear,
            'O(n²)': corr_quadratic,
            'O(2^n)': corr_exponential
        }
        
        best_complexity = max(complexities, key=complexities.get)
        print(f"Complessità temporale stimata: {best_complexity}")
    
    def _analyze_space_complexity(self, matrix_sizes: List[int], hypotheses: List[int]):
        """Analizza la complessità spaziale"""
        print(f"\nCOMPLESSITÀ SPAZIALE")
        print("-" * 40)
        
        # Filtra punti validi
        valid_data = [(s, h) for s, h in zip(matrix_sizes, hypotheses) if s > 0 and h > 0]
        
        if len(valid_data) < 3:
            print("Dati insufficienti per l'analisi della complessità spaziale")
            return
        
        sizes, hyp_filtered = zip(*valid_data)
        
        # Correlazione con diverse funzioni
        corr_linear = np.corrcoef(sizes, hyp_filtered)[0, 1] if len(set(sizes)) > 1 else 0
        corr_quadratic = np.corrcoef([s**2 for s in sizes], hyp_filtered)[0, 1] if len(set(sizes)) > 1 else 0
        
        print(f"Correlazione spaziale O(n): {corr_linear:.3f}")
        print(f"Correlazione spaziale O(n²): {corr_quadratic:.3f}")
        
        # Stima memoria
        estimated_memory = [h * 0.001 for h in hyp_filtered]  # 1KB per ipotesi
        print(f"Memoria stimata media: {np.mean(estimated_memory):.2f}MB")
        print(f"Memoria stimata massima: {max(estimated_memory):.2f}MB")
    
    def _generate_complexity_plots(self, matrix_sizes: List[int], times: List[float], 
                                  hypotheses: List[int]):
        """Genera grafici di complessità"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Grafico 1: Log-log plot tempo vs dimensione
            valid_time_data = [(s, t) for s, t in zip(matrix_sizes, times) if s > 0 and t > 0]
            if valid_time_data:
                sizes_time, times_filtered = zip(*valid_time_data)
                ax1.loglog(sizes_time, times_filtered, 'bo-', alpha=0.7)
                ax1.set_xlabel('Dimensione matrice (log)')
                ax1.set_ylabel('Tempo di calcolo (log)')
                ax1.set_title('Complessità Temporale (Log-Log)')
                ax1.grid(True, alpha=0.3)
            
            # Grafico 2: Log-log plot memoria vs dimensione
            valid_space_data = [(s, h) for s, h in zip(matrix_sizes, hypotheses) if s > 0 and h > 0]
            if valid_space_data:
                sizes_space, hyp_filtered = zip(*valid_space_data)
                ax2.loglog(sizes_space, hyp_filtered, 'ro-', alpha=0.7)
                ax2.set_xlabel('Dimensione matrice (log)')
                ax2.set_ylabel('Ipotesi generate (log)')
                ax2.set_title('Complessità Spaziale (Log-Log)')
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salva grafici
            complexity_plot_path = os.path.join(self.output_dir, 'algorithmic_complexity.png')
            plt.savefig(complexity_plot_path, dpi=300, bbox_inches='tight')
            print(f"Grafici complessità salvati in: {complexity_plot_path}")
            plt.close()
            
        except Exception as e:
            print(f"Errore nella generazione dei grafici di complessità: {e}")
    
    def _save_performance_reports(self, results: List[Dict]) -> Tuple[str, str]:
        """Salva report delle prestazioni"""
        print(f"\nSALVATAGGIO REPORT PRESTAZIONI")
        print("-" * 60)
        
        try:
            # Prepara dati per CSV
            csv_path = os.path.join(self.output_dir, 'performance_detailed.csv')
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = ['file', 'matrix_size', 'reduced_size', 'mhs_count', 
                            'computation_time', 'hypotheses_generated', 'levels_explored',
                            'max_level_size', 'timeout', 'size_limit', 'file_size_mb','ones_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for r in results:
                    writer.writerow(r)
            
            # Prepara dati per JSON
            json_path = os.path.join(self.output_dir, 'performance_statistics.json')
            times = [r['computation_time'] for r in results]
            hypotheses = [r.get('hypotheses_generated', 0) for r in results]
            
            stats = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'total_files': len(results),
                'temporal_statistics': {
                    'mean_time': float(np.mean(times)),
                    'median_time': float(np.median(times)),
                    'std_time': float(np.std(times)),
                    'min_time': float(min(times)),
                    'max_time': float(max(times))
                },
                'spatial_statistics': {
                    'mean_hypotheses': float(np.mean(hypotheses)),
                    'median_hypotheses': float(np.median(hypotheses)),
                    'std_hypotheses': float(np.std(hypotheses)),
                    'min_hypotheses': int(min(hypotheses)),
                    'max_hypotheses': int(max(hypotheses))
                },
                'detailed_results': results
            }
            
            with open(json_path, 'w') as jsonfile:
                json.dump(stats, jsonfile, indent=2)
            
            print(f"Report CSV salvato in: {csv_path}")
            print(f"Report JSON salvato in: {json_path}")
            
            return json_path, csv_path
            
        except Exception as e:
            print(f"Errore nel salvataggio dei report: {e}")
            return None, None
