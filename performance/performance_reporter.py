#!/usr/bin/env python3
"""
Performance Reporter for MHS Analysis
====================================

Modulo per la generazione di report, grafici e export dei dati
relativi alle analisi prestazioni degli algoritmi Minimal Hitting Set.
"""

import os
import time
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional

class PerformanceReporter:
    """
    Classe per la generazione di report, grafici e export
    dei dati di analisi delle prestazioni MHS
    """
    
    def __init__(self):
        """Inizializza il reporter prestazioni"""
        pass
    
    def save_performance_reports(self, analysis_report: Dict, files: List[str], 
                               times: List[float], memory_peaks: List[float], 
                               cpu_averages: List[float], complexity_data: Dict,
                               output_dir: str = None) -> Tuple[str, str, str]:
        """
        Salva i report delle prestazioni in JSON e CSV con grafici
        
        Args:
            analysis_report: Report completo dell'analisi
            files: Lista dei file processati
            times: Tempi di esecuzione
            memory_peaks: Picchi di memoria
            cpu_averages: Utilizzo CPU medio
            complexity_data: Dati di complessità
            output_dir: Directory di output personalizzata
            
        Returns:
            tuple: (json_file_path, csv_file_path, analysis_dir)
        """
        # Usa directory personalizzata o default
        if output_dir is None:
            analysis_dir = os.path.join("results", "analysis", "performance")
        else:
            analysis_dir = output_dir
            
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Salva report JSON completo
        json_file = self._save_json_report(analysis_report, analysis_dir)
        
        # Salva riassunto CSV
        csv_file = self._save_csv_summary(files, times, memory_peaks, cpu_averages, 
                                        complexity_data, analysis_dir)
        
        # Genera grafici delle prestazioni
        self._generate_performance_plots(files, times, memory_peaks, cpu_averages, 
                                       complexity_data, analysis_dir)
        
        print(f"\nReport salvati in: {analysis_dir}/")
        print(f"  • Report JSON: {os.path.basename(json_file)}")
        print(f"  • Riassunto CSV: {os.path.basename(csv_file)}")
        print(f"  • Grafici prestazioni: performance_plots_*.png")
        
        return json_file, csv_file, analysis_dir
    
    def _save_json_report(self, analysis_report: Dict, analysis_dir: str) -> str:
        """Salva il report completo in formato JSON"""
        timestamp = int(time.time())
        json_file = os.path.join(analysis_dir, f"advanced_performance_analysis_{timestamp}.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        
        return json_file
    
    def _save_csv_summary(self, files: List[str], times: List[float], 
                         memory_peaks: List[float], cpu_averages: List[float], 
                         complexity_data: Dict, analysis_dir: str) -> str:
        """Salva un riassunto delle prestazioni in formato CSV"""
        timestamp = int(time.time())
        csv_file = os.path.join(analysis_dir, f"performance_summary_{timestamp}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header con tutte le metriche
            writer.writerow([
                'File', 'Tempo_Esecuzione_s', 'Picco_Memoria_MB', 'CPU_Media_%',
                'MHS_Trovati', 'Ipotesi_Generate', 'Livelli_Esplorati', 'Max_Livello_Size',
                'Complessità_Temporale', 'Complessità_Spaziale'
            ])
            
            # Dati per ogni file
            for i, file in enumerate(files):
                filename = os.path.basename(file)
                time_val = times[i] if i < len(times) else 0
                mem_val = memory_peaks[i] if i < len(memory_peaks) else 0
                cpu_val = cpu_averages[i] if i < len(cpu_averages) else 0
                
                # Dati di complessità
                file_complexity = complexity_data.get(file, {})
                mhs_count = file_complexity.get('mhs_count', 0)
                hypotheses = file_complexity.get('hypotheses_generated', 0)
                levels = file_complexity.get('levels_explored', 0)
                max_level = file_complexity.get('max_level_size', 0)
                time_complexity = file_complexity.get('time_complexity_estimate', 'N/A')
                space_complexity = file_complexity.get('space_complexity_estimate', 'N/A')
                
                writer.writerow([
                    filename, f"{time_val:.3f}", f"{mem_val:.1f}", f"{cpu_val:.1f}",
                    mhs_count, hypotheses, levels, max_level, 
                    time_complexity, space_complexity
                ])
        
        return csv_file
    
    def _generate_performance_plots(self, files: List[str], times: List[float], 
                                  memory_peaks: List[float], cpu_averages: List[float], 
                                  complexity_data: Dict, analysis_dir: str):
        """Genera grafici delle prestazioni"""
        if not files or not times:
            print("Dati insufficienti per generare grafici")
            return
        
        # Genera grafici multipli
        self._plot_execution_times(files, times, analysis_dir)
        self._plot_memory_usage(files, memory_peaks, analysis_dir)
        self._plot_cpu_usage(files, cpu_averages, analysis_dir)
        self._plot_complexity_correlation(files, times, complexity_data, analysis_dir)
        self._plot_comprehensive_overview(files, times, memory_peaks, cpu_averages, analysis_dir)
    
    def _plot_execution_times(self, files: List[str], times: List[float], analysis_dir: str):
        """Grafico dei tempi di esecuzione"""
        if not times or all(t == 0 for t in times):
            return
        
        plt.figure(figsize=(12, 6))
        file_names = [os.path.basename(f) for f in files]
        
        plt.bar(range(len(times)), times, color='skyblue', alpha=0.7)
        plt.title('Tempi di Esecuzione per File', fontsize=14, fontweight='bold')
        plt.xlabel('File')
        plt.ylabel('Tempo (secondi)')
        plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Aggiungi statistiche
        mean_time = np.mean(times)
        plt.axhline(y=mean_time, color='red', linestyle='--', alpha=0.7, 
                   label=f'Media: {mean_time:.3f}s')
        plt.legend()
        
        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(os.path.join(analysis_dir, f"performance_plots_times_{timestamp}.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
    
    def _plot_memory_usage(self, files: List[str], memory_peaks: List[float], analysis_dir: str):
        """Grafico dell'utilizzo memoria"""
        if not memory_peaks or all(m == 0 for m in memory_peaks):
            return
        
        plt.figure(figsize=(12, 6))
        file_names = [os.path.basename(f) for f in files]
        
        plt.bar(range(len(memory_peaks)), memory_peaks, color='lightcoral', alpha=0.7)
        plt.title('Picchi di Memoria per File', fontsize=14, fontweight='bold')
        plt.xlabel('File')
        plt.ylabel('Memoria (MB)')
        plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Aggiungi statistiche
        mean_memory = np.mean(memory_peaks)
        plt.axhline(y=mean_memory, color='red', linestyle='--', alpha=0.7,
                   label=f'Media: {mean_memory:.1f}MB')
        plt.legend()
        
        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(os.path.join(analysis_dir, f"performance_plots_memory_{timestamp}.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
    
    def _plot_cpu_usage(self, files: List[str], cpu_averages: List[float], analysis_dir: str):
        """Grafico dell'utilizzo CPU"""
        if not cpu_averages or all(c == 0 for c in cpu_averages):
            return
        
        plt.figure(figsize=(12, 6))
        file_names = [os.path.basename(f) for f in files]
        
        plt.bar(range(len(cpu_averages)), cpu_averages, color='lightgreen', alpha=0.7)
        plt.title('Utilizzo CPU Medio per File', fontsize=14, fontweight='bold')
        plt.xlabel('File')
        plt.ylabel('CPU (%)')
        plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Aggiungi statistiche
        mean_cpu = np.mean(cpu_averages)
        plt.axhline(y=mean_cpu, color='red', linestyle='--', alpha=0.7,
                   label=f'Media: {mean_cpu:.1f}%')
        plt.legend()
        
        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(os.path.join(analysis_dir, f"performance_plots_cpu_{timestamp}.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
    
    def _plot_complexity_correlation(self, files: List[str], times: List[float], 
                                   complexity_data: Dict, analysis_dir: str):
        """Grafico correlazione complessità-prestazioni"""
        if not complexity_data:
            return
        
        # Estrai dati di complessità
        hypotheses = [complexity_data.get(f, {}).get('hypotheses_generated', 0) for f in files]
        levels = [complexity_data.get(f, {}).get('levels_explored', 0) for f in files]
        
        if not any(hypotheses) or not any(times):
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Correlazione ipotesi-tempo
        ax1.scatter(hypotheses, times, alpha=0.7, color='blue')
        ax1.set_xlabel('Ipotesi Generate')
        ax1.set_ylabel('Tempo Esecuzione (s)')
        ax1.set_title('Correlazione Ipotesi-Tempo')
        ax1.grid(True, alpha=0.3)
        
        # Aggiungi linea di tendenza se ci sono almeno 2 punti
        if len(hypotheses) > 1 and np.std(hypotheses) > 0:
            z = np.polyfit(hypotheses, times, 1)
            p = np.poly1d(z)
            ax1.plot(hypotheses, p(hypotheses), "r--", alpha=0.8)
            correlation = np.corrcoef(hypotheses, times)[0,1]
            ax1.text(0.05, 0.95, f'Correlazione: {correlation:.3f}', 
                    transform=ax1.transAxes, verticalalignment='top')
        
        # Correlazione livelli-tempo
        ax2.scatter(levels, times, alpha=0.7, color='green')
        ax2.set_xlabel('Livelli Esplorati')
        ax2.set_ylabel('Tempo Esecuzione (s)')
        ax2.set_title('Correlazione Livelli-Tempo')
        ax2.grid(True, alpha=0.3)
        
        # Aggiungi linea di tendenza se ci sono almeno 2 punti
        if len(levels) > 1 and np.std(levels) > 0:
            z = np.polyfit(levels, times, 1)
            p = np.poly1d(z)
            ax2.plot(levels, p(levels), "r--", alpha=0.8)
            correlation = np.corrcoef(levels, times)[0,1]
            ax2.text(0.05, 0.95, f'Correlazione: {correlation:.3f}', 
                    transform=ax2.transAxes, verticalalignment='top')
        
        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(os.path.join(analysis_dir, f"performance_plots_complexity_{timestamp}.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
    
    def _plot_comprehensive_overview(self, files: List[str], times: List[float], 
                                   memory_peaks: List[float], cpu_averages: List[float], 
                                   analysis_dir: str):
        """Grafico panoramico di tutte le metriche"""
        if not files or not times:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        file_names = [os.path.basename(f) for f in files]
        
        # Tempi di esecuzione
        if times and any(t > 0 for t in times):
            ax1.plot(range(len(times)), times, 'o-', color='blue', linewidth=2, markersize=6)
            ax1.set_title('Tempi di Esecuzione', fontweight='bold')
            ax1.set_ylabel('Tempo (s)')
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(range(len(file_names)))
            ax1.set_xticklabels(file_names, rotation=45, ha='right')
        
        # Memoria
        if memory_peaks and any(m > 0 for m in memory_peaks):
            ax2.plot(range(len(memory_peaks)), memory_peaks, 'o-', color='red', linewidth=2, markersize=6)
            ax2.set_title('Picchi di Memoria', fontweight='bold')
            ax2.set_ylabel('Memoria (MB)')
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(range(len(file_names)))
            ax2.set_xticklabels(file_names, rotation=45, ha='right')
        
        # CPU
        if cpu_averages and any(c > 0 for c in cpu_averages):
            ax3.plot(range(len(cpu_averages)), cpu_averages, 'o-', color='green', linewidth=2, markersize=6)
            ax3.set_title('Utilizzo CPU Medio', fontweight='bold')
            ax3.set_ylabel('CPU (%)')
            ax3.grid(True, alpha=0.3)
            ax3.set_xticks(range(len(file_names)))
            ax3.set_xticklabels(file_names, rotation=45, ha='right')
        
        # Distribuzione tempi (istogramma)
        if times and len(times) > 1:
            ax4.hist(times, bins=min(10, len(times)), alpha=0.7, color='skyblue', edgecolor='black')
            ax4.set_title('Distribuzione Tempi di Esecuzione', fontweight='bold')
            ax4.set_xlabel('Tempo (s)')
            ax4.set_ylabel('Frequenza')
            ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Panoramica Prestazioni MHS', fontsize=16, fontweight='bold')
        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(os.path.join(analysis_dir, f"performance_plots_overview_{timestamp}.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
    
    def save_single_execution_plot(self, monitor_data: Dict, output_dir: str, filename: str):
        """
        Salva i grafici per una singola esecuzione (CPU e memoria nel tempo)
        
        Args:
            monitor_data: Dati di monitoraggio con time_samples, cpu_samples, memory_samples
            output_dir: Directory di output
            filename: Nome base del file
        """
        if not monitor_data.get('time_samples') or not monitor_data.get('cpu_samples'):
            print("Dati di monitoraggio insufficienti per generare grafici")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        plt.figure(figsize=(12, 4))
        
        # Grafico CPU
        plt.subplot(1, 2, 1)
        plt.plot(monitor_data['time_samples'], monitor_data['cpu_samples'], 'b-', linewidth=1)
        plt.title('Utilizzo CPU nel tempo')
        plt.xlabel('Tempo (s)')
        plt.ylabel('CPU (%)')
        plt.grid(True, alpha=0.3)
        
        # Grafico Memoria
        plt.subplot(1, 2, 2)
        plt.plot(monitor_data['time_samples'], monitor_data['memory_samples'], 'r-', linewidth=1)
        plt.title('Utilizzo Memoria nel tempo')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Memoria (MB)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        graph_file = os.path.join(output_dir, f"{filename}_performance.png")
        plt.savefig(graph_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return graph_file
    
    def generate_comprehensive_report(self, results_data: Dict, performance_data: Dict, output_dir: str = None) -> Optional[str]:
        """
        Genera un report completo con grafici e analisi comparative
        
        Crea visualizzazioni grafiche dei risultati dell'esperimento di confronto
        includendo tempi di calcolo, numero di MHS trovati, relazioni complessità-tempo
        e utilizzo delle risorse hardware. Salva il report come file PNG.
        
        Args:
            results_data: Dizionario con i risultati MHS per file
            performance_data: Dizionario con i dati prestazioni per file
            output_dir: Directory di output personalizzata
            
        Returns:
            str: Path del file grafico generato o None se errore
        """
        if not results_data:
            print("Nessun dato per il report")
            return None
        
        # Usa directory personalizzata o default
        if output_dir is None:
            reports_dir = os.path.join("results", "analysis")
        else:
            reports_dir = output_dir
            
        os.makedirs(reports_dir, exist_ok=True)
        
        try:
            # Crea grafici comparativi
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Dati per i grafici
            files = list(results_data.keys())
            times = [results_data[f][1]['computation_time'] for f in files if len(results_data[f]) > 1]
            mhs_counts = [results_data[f][1]['num_mhs'] for f in files if len(results_data[f]) > 1]
            hypotheses = [results_data[f][1]['hypotheses_generated'] for f in files if len(results_data[f]) > 1]
            file_labels = [os.path.basename(f)[:15] for f in files]
            
            # Grafico 1: Tempi di calcolo
            if times:
                ax1.bar(range(len(files)), times, color='skyblue', alpha=0.7)
                ax1.set_xlabel('File di permutazione')
                ax1.set_ylabel('Tempo (s)')
                ax1.set_title('Tempi di Calcolo per Permutazione')
                ax1.set_xticks(range(len(files)))
                ax1.set_xticklabels(file_labels, rotation=45, ha='right')
                ax1.grid(True, alpha=0.3)
            
            # Grafico 2: Numero MHS
            if mhs_counts:
                ax2.bar(range(len(files)), mhs_counts, color='lightgreen', alpha=0.7)
                ax2.set_xlabel('File di permutazione')
                ax2.set_ylabel('Numero MHS')
                ax2.set_title('MHS Trovati per Permutazione')
                ax2.set_xticks(range(len(files)))
                ax2.set_xticklabels(file_labels, rotation=45, ha='right')
                ax2.grid(True, alpha=0.3)
            
            # Grafico 3: Scatter tempo vs ipotesi
            if hypotheses and times:
                ax3.scatter(hypotheses, times, alpha=0.6, color='orange', s=60)
                ax3.set_xlabel('Ipotesi Generate')
                ax3.set_ylabel('Tempo (s)')
                ax3.set_title('Relazione Complessità-Tempo')
                ax3.grid(True, alpha=0.3)
            
            # Grafico 4: Performance hardware (se disponibili)
            if performance_data:
                hw_files = []
                memory_usage = []
                cpu_usage = []
                
                for f in files:
                    if f in performance_data:
                        hw_files.append(os.path.basename(f)[:15])
                        memory_usage.append(performance_data[f].get('peak_memory_mb', 0))
                        cpu_usage.append(performance_data[f].get('avg_cpu_percent', 0))
                
                if memory_usage:
                    ax4_twin = ax4.twinx()
                    bars1 = ax4.bar([i-0.2 for i in range(len(hw_files))], memory_usage, 
                                   width=0.4, label='Memoria (MB)', color='purple', alpha=0.7)
                    bars2 = ax4_twin.bar([i+0.2 for i in range(len(hw_files))], cpu_usage, 
                                        width=0.4, label='CPU (%)', color='red', alpha=0.7)
                    
                    ax4.set_xlabel('File di permutazione')
                    ax4.set_ylabel('Memoria (MB)', color='purple')
                    ax4_twin.set_ylabel('CPU (%)', color='red')
                    ax4.set_title('Utilizzo Risorse Hardware')
                    ax4.set_xticks(range(len(hw_files)))
                    ax4.set_xticklabels(hw_files, rotation=45, ha='right')
                    ax4.grid(True, alpha=0.3)
                else:
                    ax4.text(0.5, 0.5, 'Dati hardware\nnon disponibili', 
                            ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                    ax4.set_title('Monitoraggio Hardware')
            else:
                ax4.text(0.5, 0.5, 'Dati hardware\nnon disponibili', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Monitoraggio Hardware')
            
            plt.tight_layout()
            
            # Salva i grafici nella directory specificata
            timestamp = int(time.time())
            report_file = os.path.join(reports_dir, f"permutation_analysis_report_{timestamp}.png")
            plt.savefig(report_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return report_file
        except KeyboardInterrupt:
            raise    
        except Exception as e:
            print(f"Errore nella generazione grafici: {e}")
            return None
