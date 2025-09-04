#!/usr/bin/env python3
"""
Pattern Analyzer for Permutation Performance Analysis
====================================================

Modulo specifico per l'identificazione di pattern nelle variazioni prestazionali
tra diverse permutazioni della stessa matrice MHS.
"""

import os
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=np.RankWarning)
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import statistics
import math

class PermutationPatternAnalyzer:
    """
    Classe per l'analisi specifica dei pattern prestazionali tra permutazioni
    """
    
    def __init__(self, execution_manager=None):
        """
        Inizializza l'analizzatore di pattern
        
        Args:
            execution_manager: Gestore dell'esecuzione per organizzare i file output
        """
        self.pattern_results = {}
        self.execution_manager = execution_manager
        
    def analyze_performance_patterns(self, results_data: Dict, performance_data: Dict) -> Dict:
        """
        Analizza i pattern prestazionali tra le permutazioni
        
        Args:
            results_data: Dati risultati MHS {file: (mhs_list, statistics)}
            performance_data: Dati prestazioni {file: stats}
            
        Returns:
            Dict con l'analisi dei pattern
        """
        if not results_data:
            return {}
        
        print("\n" + "=" * 60)
        print("ANALISI PATTERN PRESTAZIONALI PERMUTAZIONI")
        print("=" * 60)
        
        # Estrai dati per l'analisi
        files = list(results_data.keys())
        times = [results_data[f][1]['computation_time'] for f in files]
        hypotheses = [results_data[f][1]['hypotheses_generated'] for f in files]
        memory_peaks = [performance_data.get(f, {}).get('peak_memory_mb', 0) for f in files]
        
        # Calcola statistiche pattern
        pattern_analysis = self._calculate_pattern_statistics(times, hypotheses, memory_peaks, files)
        
        # Identifica outlier prestazionali
        performance_outliers = self._identify_performance_outliers(times, files)
        
        # Analizza stabilità algoritmo
        stability_analysis = self._analyze_algorithm_stability(times, hypotheses)
        
        # Classifica pattern di variazione
        variation_patterns = self._classify_variation_patterns(times, files)
        
        # Stampa risultati analisi
        self._print_pattern_analysis(pattern_analysis, performance_outliers, 
                                   stability_analysis, variation_patterns)
        
        # Salva risultati per report
        self.pattern_results = {
            'pattern_statistics': pattern_analysis,
            'performance_outliers': performance_outliers,
            'stability_analysis': stability_analysis,
            'variation_patterns': variation_patterns,
            'raw_data': {
                'files': files,
                'times': times,
                'hypotheses': hypotheses,
                'memory_peaks': memory_peaks
            }
        }
        
        return self.pattern_results
    
    def _calculate_pattern_statistics(self, times: List[float], hypotheses: List[int], 
                                    memory_peaks: List[float], files: List[str]) -> Dict:
        """Calcola statistiche specifiche per i pattern"""
        if not times:
            return {}
        # Controllo per correlazione robusta
        def safe_corrcoef(x, y):
            if len(x) <= 1 or len(set(x)) <= 1 or len(set(y)) <= 1:
                return float('nan')
            try:
                return np.corrcoef(x, y)[0, 1]
            except Exception:
                return float('nan')
        return {
            'time_statistics': {
                'mean': np.mean(times),
                'std': np.std(times),
                'cv': np.std(times) / np.mean(times) if np.mean(times) > 0 else 0,
                'min': min(times),
                'max': max(times),
                'range_ratio': max(times) / min(times) if min(times) > 0 else float('inf')
            },
            'hypothesis_statistics': {
                'mean': np.mean(hypotheses),
                'std': np.std(hypotheses),
                'cv': np.std(hypotheses) / np.mean(hypotheses) if np.mean(hypotheses) > 0 else 0
            },
            'memory_statistics': {
                'mean': np.mean(memory_peaks) if any(m > 0 for m in memory_peaks) else 0,
                'std': np.std(memory_peaks) if any(m > 0 for m in memory_peaks) else 0,
                'available': any(m > 0 for m in memory_peaks)
            },
            'correlations': {
                'time_hypothesis': safe_corrcoef(times, hypotheses),
                'time_memory': safe_corrcoef(times, memory_peaks) if any(m > 0 for m in memory_peaks) else float('nan')
            }
        }
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calcola percentile usando solo librerie native"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        index = (percentile / 100) * (n - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(math.floor(index))
            upper_index = int(math.ceil(index))
            if upper_index >= n:
                return sorted_values[-1]
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    def _calculate_zscore(self, values: List[float]) -> List[float]:
        """Calcola Z-score usando solo librerie native"""
        if len(values) < 2:
            return [0.0] * len(values)
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        if std_val == 0:
            return [0.0] * len(values)
        
        return [(v - mean_val) / std_val for v in values]
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """Calcola skewness usando solo librerie native"""
        if len(values) < 3:
            return 0.0
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        if std_val == 0:
            return 0.0
        
        n = len(values)
        skew_sum = sum(((v - mean_val) / std_val) ** 3 for v in values)
        return (n / ((n - 1) * (n - 2))) * skew_sum
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calcola kurtosis usando solo librerie native"""
        if len(values) < 4:
            return 0.0
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        if std_val == 0:
            return 0.0
        
        n = len(values)
        kurt_sum = sum(((v - mean_val) / std_val) ** 4 for v in values)
        kurt = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * kurt_sum
        kurt -= 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
        return kurt
    
    def _identify_performance_outliers(self, times: List[float], files: List[str]) -> Dict:
        """Identifica outlier prestazionali usando analisi statistica"""
        if len(times) < 3:
            return {'outliers': [], 'method': 'insufficient_data'}
        
        # Metodo 1: Z-score (2 deviazioni standard)
        z_scores = [abs(z) for z in self._calculate_zscore(times)]
        z_outliers = [i for i, z in enumerate(z_scores) if z > 2]
        
        # Metodo 2: IQR (Interquartile Range)
        q1 = self._calculate_percentile(times, 25)
        q3 = self._calculate_percentile(times, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = [i for i, t in enumerate(times) if t < lower_bound or t > upper_bound]
        
        # Combina risultati
        outlier_indices = list(set(z_outliers + iqr_outliers))
        
        outliers = []
        for idx in outlier_indices:
            outliers.append({
                'index': idx,
                'file': os.path.basename(files[idx]),
                'time': times[idx],
                'z_score': z_scores[idx],
                'deviation_from_mean': (times[idx] - np.mean(times)) / np.std(times),
                'type': 'slow' if times[idx] > np.mean(times) else 'fast'
            })
        
        return {
            'outliers': outliers,
            'total_outliers': len(outliers),
            'outlier_percentage': len(outliers) / len(times) * 100,
            'method': 'zscore_and_iqr'
        }
    
    def _analyze_algorithm_stability(self, times: List[float], hypotheses: List[int]) -> Dict:
        """Analizza la stabilità dell'algoritmo tra permutazioni"""
        if len(times) < 2:
            return {'stability': 'unknown', 'reason': 'insufficient_data'}
        
        time_cv = np.std(times) / np.mean(times) if np.mean(times) > 0 else 0
        hyp_cv = np.std(hypotheses) / np.mean(hypotheses) if np.mean(hypotheses) > 0 else 0
        
        # Classifica stabilità basata su coefficiente di variazione
        if time_cv < 0.1:
            time_stability = 'very_stable'
        elif time_cv < 0.3:
            time_stability = 'stable'
        elif time_cv < 0.5:
            time_stability = 'moderately_stable'
        else:
            time_stability = 'unstable'
        
        if hyp_cv < 0.05:
            hypothesis_stability = 'very_stable'
        elif hyp_cv < 0.15:
            hypothesis_stability = 'stable'
        elif hyp_cv < 0.3:
            hypothesis_stability = 'moderately_stable'
        else:
            hypothesis_stability = 'unstable'
        
        return {
            'time_stability': time_stability,
            'time_cv': time_cv,
            'hypothesis_stability': hypothesis_stability,
            'hypothesis_cv': hyp_cv,
            'overall_stability': 'stable' if time_cv < 0.3 and hyp_cv < 0.15 else 'variable',
            'performance_predictability': 'high' if time_cv < 0.2 else 'medium' if time_cv < 0.4 else 'low'
        }
    
    def _classify_variation_patterns(self, times: List[float], files: List[str]) -> Dict:
        """Classifica i pattern di variazione prestazionale"""
        if len(times) < 3:
            return {'pattern_type': 'insufficient_data'}
        
        # Analizza trend temporale (ordine di esecuzione)
        indices = list(range(len(times)))
        correlation_with_order = np.corrcoef(indices, times)[0,1]
        
        # Analizza distribuzione
        skewness = self._calculate_skewness(times)
        kurtosis = self._calculate_kurtosis(times)
        
        # Classifica pattern
        if abs(correlation_with_order) > 0.7:
            pattern_type = 'trending' if correlation_with_order > 0 else 'improving'
        elif np.std(times) / np.mean(times) < 0.1:
            pattern_type = 'consistent'
        elif len([t for t in times if abs(t - np.mean(times)) > 2 * np.std(times)]) > 0:
            pattern_type = 'outlier_driven'
        else:
            pattern_type = 'random_variation'
        
        return {
            'pattern_type': pattern_type,
            'trend_correlation': correlation_with_order,
            'distribution_skewness': skewness,
            'distribution_kurtosis': kurtosis,
            'variation_coefficient': np.std(times) / np.mean(times),
            'interpretation': self._interpret_pattern(pattern_type, correlation_with_order)
        }
    
    def _interpret_pattern(self, pattern_type: str, correlation: float) -> str:
        """Interpreta il pattern identificato"""
        interpretations = {
            'trending': f"Performance degrada nel tempo (r={correlation:.3f})",
            'improving': f"Performance migliora nel tempo (r={correlation:.3f})",
            'consistent': "Performance molto stabile tra permutazioni",
            'outlier_driven': "Variazioni dominate da poche permutazioni anomale",
            'random_variation': "Variazioni apparentemente casuali",
            'insufficient_data': "Dati insufficienti per pattern analysis"
        }
        return interpretations.get(pattern_type, "Pattern non classificato")
    
    def _print_pattern_analysis(self, pattern_stats: Dict, outliers: Dict, 
                               stability: Dict, variations: Dict):
        """Stampa i risultati dell'analisi pattern"""
        
        
        # Statistiche temporali
        if pattern_stats.get('time_statistics'):
            ts = pattern_stats['time_statistics']
            print(f"Variabilità Temporale:")
            print(f"   • Coefficiente di variazione: {ts['cv']:.3f}")
            print(f"   • Range prestazioni: {ts['range_ratio']:.2f}x")
            print(f"   • Deviazione standard: {ts['std']:.3f}s")
        
        # Outlier
        if outliers.get('outliers'):
            print(f"\nOutlier Prestazionali ({outliers['total_outliers']}):")
            for outlier in outliers['outliers'][:3]:  # Mostra top 3
                print(f"   • {outlier['file']}: {outlier['time']:.3f}s "
                      f"({outlier['type']}, z={outlier['z_score']:.2f})")
            if len(outliers['outliers']) > 3:
                print(f"   ... e altri {len(outliers['outliers'])-3}")
        
        # Stabilità
        if stability:
            print(f"\nStabilità Algoritmo:")
            print(f"   • Stabilità temporale: {stability['time_stability']}")
            print(f"   • Stabilità computazionale: {stability['hypothesis_stability']}")
            print(f"   • Prevedibilità: {stability['performance_predictability']}")
        
        # Pattern di variazione
        if variations:
            print(f"\nPattern Identificato:")
            print(f"   • Tipo: {variations['pattern_type']}")
            print(f"   • Interpretazione: {variations['interpretation']}")
            
    def generate_pattern_visualizations(self) -> List[str]:
        """
        Genera visualizzazioni specifiche per i pattern prestazionali
        
        Returns:
            Lista dei file grafici generati
        """
        if not self.pattern_results:
            print("Nessun dato pattern disponibile per la visualizzazione")
            return []
        
        # Usa il gestore di esecuzione se disponibile, altrimenti directory standard
        if self.execution_manager:
            reports_dir = self.execution_manager.get_execution_dir()
        else:
            reports_dir = os.path.join("results", "analysis", "reports")
        
        os.makedirs(reports_dir, exist_ok=True)
        
        generated_files = []
        
        # Grafico 1: Performance Variation Pattern
        file1 = self._generate_variation_pattern_plot(reports_dir)
        if file1:
            generated_files.append(file1)
            if self.execution_manager:
                self.execution_manager.register_file(file1, "png", "Analisi Pattern di Variazione Prestazionale")
        
        # Grafico 2: Performance Stability Analysis
        file2 = self._generate_stability_analysis_plot(reports_dir)
        if file2:
            generated_files.append(file2)
            if self.execution_manager:
                self.execution_manager.register_file(file2, "png", "Analisi Stabilità Algoritmo MHS")
        
        # Grafico 3: Outlier Detection Visualization
        file3 = self._generate_outlier_detection_plot(reports_dir)
        if file3:
            generated_files.append(file3)
            if self.execution_manager:
                self.execution_manager.register_file(file3, "png", "Identificazione Outlier Prestazionali")
        
        
        
        return generated_files
    
    def _generate_variation_pattern_plot(self, output_dir: str) -> Optional[str]:
        """Genera grafico pattern di variazione"""
        try:
            raw_data = self.pattern_results['raw_data']
            times = raw_data['times']
            files = raw_data['files']
            
            if not times:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Subplot 1: Tempo per permutazione con banda di confidenza
            permutation_indices = range(len(times))
            mean_time = np.mean(times)
            std_time = np.std(times)
            
            ax1.plot(permutation_indices, times, 'o-', color='blue', linewidth=2, markersize=8)
            ax1.axhline(y=mean_time, color='red', linestyle='--', alpha=0.7, label=f'Media: {mean_time:.3f}s')
            ax1.fill_between(permutation_indices, 
                           mean_time - std_time, mean_time + std_time, 
                           alpha=0.2, color='red', label=f'±1σ: {std_time:.3f}s')
            
            # Evidenzia outlier
            outliers = self.pattern_results['performance_outliers']['outliers']
            for outlier in outliers:
                idx = outlier['index']
                color = 'red' if outlier['type'] == 'slow' else 'green'
                ax1.scatter(idx, times[idx], s=150, color=color, marker='*', 
                          label=f"Outlier {outlier['type']}" if outlier == outliers[0] else "")
            
            ax1.set_xlabel('Indice Permutazione')
            ax1.set_ylabel('Tempo di Esecuzione (s)')
            ax1.set_title('Pattern Variazione Prestazionale tra Permutazioni')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Subplot 2: Tempo normalizzato (% rispetto alla media)
            normalized_times = [(t / mean_time - 1) * 100 for t in times]
            colors = ['red' if nt > 0 else 'green' for nt in normalized_times]
            
            bars = ax2.bar(permutation_indices, normalized_times, color=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            ax2.axhline(y=20, color='red', linestyle='--', alpha=0.5, label='±20%')
            ax2.axhline(y=-20, color='red', linestyle='--', alpha=0.5)
            
            ax2.set_xlabel('Indice Permutazione')
            ax2.set_ylabel('Deviazione dalla Media (%)')
            ax2.set_title('Performance Relativa (% vs Media)')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Aggiungi etichette file sui bar più significativi
            for i, (bar, file, norm_time) in enumerate(zip(bars, files, normalized_times)):
                if abs(norm_time) > 15:  # Solo per deviazioni > 15%
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if norm_time > 0 else -10),
                            os.path.basename(file)[:10], ha='center', va='bottom' if norm_time > 0 else 'top',
                            fontsize=8, rotation=45)
            
            plt.tight_layout()
            
            output_file = os.path.join(output_dir, f"pattern_variation_analysis_report_1.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_file
        except KeyboardInterrupt:
            raise    
        except Exception as e:
            print(f"Errore nella generazione del grafico pattern variation: {e}")
            return None
    
    def _generate_stability_analysis_plot(self, output_dir: str) -> Optional[str]:
        """Genera grafico analisi stabilità"""
        try:
            raw_data = self.pattern_results['raw_data']
            times = raw_data['times']
            hypotheses = raw_data['hypotheses']
            
            if not times:
                return None
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Subplot 1: Box plot tempi
            ax1.boxplot(times, patch_artist=True, 
                       boxprops=dict(facecolor='lightblue', alpha=0.7))
            ax1.set_ylabel('Tempo di Esecuzione (s)')
            ax1.set_title('Distribuzione Tempi di Esecuzione')
            ax1.grid(True, alpha=0.3)
            
            # Aggiungi statistiche al box plot
            stats_text = f"Media: {np.mean(times):.3f}s\nStd: {np.std(times):.3f}s\nCV: {np.std(times)/np.mean(times):.3f}"
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Subplot 2: Istogramma tempi
            ax2.hist(times, bins=min(10, len(times)//2 + 1), alpha=0.7, color='skyblue', edgecolor='black')
            ax2.axvline(np.mean(times), color='red', linestyle='--', label=f'Media: {np.mean(times):.3f}s')
            ax2.axvline(np.median(times), color='green', linestyle='--', label=f'Mediana: {np.median(times):.3f}s')
            ax2.set_xlabel('Tempo di Esecuzione (s)')
            ax2.set_ylabel('Frequenza')
            ax2.set_title('Distribuzione Frequenza Tempi')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Subplot 3: Scatter tempo vs ipotesi
            ax3.scatter(hypotheses, times, alpha=0.6, color='orange', s=60)
            z = np.polyfit(hypotheses, times, 1)
            p = np.poly1d(z)
            ax3.plot(hypotheses, p(hypotheses), "r--", alpha=0.8)
            correlation = np.corrcoef(hypotheses, times)[0,1]
            ax3.text(0.05, 0.95, f'Correlazione: {correlation:.3f}', 
                    transform=ax3.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            ax3.set_xlabel('Ipotesi Generate')
            ax3.set_ylabel('Tempo di Esecuzione (s)')
            ax3.set_title('Relazione Complessità-Tempo')
            ax3.grid(True, alpha=0.3)
            
            # Subplot 4: Coefficienti di variazione
            stability_data = self.pattern_results['stability_analysis']
            metrics = ['Tempo', 'Ipotesi']
            cv_values = [stability_data['time_cv'], stability_data['hypothesis_cv']]
            colors = ['red' if cv > 0.3 else 'orange' if cv > 0.15 else 'green' for cv in cv_values]
            
            bars = ax4.bar(metrics, cv_values, color=colors, alpha=0.7)
            ax4.set_ylabel('Coefficiente di Variazione')
            ax4.set_title('Stabilità Metriche (CV)')
            ax4.grid(True, alpha=0.3)
            
            # Aggiungi linee di riferimento
            ax4.axhline(y=0.15, color='orange', linestyle='--', alpha=0.5, label='Soglia moderata')
            ax4.axhline(y=0.3, color='red', linestyle='--', alpha=0.5, label='Soglia instabilità')
            ax4.legend()
            
            # Etichette sui bar
            for bar, cv in zip(bars, cv_values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{cv:.3f}', ha='center', va='bottom')
            
            plt.suptitle('Analisi Stabilità Algoritmo MHS', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            output_file = os.path.join(output_dir, f"pattern_stability_analysis_report_2.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_file
        
        except KeyboardInterrupt:
            raise    
        except Exception as e:
            print(f"Errore nella generazione del grafico stabilità: {e}")
            return None
    
    def _generate_outlier_detection_plot(self, output_dir: str) -> Optional[str]:
        """Genera grafico identificazione outlier"""
        try:
            raw_data = self.pattern_results['raw_data']
            times = raw_data['times']
            files = raw_data['files']
            outliers_data = self.pattern_results['performance_outliers']
            
            if not times or len(times) < 3:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Subplot 1: Z-score analysis
            z_scores = [abs(z) for z in self._calculate_zscore(times)]
            colors = ['red' if z > 2 else 'orange' if z > 1 else 'green' for z in z_scores]
            
            bars = ax1.bar(range(len(times)), z_scores, color=colors, alpha=0.7)
            ax1.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='Soglia outlier (z=2)')
            ax1.axhline(y=1, color='orange', linestyle='--', alpha=0.7, label='Soglia attenzione (z=1)')
            
            ax1.set_xlabel('Indice Permutazione')
            ax1.set_ylabel('Z-Score (valore assoluto)')
            ax1.set_title('Analisi Z-Score per Identificazione Outlier')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Etichetta outlier significativi
            for i, (z, file) in enumerate(zip(z_scores, files)):
                if z > 2:
                    ax1.text(i, z + 0.1, os.path.basename(file)[:8], 
                            ha='center', va='bottom', fontsize=8, rotation=45)
            
            # Subplot 2: Performance map (heatmap-style)
            # Crea una matrice di performance normalizzate
            normalized_times = (np.array(times) - np.mean(times)) / np.std(times)
            memory_peaks = raw_data['memory_peaks']
            hypotheses = raw_data['hypotheses']
            
            # Normalizza anche gli altri dati se disponibili
            if any(m > 0 for m in memory_peaks):
                normalized_memory = (np.array(memory_peaks) - np.mean(memory_peaks)) / (np.std(memory_peaks) + 1e-10)
            else:
                normalized_memory = np.zeros_like(normalized_times)
                
            normalized_hypotheses = (np.array(hypotheses) - np.mean(hypotheses)) / (np.std(hypotheses) + 1e-10)
            
            # Crea heatmap
            performance_matrix = np.array([normalized_times, normalized_hypotheses, normalized_memory])
            metric_labels = ['Tempo', 'Ipotesi', 'Memoria']
            
            im = ax2.imshow(performance_matrix, cmap='RdYlGn_r', aspect='auto', interpolation='nearest')
            ax2.set_xticks(range(len(files)))
            ax2.set_xticklabels([os.path.basename(f)[:8] for f in files], rotation=45, ha='right')
            ax2.set_yticks(range(len(metric_labels)))
            ax2.set_yticklabels(metric_labels)
            ax2.set_title('Mappa Performance Normalizzate')
            
            # Aggiungi colorbar
            cbar = plt.colorbar(im, ax=ax2)
            cbar.set_label('Performance Normalizzata (σ)')
            
            # Evidenzia celle outlier
            for i, outlier in enumerate(outliers_data['outliers']):
                idx = outlier['index']
                ax2.add_patch(plt.Rectangle((idx-0.4, -0.4), 0.8, 0.8, 
                                          fill=False, edgecolor='black', linewidth=2))
            
            plt.tight_layout()
            
            output_file = os.path.join(output_dir, f"pattern_outlier_detection_report_3.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_file
        except KeyboardInterrupt:
            raise    
        except Exception as e:
            print(f"Errore nella generazione del grafico outlier: {e}")
            return None
