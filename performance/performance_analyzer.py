#!/usr/bin/env python3
"""
Performance Analyzer for MHS Analysis
====================================

Modulo per l'analisi avanzata delle prestazioni e complessità computazionale
degli algoritmi Minimal Hitting Set.
"""

import os
import time
import numpy as np
from typing import Dict, List

class PerformanceAnalyzer:
    """
    Classe per l'analisi avanzata delle prestazioni e complessità
    Gestisce analisi comparative su multiple esecuzioni MHS
    """
    
    def __init__(self):
        """Inizializza l'analizzatore prestazioni"""
        self.analysis_files = {}
        
    def analyze_comprehensive_performance(self, performance_data: Dict, results_data: Dict, output_dir: str = None):
        """
        Esegue analisi prestazioni avanzate sui risultati e salva i report
        
        Args:
            performance_data: Dati prestazioni raccolti {file: stats}
            results_data: Dati risultati MHS {file: (mhs_list, statistics)}
            output_dir: Directory di output personalizzata (default: results/analysis/performance)
            
        Returns:
            tuple: (json_file_path, csv_file_path, analysis_dir)
        """
        if not performance_data:
            print("Nessun dato prestazioni disponibile per analisi avanzate")
            return None, None, None
        
        # Usa directory personalizzata o default
        if output_dir is None:
            output_dir = os.path.join("results", "analysis", "performance")
        
        print("\n")
        print("=" * 50)
        print("ANALISI PRESTAZIONI AVANZATE")
        print("=" * 50)
        print("\n")
        
        # Estrai metriche
        files = list(performance_data.keys())
        times = []
        memory_peaks = []
        cpu_averages = []
        
        for file in files:
            perf = performance_data[file]
            times.append(perf.get('execution_time', 0))
            memory_peaks.append(perf.get('peak_memory_mb', 0))
            cpu_averages.append(perf.get('avg_cpu_percent', 0))
        
        # Raccogli dati sulla complessità per il report
        complexity_data = {}
        for file, (mhs_list, stats) in results_data.items():
            complexity_data[file] = {
                'mhs_count': len(mhs_list) if mhs_list else 0,
                'hypotheses_generated': stats.get('hypotheses_generated', 0),
                'levels_explored': len(stats.get('levels_generated', [])),
                'max_level_size': max(stats.get('levels_generated', [0])) if stats.get('levels_generated') else 0,
                'time_complexity_estimate': stats.get('time_complexity_estimate', 'N/A'),
                'space_complexity_estimate': stats.get('space_complexity_estimate', 'N/A')
            }

        # Crea report dettagliato con tutte le metriche
        analysis_report = self._create_comprehensive_report(
            files, times, memory_peaks, cpu_averages, complexity_data
        )
        
        # Stampa analisi temporali
        self._print_temporal_analysis(times, files)
        
        # Stampa analisi memoria/CPU
        self._print_hardware_analysis(memory_peaks, cpu_averages)
        
        # Stampa analisi spaziali dettagliate
        self._print_spatial_analysis(memory_peaks, times, files, results_data)
        
        # Salva report (importa qui per evitare dipendenze circolari)
        from .performance_reporter import PerformanceReporter
        reporter = PerformanceReporter()
        return reporter.save_performance_reports(analysis_report, files, times, memory_peaks, 
                                               cpu_averages, complexity_data, output_dir)
    
    def _create_comprehensive_report(self, files, times, memory_peaks, cpu_averages, complexity_data):
        """Crea il report comprensivo con tutte le metriche"""
        return {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_permutations': len(files),
            'performance_metrics': {
                'execution_times': {
                    'mean': float(np.mean(times)) if times else 0,
                    'std': float(np.std(times)) if times else 0,
                    'min': float(min(times)) if times else 0,
                    'max': float(max(times)) if times else 0,
                    'all_times': times
                },
                'memory_usage': {
                    'mean_peak': float(np.mean(memory_peaks)) if memory_peaks else 0,
                    'max_peak': float(max(memory_peaks)) if memory_peaks else 0,
                    'all_peaks': memory_peaks
                },
                'cpu_usage': {
                    'mean_avg': float(np.mean(cpu_averages)) if cpu_averages else 0,
                    'max_avg': float(max(cpu_averages)) if cpu_averages else 0,
                    'all_averages': cpu_averages
                }
            },
            'complexity_analysis': {
                'hypotheses_mean': float(np.mean([data['hypotheses_generated'] for data in complexity_data.values()])) if complexity_data else 0,
                'levels_mean': float(np.mean([data['levels_explored'] for data in complexity_data.values()])) if complexity_data else 0,
                'time_hypotheses_correlation': float(np.corrcoef([complexity_data[f]['hypotheses_generated'] for f in files], times)[0,1]) if len(files) > 1 and complexity_data else 0
            },
            'file_details': self._create_file_details(files, times, memory_peaks, cpu_averages, complexity_data)
        }
    
    def _create_file_details(self, files, times, memory_peaks, cpu_averages, complexity_data):
        """Crea i dettagli per ogni file"""
        file_details = {}
        for i, file in enumerate(files):
            filename = os.path.basename(file)
            file_complexity = complexity_data.get(file, {})
            file_details[filename] = {
                'execution_time': times[i] if i < len(times) else 0,
                'memory_peak': memory_peaks[i] if i < len(memory_peaks) else 0,
                'cpu_average': cpu_averages[i] if i < len(cpu_averages) else 0,
                'mhs_count': file_complexity.get('mhs_count', 0),
                'hypotheses_generated': file_complexity.get('hypotheses_generated', 0),
                'levels_explored': file_complexity.get('levels_explored', 0),
                'max_level_size': file_complexity.get('max_level_size', 0),
                'time_complexity_estimate': file_complexity.get('time_complexity_estimate', 'N/A'),
                'space_complexity_estimate': file_complexity.get('space_complexity_estimate', 'N/A')
            }
        return file_details
    
    def _print_temporal_analysis(self, times, files):
        """Stampa analisi delle prestazioni temporali"""
        if times:
            print("Prestazioni temporali:")
            print(f"   • Tempo medio: {np.mean(times):.3f}s")
            print(f"   • Deviazione std: {np.std(times):.3f}s")
            print(f"   • Range: {min(times):.3f}s - {max(times):.3f}s")
            print(f"   • Tempo minimo: {min(times):.3f}s")
            print(f"   • Tempo massimo: {max(times):.3f}s")
            print(f"   • Rapporto max/min: {max(times)/min(times):.2f}x")
            
            # Identifica outliers prestazionali
            mean_time = np.mean(times)
            std_time = np.std(times)
            threshold = mean_time + 2 * std_time
            
            slow_files = [files[i] for i, t in enumerate(times) if t > threshold]
            if slow_files:
                print(f"   • File lenti (>{threshold:.3f}s): {len(slow_files)}")
                for f in slow_files[:3]:  # Mostra i primi 3
                    idx = files.index(f)
                    print(f"     - {os.path.basename(f)}: {times[idx]:.3f}s")
    
    def _print_hardware_analysis(self, memory_peaks, cpu_averages):
        """Stampa analisi utilizzo hardware"""
        if memory_peaks and any(m > 0 for m in memory_peaks):
            print(f"\nUtilizzo memoria:")
            print(f"   • Picco medio: {np.mean(memory_peaks):.2f}MB")
            print(f"   • Picco massimo: {max(memory_peaks):.2f}MB")
            print(f"   • Variabilità: {np.std(memory_peaks):.2f}MB")
        else:
            print(f"\nUtilizzo memoria:")
            print(f"   • Dati non disponibili (possibile problema di monitoraggio)")
        
        if cpu_averages and any(c > 0 for c in cpu_averages):
            print(f"\nUtilizzo CPU:")
            print(f"   • Media generale: {np.mean(cpu_averages):.1f}%")
            print(f"   • Massimo carico: {max(cpu_averages):.1f}%")
            print(f"   • Efficienza: {min(cpu_averages):.1f}% - {max(cpu_averages):.1f}%")
        else:
            print(f"\nUtilizzo CPU:")
            print(f"   • Dati non disponibili (calcoli troppo veloci per il campionamento)")
    
    def _print_spatial_analysis(self, memory_peaks, times, files, results_data):
        """Stampa analisi prestazioni spaziali dettagliate"""
        print("\n")
        print("=" * 50)
        print("PRESTAZIONI SPAZIALI")
        print("=" * 50)
        print("\n")

        if memory_peaks and any(m > 0 for m in memory_peaks):
            # Calcola statistiche spaziali avanzate
            hypotheses_list = [results_data[f][1].get('hypotheses_generated', 0) for f in files]
            
            print(" Statistiche memoria:")
            print(f"      • Allocazione media: {np.mean(memory_peaks):.2f}MB")
            print(f"      • Picco massimo assoluto: {max(memory_peaks):.2f}MB")
            print(f"      • Picco minimo: {min(memory_peaks):.2f}MB")
            print(f"      • Stabilità allocazione: ±{np.std(memory_peaks):.2f}MB")
            print(f"      • Range utilizzo: {max(memory_peaks) - min(memory_peaks):.2f}MB")
            
            # Correlazione memoria-complessità
            if hypotheses_list and any(h > 0 for h in hypotheses_list):
                correlation = np.corrcoef(memory_peaks, hypotheses_list)[0,1]
                print(" Correlazioni:")
                print(f"      • Memoria-ipotesi: {correlation:.3f}")
                if abs(correlation) > 0.7:
                    print(f"        → Correlazione {'forte' if correlation > 0 else 'forte inversa'}")
                elif abs(correlation) > 0.3:
                    print(f"        → Correlazione moderata")
                else:
                    print(f"        → Memoria indipendente dalla complessità")
                
                # Analisi efficienza spaziale
                avg_memory_per_hypothesis = np.mean([m/h if h > 0 else 0 
                                                   for m, h in zip(memory_peaks, hypotheses_list)])
                print(f"      • Efficienza spaziale: {avg_memory_per_hypothesis:.3f}MB/ipotesi")
            
            # Classificazione uso memoria
            memory_range = max(memory_peaks) - min(memory_peaks)
            if memory_range < 1.0:
                efficiency = "ottima"
                efficiency_note = "uso memoria molto consistente"
            elif memory_range < 5.0:
                efficiency = "buona"
                efficiency_note = "variazioni moderate"
            else:
                efficiency = "variabile"
                efficiency_note = "uso memoria non uniforme"
            
            print(" Efficienza spaziale:")
            print(f"      • Consistenza: {efficiency} ({efficiency_note})")
            print(f"      • Overhead variabile: {(memory_range/np.mean(memory_peaks)*100):.1f}%")
            
            # Correlazione memoria-tempo se disponibile
            if times and len(times) == len(memory_peaks):
                time_memory_corr = np.corrcoef(times, memory_peaks)[0,1]
                print(f"      • Correlazione tempo-memoria: {time_memory_corr:.3f}")
        else:
            print(" Monitoraggio spaziale: non disponibile")
            print("      • Possibili cause: calcoli troppo veloci, errori di campionamento")
            print("      • Raccomandazione: testare con matrici più grandi")
    
    def analyze_complexity(self, results_data: Dict, performance_data: Dict):
        """
        Genera analisi della complessità computazionale
        
        Args:
            results_data: Dati risultati MHS {file: (mhs_list, statistics)}
            performance_data: Dati prestazioni {file: stats}
        """
        if not results_data:
            return
        
        print("\n")
        print("=" * 50)
        print("ANALISI COMPLESSITÀ COMPUTAZIONALE")
        print("=" * 50)
        print("\n")
        
        # Raccogli dati sulla complessità
        complexity_data = []
        
        for file, (mhs_list, stats) in results_data.items():
            data = {
                'file': os.path.basename(file),
                'mhs_count': len(mhs_list) if mhs_list else 0,
                'hypotheses_generated': stats.get('hypotheses_generated', 0),
                'levels_explored': len(stats.get('levels_generated', [])),
                'max_level_size': max(stats.get('levels_generated', [0])) if stats.get('levels_generated') else 0,
                'execution_time': performance_data.get(file, {}).get('execution_time', 0)
            }
            complexity_data.append(data)
        
        if complexity_data:
            # Calcola metriche di complessità
            hypotheses = [d['hypotheses_generated'] for d in complexity_data]
            levels = [d['levels_explored'] for d in complexity_data]
            times = [d['execution_time'] for d in complexity_data]
            
            print("Metriche complessità:")
            print(f"   • Ipotesi generate (media): {np.mean(hypotheses):.0f}")
            print(f"   • Livelli esplorati (media): {np.mean(levels):.1f}")
            if len(hypotheses) > 1 and len(times) > 1:
                print(f"   • Correlazione ipotesi-tempo: {np.corrcoef(hypotheses, times)[0,1]:.3f}")
            
            # Mostra stime di complessità per ogni file
            print("\nStime complessità per file:")
            for file, (mhs_list, stats) in results_data.items():
                filename = os.path.basename(file)
                time_complexity = stats.get('time_complexity_estimate', 'N/A')
                space_complexity = stats.get('space_complexity_estimate', 'N/A')
                print(f"   • {filename}:")
                print(f"     - Tempo: {time_complexity}")
                print(f"     - Spazio: {space_complexity}")
            
            # Aggiungi analisi complessità spaziale
            memory_peaks = [performance_data.get(file, {}).get('peak_memory_mb', 0) 
                           for file, _ in results_data.items()]
            if memory_peaks and any(m > 0 for m in memory_peaks):
                print("\nAnalisi spaziale:")
                print(f"   • Memoria media: {np.mean(memory_peaks):.2f}MB")
                if len(hypotheses) > 1 and len(memory_peaks) > 1:
                    print(f"   • Correlazione ipotesi-memoria: {np.corrcoef(hypotheses, memory_peaks)[0,1]:.3f}")
            else:
                print("\nAnalisi spaziale:")
                print(f"   • Memoria: dati non disponibili o non significativi")
            
            # Classifica per complessità
            complexity_scores = []
            for d in complexity_data:
                # Score basato su ipotesi generate e tempo
                score = (d['hypotheses_generated'] * 0.7 + d['execution_time'] * 100 * 0.3)
                complexity_scores.append((d['file'], score, d))
            
            complexity_scores.sort(key=lambda x: x[1])
            
            print("\nClassifica complessità (dal più semplice):")
            for i, (file, score, data) in enumerate(complexity_scores[:5]):
                print(f"   {i+1}. {file}: {data['hypotheses_generated']} ipotesi, {data['execution_time']:.3f}s")
            
            if len(complexity_scores) > 5:
                print(f"   ... e altri {len(complexity_scores)-5} file")
                
                # Mostra i più complessi
                print("\nFile più complessi:")
                for file, score, data in complexity_scores[-3:]:
                    print(f"   • {file}: {data['hypotheses_generated']} ipotesi, {data['execution_time']:.3f}s")
        
        # Analisi stabilità algoritmo
        print("\n")
        print("=" * 50)
        print("ANALISI STABILITÀ ALGORITMO")
        print("=" * 50)
        
        mhs_counts = [len(mhs_list) if mhs_list else 0 for mhs_list, _ in results_data.values()]
        if mhs_counts and len(set(mhs_counts)) > 1:
            print("\nATTENZIONE: Differenze nel numero di MHS trovati!")
            print(f"   Range: {min(mhs_counts)} - {max(mhs_counts)} MHS")
            print(f"   Questo potrebbe indicare errori nell'algoritmo.")
        else:
            print("Stabilità algoritmo: tutti i file producono lo stesso numero di MHS")
    
    def get_analysis_files_summary(self):
        """
        Restituisce un riepilogo dei file di analisi generati
        
        Returns:
            dict: Dizionario con i percorsi dei file generati o None se non disponibili
        """
        return getattr(self, 'analysis_files', None)
    
    def print_analysis_files_summary(self):
        """
        Stampa un riepilogo dei file di analisi disponibili
        """
        files = self.get_analysis_files_summary()
        if files:
            print("\n" + "=" * 50)
            print("FILE DI ANALISI DISPONIBILI")
            print("=" * 50)
            print("\nReport dettagliati:")
            if files.get('json_report'):
                print(f"   • Report JSON completo: {files['json_report']}")
            if files.get('csv_summary'):
                print(f"   • Riassunto CSV: {files['csv_summary']}")
            if files.get('reports_dir'):
                print(f"   • Grafici e visualizzazioni: {files['reports_dir']}/")
    
    def set_analysis_files(self, json_report, csv_summary, reports_dir):
        """Imposta i percorsi dei file di analisi per il report finale"""
        self.analysis_files = {
            'json_report': json_report,
            'csv_summary': csv_summary,
            'reports_dir': reports_dir
        }
    
    def generate_comprehensive_report(self, results_data: Dict, performance_data: Dict, output_dir: str = None):
        """
        Genera un report completo con grafici e analisi comparative
        
        Delega al PerformanceReporter per la generazione del report grafico
        
        Args:
            results_data: Dizionario con i risultati MHS per file
            performance_data: Dizionario con i dati prestazioni per file
            output_dir: Directory di output personalizzata
            
        Returns:
            str: Path del file grafico generato o None se errore
        """
        from .performance_reporter import PerformanceReporter
        reporter = PerformanceReporter()
        return reporter.generate_comprehensive_report(results_data, performance_data, output_dir)
