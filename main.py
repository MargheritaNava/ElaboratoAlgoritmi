#!/usr/bin/env python3
"""
Script principale per l'Elaborato 2023-2024
======================================

Script principale che integra tutti e tre i compiti proposti nell'elaborato:
- Compito 1: Calcolo MHS
- Compito 2: Sperimentazione
- Compito 3: Permutazioni e confronti

Autori: Mattia Pavlovic, Elena Margherita Nava e Jennifer Piangatelli
"""

import os
import sys
import argparse
import time
import glob
from mhs_calculator import MHSCalculator
from matrix_permutator import MatrixPermutator
from mhs_comparator import MHSComparator
import numpy as np
import matplotlib.pyplot as plt
import json
import csv

def compito_1_calcolo_mhs(input_file: str, output_file: str = None, timeout: int = 300, max_size: int = 50):
    """
    Compito 1: Calcolo dei Minimal Hitting Set con timeout impostato a 300s e limite relativo alla dimensione del file impostato a 50MB
    """
    print("COMPITO 1: Calcolo Minimal Hitting Set")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"File non trovato: {input_file}")
        return False
    
    # Genera nome output se non specificato
    if not output_file:
        input_dir = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # Se il file è in una cartella benchmark, salva nella sottocartella output
        if 'benchmark' in input_dir.lower():
            output_dir = os.path.join(input_dir, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Creata cartella output: {output_dir}")
            output_file = os.path.join(output_dir, f"{base_name}.mhs")
        else:
            output_file = f"{base_name}.mhs"
    
    # Calcola MHS con timeout e limiti
    calculator = MHSCalculator(input_file, timeout_seconds=timeout, max_file_size_mb=max_size)
    mhs_list = calculator.run(output_file)
    
    # Verifica
    if calculator.statistics.get('interrupted_by_timeout', False):
        print(f"Compito 1 completato con timeout. Risultati parziali in: {output_file}")
        return True  # Comunque considerato successo per continuare
    elif calculator.statistics.get('interrupted_by_size', False):
        print(f"File troppo grande per Compito 1. Stato salvato in: {output_file}")
        return True
    else:
        print(f"Compito 1 completato. Risultati in: {output_file}")
        return True

def compito_2_sperimentazione(benchmark_dir: str, output_dir: str = None, timeout: int = 300, max_size: int = 50, max_files: int = 10):
    """
    Compito 2: Sperimentazione sui benchmark con timeout e limiti
    """
    print("\nCOMPITO 2: Sperimentazione sui benchmark")
    print("="*50)
    
    if not os.path.exists(benchmark_dir):
        print(f"Directory benchmark non trovata: {benchmark_dir}")
        return False
    
    # Crea directory output dentro la cartella benchmark
    if not output_dir:
        output_dir = os.path.join(benchmark_dir, "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Creata cartella output: {output_dir}")
    else:
        print(f"Utilizzando cartella output: {output_dir}")
    
    # Trova tutti i file .matrix
    matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
    
    if not matrix_files:
        print(f"Nessun file .matrix trovato in: {benchmark_dir}")
        return False
    
    print(f"Trovati {len(matrix_files)} file di benchmark")
    
    # Limita il numero di file per evitare tempi eccessivi
    matrix_files = sorted(matrix_files)[:max_files]
    print(f"Elaborazione dei primi {len(matrix_files)} file...")
    print(f"Timeout per file: {timeout}s")
    print(f"Limite dimensione: {max_size}MB")
    
    results_summary = []
    total_start_time = time.time()
    
    for i, matrix_file in enumerate(matrix_files, 1):
        print(f"\n[{i}/{len(matrix_files)}] Elaborazione: {os.path.basename(matrix_file)}")
        
        try:
            # Calcola MHS con timeout
            base_name = os.path.splitext(os.path.basename(matrix_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.mhs")
            
            start_time = time.time()
            calculator = MHSCalculator(matrix_file, timeout_seconds=timeout, max_file_size_mb=max_size)
            mhs_list = calculator.run(output_file)
            end_time = time.time()
            
            # Raccogli risultati ESTESI per analisi critica
            result = {
                'file': os.path.basename(matrix_file),
                'matrix_size': f"{calculator.n_rows}×{calculator.n_cols}",
                'reduced_size': f"{calculator.n_rows}×{calculator.n_cols_reduced}",
                'mhs_count': len(mhs_list) if mhs_list else 0,
                'computation_time': end_time - start_time,
                'hypotheses_generated': calculator.statistics.get('hypotheses_generated', 0),
                'levels_explored': len(calculator.statistics.get('levels_generated', [])),
                'max_level_size': max(calculator.statistics.get('levels_generated', [0])) if calculator.statistics.get('levels_generated') else 0,
                'timeout': calculator.statistics.get('interrupted_by_timeout', False),
                'size_limit': calculator.statistics.get('interrupted_by_size', False),
                'file_size_mb': os.path.getsize(matrix_file) / (1024*1024)
            }
            results_summary.append(result)
            
        except Exception as e:
            print(f"Errore: {e}")
            results_summary.append({
                'file': os.path.basename(matrix_file),
                'error': str(e)
            })
    
    total_time = time.time() - total_start_time
    
    # Stampa riassunto
    print(f"\nRIASSUNTO SPERIMENTAZIONE")
    print("="*80)
    print(f"{'File':<20} {'Matrice':<10} {'Ridotta':<10} {'MHS':<6} {'Tempo(s)':<8} {'Ipotesi':<8} {'Status':<10}")
    print("-" * 80)
    
    timeouts = 0
    size_limits = 0
    errors = 0
    successes = 0
    
    for result in results_summary:
        if 'error' not in result:
            status = "OK"
            if result.get('timeout', False):
                status = "TIMEOUT"
                timeouts += 1
            elif result.get('size_limit', False):
                status = "TOO_BIG"
                size_limits += 1
            else:
                successes += 1
                
            print(f"{result['file']:<20} "
                  f"{result['matrix_size']:<10} "
                  f"{result['reduced_size']:<10} "
                  f"{result['mhs_count']:<6} "
                  f"{result['computation_time']:<8.3f} "
                  f"{result['hypotheses_generated']:<8} "
                  f"{status:<10}")
        else:
            print(f"{result['file']:<20} ERROR: {result['error']}")
            errors += 1
    
    print("-" * 80)
    print(f"📈 STATISTICHE TOTALI:")
    print(f"   Successi: {successes}/{len(matrix_files)}")
    print(f"   Timeout: {timeouts}")
    print(f"   File troppo grandi: {size_limits}")
    print(f"   Errori: {errors}")
    print(f"   Tempo totale: {total_time:.1f}s")
    
    # 🆕 AGGIUNTA: VALUTAZIONE CRITICA DELLE PRESTAZIONI
    print(f"\n🎯 AVVIO VALUTAZIONE CRITICA DELLE PRESTAZIONI...")
    analyze_performance_critically(results_summary, output_dir)
    
    # 🆕 AGGIUNTA: ANALISI COMPLESSITÀ TEORICA (ASINTOTICA)
    print(f"\n🔬 AVVIO ANALISI COMPLESSITÀ TEORICA (BIG O)...")
    analyze_theoretical_complexity(results_summary, output_dir)
    
    # 🆕 AGGIUNTA: SALVATAGGIO REPORT DETTAGLIATI
    save_performance_report(results_summary, output_dir)
    
    print(f"\n✅ Compito 2 completato con valutazione critica!")
    print(f"   • Risultati MHS: {output_dir}")
    print(f"   • Analisi prestazioni: {output_dir}/performance_analysis.png")
    print(f"   • Complessità asintotica: {output_dir}/algorithmic_complexity.png")
    print(f"   • Report dettagliati: {output_dir}/performance_*.csv/json")
    
    return True

def compito_3_permutazioni(input_file: str, num_permutations: int = 5, timeout: int = 300, max_size: int = 50):
    """
    Compito 3: Permutazioni e confronti con timeout e limiti
    """
    print(f"\nCOMPITO 3: Permutazioni e confronti")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"File non trovato: {input_file}")
        return False
    
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    perm_dir = f"permutations_{base_name}"
    
    # Genera permutazioni
    print(f"Generazione di {num_permutations} permutazioni...")
    permutator = MatrixPermutator(input_file)
    
    if not permutator.load_matrix():
        return False
    
    permutator.generate_permutation_files(perm_dir, num_permutations)
    
    # Confronta i risultati con timeout
    print(f"\nConfronto risultati delle permutazioni (timeout: {timeout}s)...")
    pattern = os.path.join(perm_dir, "*.matrix")
    matrix_files = glob.glob(pattern)
    
    if matrix_files:
        # Calcola MHS per ogni permutazione con timeout
        print(f"Calcolando MHS per {len(matrix_files)} permutazioni...")
        
        results = []
        for i, matrix_file in enumerate(matrix_files, 1):
            print(f"[{i}/{len(matrix_files)}] {os.path.basename(matrix_file)}")
            
            try:
                # Crea nome output nella cartella permutazioni
                base_perm_name = os.path.splitext(os.path.basename(matrix_file))[0]
                output_file = os.path.join(perm_dir, f"{base_perm_name}.mhs")
                
                calculator = MHSCalculator(matrix_file, timeout_seconds=timeout, max_file_size_mb=max_size)
                mhs_list = calculator.run(output_file)
                
                results.append({
                    'file': os.path.basename(matrix_file),
                    'mhs_count': len(mhs_list) if mhs_list else 0,
                    'time': calculator.statistics.get('total_time', 0),
                    'timeout': calculator.statistics.get('interrupted_by_timeout', False),
                    'size_limit': calculator.statistics.get('interrupted_by_size', False)
                })
            except Exception as e:
                print(f"Errore su {matrix_file}: {e}")
                results.append({
                    'file': os.path.basename(matrix_file),
                    'error': str(e)
                })
        
        # Stampa riassunto confronti
        print(f"\nRIASSUNTO CONFRONTO PERMUTAZIONI")
        print("-" * 60)
        print(f"{'File':<25} {'MHS':<6} {'Tempo(s)':<8} {'Status':<10}")
        print("-" * 60)
        
        for result in results:
            if 'error' not in result:
                status = "OK"
                if result.get('timeout', False):
                    status = "TIMEOUT"
                elif result.get('size_limit', False):
                    status = "TOO_BIG"
                
                print(f"{result['file']:<25} "
                      f"{result['mhs_count']:<6} "
                      f"{result['time']:<8.3f} "
                      f"{status:<10}")
            else:
                print(f"{result['file']:<25} ERROR: {result['error']}")
        
        # Usa il comparatore se è disponibile
        try:
            comparator = MHSComparator()
            comparator.run_comparison_experiment(matrix_files)
        except Exception as e:
            print(f"Errore nel comparatore: {e}")
    else:
        print(f"Nessun file di permutazione trovato in: {perm_dir}")
        return False
    
    print(f"Compito 3 completato. File in: {perm_dir}")
    return True

def run_complete_experiment(timeout: int = 300, max_size: int = 50):
    """
    Esegue l'esperimento completo su tutti e tre i compiti con timeout e limiti
    """
    print("ELABORATO 2023-2024: Calcolo Minimal Hitting Set")
    print("="*60)
    print("Autori: Mattia Pavlovic, Elena Margherita Nava e Jennifer Piangatelli")
    print("Data:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Timeout per file: {timeout}s")
    print(f"Limite dimensione: {max_size}MB")
    print("="*60)
    
    # Controlla se esistono i benchmark
    benchmark_dirs = ["benchmarks1", "benchmarks2"]
    available_benchmarks = [d for d in benchmark_dirs if os.path.exists(d)]
    
    if not available_benchmarks:
        print("Nessuna directory di benchmark trovata")
        return False
    else:
        # Usa i benchmark 
        benchmark_dir = available_benchmarks[0]
        
        # Compito 2: Sperimentazione
        compito_2_sperimentazione(benchmark_dir, timeout=timeout, max_size=max_size, max_files=10)
        
        # Compito 1 e 3: Su un file specifico
        matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
        if matrix_files:
            test_file = matrix_files[0]  # Prendi il primo file
            
            # Compito 1
            compito_1_calcolo_mhs(test_file, timeout=timeout, max_size=max_size)
            
            # Compito 3
            compito_3_permutazioni(test_file, 3, timeout=timeout, max_size=max_size)
    
    print(f"\nESPERIMENTO COMPLETO TERMINATO")
    print("="*60)

def analyze_performance_critically(results_summary: list, output_dir: str):
    """
    Valutazione critica delle prestazioni spaziali e temporali
    """
    print(f"\nVALUTAZIONE CRITICA DELLE PRESTAZIONI")
    print("="*80)
    
    # Filtra risultati validi
    valid_results = [r for r in results_summary if 'error' not in r]
    
    if not valid_results:
        print("Nessun risultato valido per l'analisi")
        return False
    
    # Estrai dati per analisi
    times = [r['computation_time'] for r in valid_results]
    mhs_counts = [r['mhs_count'] for r in valid_results]
    hypotheses = [r['hypotheses_generated'] for r in valid_results]
    matrix_sizes = []
    
    for r in valid_results:
        size_str = r['matrix_size']
        if '×' in size_str:
            rows, cols = map(int, size_str.split('×'))
            matrix_sizes.append(rows * cols)
        else:
            matrix_sizes.append(0)
    
    # 1. ANALISI TEMPORALE
    print(f"\nANALISI PRESTAZIONI TEMPORALI")
    print("-" * 60)
    print(f"Tempo medio di calcolo: {np.mean(times):.3f}s")
    print(f"Tempo mediano: {np.median(times):.3f}s")
    print(f"Deviazione standard: {np.std(times):.3f}s")
    print(f"Tempo minimo: {min(times):.3f}s")
    print(f"Tempo massimo: {max(times):.3f}s")
    print(f"Range temporale: {max(times) - min(times):.3f}s")
    
    # Classificazione prestazioni temporali
    fast_files = [r for r in valid_results if r['computation_time'] < np.mean(times) - np.std(times)]
    slow_files = [r for r in valid_results if r['computation_time'] > np.mean(times) + np.std(times)]
    
    print(f"\nFile elaborati VELOCEMENTE ({len(fast_files)}):")
    for f in fast_files[:5]:  # Top 5
        print(f"   • {f['file']}: {f['computation_time']:.3f}s ({f['mhs_count']} MHS)")
    
    print(f"\nFile elaborati LENTAMENTE ({len(slow_files)}):")
    for f in slow_files[:5]:  # Top 5
        print(f"   • {f['file']}: {f['computation_time']:.3f}s ({f['mhs_count']} MHS)")
    
    # 2. ANALISI SPAZIALE (approssimata tramite ipotesi generate)
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
    
    # 3. CORRELAZIONI E RELAZIONI
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
    
    # 4. CLASSIFICAZIONE COMPLESSITÀ
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
    
    for r in valid_results:
        time = r['computation_time']
        hyp = r['hypotheses_generated']
        
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
    
    # 5. GENERAZIONE GRAFICI
    print(f"\nGENERAZIONE GRAFICI ANALITICI")
    print("-" * 60)
    
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
        plot_path = os.path.join(output_dir, 'performance_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Grafici salvati in: {plot_path}")
        plt.close()
        
    except Exception as e:
        print(f"Errore nella generazione grafici: {e}")
    
    # 6. ANALISI COMPLESSITÀ ASINTOTICA
    print(f"\n🔬 AVVIO ANALISI COMPLESSITÀ ALGORITMICA...")
    analyze_algorithmic_complexity(results_summary, output_dir)
    
    # 7. REPORT FINALE CRITICO
    print(f"\n📝 VALUTAZIONE CRITICA FINALE")
    print("="*80)
    
    # Efficienza complessiva
    total_files = len(valid_results)
    total_time = sum(times)
    avg_efficiency = total_files / total_time if total_time > 0 else 0
    
    print(f"🎯 PRESTAZIONI COMPLESSIVE:")
    print(f"   • File elaborati: {total_files}")
    print(f"   • Tempo totale: {total_time:.1f}s")
    print(f"   • Efficienza: {avg_efficiency:.2f} file/secondo")
    
    # Identifica colli di bottiglia
    bottlenecks = [r for r in valid_results if r['computation_time'] > np.mean(times) + 2*np.std(times)]
    if bottlenecks:
        print(f"\n⚠️ COLLI DI BOTTIGLIA IDENTIFICATI ({len(bottlenecks)} file):")
        for b in bottlenecks:
            print(f"   • {b['file']}: {b['computation_time']:.3f}s - {b['hypotheses_generated']} ipotesi")
    
    # Raccomandazioni
    print(f"\n💡 RACCOMANDAZIONI PRESTAZIONI:")
    if np.std(times) > np.mean(times):
        print("   • Alta variabilità nei tempi → Implementare timeout adattivi")
    if max(hypotheses) > 10 * np.mean(hypotheses):
        print("   • Picchi di complessità → Migliorare tecniche di potatura")
    if len(matrix_sizes) > 0 and np.corrcoef(matrix_sizes, times)[0,1] > 0.8:
        print("   • Forte dipendenza dalla dimensione → Ottimizzare per matrici grandi")
    
    return True

def save_performance_report(results_summary: list, output_dir: str):
    """
    Salva un report dettagliato delle prestazioni in formato CSV e JSON
    """
    # Prepara i dati
    valid_results = [r for r in results_summary if 'error' not in r]
    
    # Salva CSV dettagliato
    csv_path = os.path.join(output_dir, 'performance_detailed.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        if valid_results:
            fieldnames = valid_results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(valid_results)
    
    # Salva statistiche aggregate in JSON
    if valid_results:
        times = [r['computation_time'] for r in valid_results]
        hypotheses = [r['hypotheses_generated'] for r in valid_results]
        
        stats = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_files_processed': len(valid_results),
            'temporal_performance': {
                'mean_time': float(np.mean(times)),
                'median_time': float(np.median(times)),
                'std_time': float(np.std(times)),
                'min_time': float(min(times)),
                'max_time': float(max(times))
            },
            'spatial_performance': {
                'mean_hypotheses': float(np.mean(hypotheses)),
                'median_hypotheses': float(np.median(hypotheses)),
                'std_hypotheses': float(np.std(hypotheses)),
                'min_hypotheses': int(min(hypotheses)),
                'max_hypotheses': int(max(hypotheses))
            },
            'efficiency_metrics': {
                'files_per_second': len(valid_results) / sum(times) if sum(times) > 0 else 0,
                'average_mhs_per_file': np.mean([r['mhs_count'] for r in valid_results])
            }
        }
        
        json_path = os.path.join(output_dir, 'performance_statistics.json')
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(stats, jsonfile, indent=2)
    
    print(f"Report salvati:")
    print(f"   • CSV dettagliato: {csv_path}")
    print(f"   • Statistiche JSON: {json_path}")

def analyze_algorithmic_complexity(results_summary: list, output_dir: str):
    """
    Analizza la complessità asintotica temporale e spaziale (Big O notation)
    """
    print(f"\n🔬 ANALISI COMPLESSITÀ ALGORITMICA ASINTOTICA")
    print("="*80)
    
    # Filtra risultati validi
    valid_results = [r for r in results_summary if 'error' not in r]
    
    if not valid_results:
        print("❌ Nessun risultato valido per l'analisi")
        return False
    
    # Estrai dati per analisi
    matrix_sizes = []
    times = []
    hypotheses = []
    
    for r in valid_results:
        size_str = r['matrix_size']
        if '×' in size_str:
            rows, cols = map(int, size_str.split('×'))
            n = rows * cols  # Dimensione totale della matrice
            matrix_sizes.append(n)
            times.append(r['computation_time'])
            hypotheses.append(r['hypotheses_generated'])
    
    if len(matrix_sizes) < 3:
        print("❌ Dati insufficienti per analisi complessità (minimo 3 campioni)")
        return False
    
    # 1. ANALISI COMPLESSITÀ TEMPORALE
    print(f"\n⏱️  COMPLESSITÀ TEMPORALE ASINTOTICA")
    print("-" * 60)
    
    # Ordina i dati per dimensione
    sorted_data = sorted(zip(matrix_sizes, times, hypotheses))
    sizes_sorted = [x[0] for x in sorted_data]
    times_sorted = [x[1] for x in sorted_data]
    hyp_sorted = [x[2] for x in sorted_data]
    
    # Calcola rapporti di crescita
    time_growth_ratios = []
    size_growth_ratios = []
    
    for i in range(1, len(sizes_sorted)):
        if sizes_sorted[i-1] > 0 and times_sorted[i-1] > 0:
            size_ratio = sizes_sorted[i] / sizes_sorted[i-1]
            time_ratio = times_sorted[i] / times_sorted[i-1]
            
            if size_ratio > 1.1:  # Solo se c'è crescita significativa
                time_growth_ratios.append(time_ratio)
                size_growth_ratios.append(size_ratio)
    
    # Stima la complessità temporale
    if time_growth_ratios:
        avg_time_growth = sum(time_growth_ratios) / len(time_growth_ratios)
        avg_size_growth = sum(size_growth_ratios) / len(size_growth_ratios)
        
        # Calcola l'esponente approssimativo
        if avg_size_growth > 1:
            import math
            growth_exponent = math.log(avg_time_growth) / math.log(avg_size_growth)
            
            print(f"Rapporto crescita tempo medio: {avg_time_growth:.3f}")
            print(f"Rapporto crescita dimensione medio: {avg_size_growth:.3f}")
            print(f"Esponente stimato: {growth_exponent:.2f}")
            
            # Classifica la complessità
            if growth_exponent < 0.5:
                complexity_class = "O(log n) - Logaritmica"
                emoji = "🟢"
                description = "Ottima scalabilità"
            elif growth_exponent < 1.2:
                complexity_class = "O(n) - Lineare"
                emoji = "🟡"
                description = "Buona scalabilità"
            elif growth_exponent < 1.8:
                complexity_class = "O(n log n) - Linearitmica"
                emoji = "🟠"
                description = "Scalabilità accettabile"
            elif growth_exponent < 2.5:
                complexity_class = "O(n²) - Quadratica"
                emoji = "🔴"
                description = "Scalabilità limitata"
            elif growth_exponent < 3.5:
                complexity_class = "O(n³) - Cubica"
                emoji = "🔴"
                description = "Scalabilità problematica"
            else:
                complexity_class = "O(2^n) - Esponenziale"
                emoji = "💀"
                description = "Scalabilità critica"
            
            print(f"📊 Complessità temporale stimata: {emoji} {complexity_class}")
            print(f"📝 Valutazione: {description}")
        else:
            print("❌ Impossibile stimare complessità (dati insufficienti)")
    
    # 2. ANALISI COMPLESSITÀ SPAZIALE
    print(f"\n💾 COMPLESSITÀ SPAZIALE ASINTOTICA")
    print("-" * 60)
    
    # Analizza la crescita dello spazio (tramite ipotesi generate)
    hyp_growth_ratios = []
    
    for i in range(1, len(sizes_sorted)):
        if sizes_sorted[i-1] > 0 and hyp_sorted[i-1] > 0:
            size_ratio = sizes_sorted[i] / sizes_sorted[i-1]
            hyp_ratio = hyp_sorted[i] / hyp_sorted[i-1]
            
            if size_ratio > 1.1:  # Solo se c'è crescita significativa
                hyp_growth_ratios.append(hyp_ratio)
    
    if hyp_growth_ratios:
        avg_hyp_growth = sum(hyp_growth_ratios) / len(hyp_growth_ratios)
        
        # Calcola l'esponente per lo spazio
        if avg_size_growth > 1:
            import math
            space_exponent = math.log(avg_hyp_growth) / math.log(avg_size_growth)
            
            print(f"Rapporto crescita spazio medio: {avg_hyp_growth:.3f}")
            print(f"Esponente spaziale stimato: {space_exponent:.2f}")
            
            # Classifica la complessità spaziale
            if space_exponent < 0.5:
                space_complexity_class = "O(log n) - Logaritmica"
                space_emoji = "🟢"
                space_description = "Uso memoria ottimo"
            elif space_exponent < 1.2:
                space_complexity_class = "O(n) - Lineare"
                space_emoji = "🟡"
                space_description = "Uso memoria buono"
            elif space_exponent < 1.8:
                space_complexity_class = "O(n log n) - Linearitmica"
                space_emoji = "🟠"
                space_description = "Uso memoria accettabile"
            elif space_exponent < 2.5:
                space_complexity_class = "O(n²) - Quadratica"
                space_emoji = "🔴"
                space_description = "Uso memoria elevato"
            elif space_exponent < 3.5:
                space_complexity_class = "O(n³) - Cubica"
                space_emoji = "🔴"
                space_description = "Uso memoria critico"
            else:
                space_complexity_class = "O(2^n) - Esponenziale"
                space_emoji = "💀"
                space_description = "Uso memoria proibitivo"
            
            print(f"📊 Complessità spaziale stimata: {space_emoji} {space_complexity_class}")
            print(f"📝 Valutazione: {space_description}")
    
    # 3. CONFRONTO CON COMPLESSITÀ TEORICA MHS
    print(f"\n📚 CONFRONTO CON TEORIA ALGORITMI MHS")
    print("-" * 60)
    print("💡 COMPLESSITÀ TEORICA ALGORITMI MHS:")
    print("   • Caso peggiore generale: O(3^(n/3)) - Esponenziale rispetto al numero di elementi")
    print("   • Spazio tipico: O(k × n) dove k = numero di MHS trovati")
    print("   • Dipendenza critica da:")
    print("     - Struttura della matrice (densità, pattern)")
    print("     - Efficacia delle tecniche di potatura")
    print("     - Euristica di esplorazione utilizzata")
    print("     - Numero di elementi per riga (branching factor)")
    
    # Confronto con implementazione corrente
    if 'growth_exponent' in locals():
        print(f"\n🔍 CONFRONTO IMPLEMENTAZIONE CORRENTE:")
        if growth_exponent < 2.0:
            print("   ✅ Prestazioni MIGLIORI del caso peggiore teorico")
            print("   🎯 Potature e ottimizzazioni efficaci")
        elif growth_exponent < 3.0:
            print("   ⚠️ Prestazioni VICINE al caso peggiore teorico")
            print("   🔧 Possibili miglioramenti nelle potature")
        else:
            print("   🚨 Prestazioni PEGGIORI del caso peggiore teorico")
            print("   🛠️ Necessari miglioramenti algoritmici urgenti")
    
    # 4. TABELLA CRESCITA DETTAGLIATA
    print(f"\n📋 TABELLA CRESCITA ASINTOTICA DETTAGLIATA")
    print("-" * 90)
    print(f"{'Dimensione':<12} {'Tempo(s)':<10} {'Ipotesi':<10} {'Ratio T':<10} {'Ratio S':<10} {'O(T)':<15} {'O(S)':<15}")
    print("-" * 90)
    
    for i, (size, time, hyp) in enumerate(zip(sizes_sorted, times_sorted, hyp_sorted)):
        if i == 0:
            print(f"{size:<12} {time:<10.4f} {hyp:<10} {'--':<10} {'--':<10} {'baseline':<15} {'baseline':<15}")
        else:
            t_ratio = time / times_sorted[i-1] if times_sorted[i-1] > 0 else 0
            s_ratio = hyp / hyp_sorted[i-1] if hyp_sorted[i-1] > 0 else 0
            
            # Stima locale della complessità
            if sizes_sorted[i-1] > 0:
                size_ratio_local = sizes_sorted[i] / sizes_sorted[i-1]
                if size_ratio_local > 1:
                    t_exp_local = math.log(t_ratio) / math.log(size_ratio_local) if t_ratio > 0 else 0
                    s_exp_local = math.log(s_ratio) / math.log(size_ratio_local) if s_ratio > 0 else 0
                    
                    # Classifica locale
                    t_class = "log" if t_exp_local < 0.5 else "lin" if t_exp_local < 1.2 else "quad" if t_exp_local < 2.5 else "exp"
                    s_class = "log" if s_exp_local < 0.5 else "lin" if s_exp_local < 1.2 else "quad" if s_exp_local < 2.5 else "exp"
                else:
                    t_class = s_class = "n/a"
            else:
                t_class = s_class = "n/a"
            
            print(f"{size:<12} {time:<10.4f} {hyp:<10} {t_ratio:<10.2f} {s_ratio:<10.2f} {t_class:<15} {s_class:<15}")
    
    # 5. VISUALIZZAZIONE COMPLESSITÀ ASINTOTICA
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Grafico complessità temporale (log-log per vedere chiaramente la crescita)
        ax1.loglog(sizes_sorted, times_sorted, 'bo-', linewidth=2, markersize=8, label='Dati empirici')
        
        # Aggiungi curve di riferimento teoriche
        x_ref = np.linspace(min(sizes_sorted), max(sizes_sorted), 100)
        
        # Scala le curve di riferimento al primo punto
        base_time = times_sorted[0]
        base_size = sizes_sorted[0]
        
        # Curve teoriche scalate
        linear = base_time * (x_ref / base_size)
        quadratic = base_time * (x_ref / base_size)**2
        cubic = base_time * (x_ref / base_size)**3
        exponential = base_time * (2**(x_ref / base_size - 1))
        
        ax1.loglog(x_ref, linear, 'g--', alpha=0.8, linewidth=2, label='O(n) - Lineare')
        ax1.loglog(x_ref, quadratic, 'orange', linestyle='--', alpha=0.8, linewidth=2, label='O(n²) - Quadratica')
        ax1.loglog(x_ref, cubic, 'red', linestyle='--', alpha=0.8, linewidth=2, label='O(n³) - Cubica')
        
        # Evita overflow per curve esponenziali
        try:
            ax1.loglog(x_ref[:50], exponential[:50], 'm--', alpha=0.8, linewidth=2, label='O(2^n) - Esponenziale')
        except:
            pass
        
        ax1.set_xlabel('Dimensione matrice (n)', fontsize=12)
        ax1.set_ylabel('Tempo di calcolo (s)', fontsize=12)
        ax1.set_title('Analisi Complessità Temporale Asintotica', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Grafico complessità spaziale
        ax2.loglog(sizes_sorted, hyp_sorted, 'ro-', linewidth=2, markersize=8, label='Ipotesi generate (empiriche)')
        
        # Curve spaziali di riferimento
        space_linear = hyp_sorted[0] * (x_ref / base_size)
        space_quadratic = hyp_sorted[0] * (x_ref / base_size)**2
        space_cubic = hyp_sorted[0] * (x_ref / base_size)**3
        
        ax2.loglog(x_ref, space_linear, 'g--', alpha=0.8, linewidth=2, label='O(n) - Lineare')
        ax2.loglog(x_ref, space_quadratic, 'orange', linestyle='--', alpha=0.8, linewidth=2, label='O(n²) - Quadratica')
        ax2.loglog(x_ref, space_cubic, 'red', linestyle='--', alpha=0.8, linewidth=2, label='O(n³) - Cubica')
        
        ax2.set_xlabel('Dimensione matrice (n)', fontsize=12)
        ax2.set_ylabel('Spazio utilizzato (ipotesi)', fontsize=12)
        ax2.set_title('Analisi Complessità Spaziale Asintotica', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salva il grafico
        complexity_plot_path = os.path.join(output_dir, 'algorithmic_complexity.png')
        plt.savefig(complexity_plot_path, dpi=300, bbox_inches='tight')
        print(f"\n📊 Grafico complessità asintotica salvato: {complexity_plot_path}")
        plt.close()
        
    except Exception as e:
        print(f"⚠️ Errore nella generazione grafico complessità: {e}")
    
    # 6. RACCOMANDAZIONI ALGORITMICHE BASATE SU COMPLESSITÀ
    print(f"\n💡 RACCOMANDAZIONI ALGORITMICHE")
    print("-" * 60)
    
    if 'growth_exponent' in locals():
        if growth_exponent > 3.0:
            print("🚨 COMPLESSITÀ CRITICA RILEVATA:")
            print("   • Implementare tecniche di potatura più aggressive")
            print("   • Considerare algoritmi approssimativi per matrici grandi")
            print("   • Limitare i livelli di esplorazione massimi")
            print("   • Valutare parallelizzazione del calcolo")
        elif growth_exponent > 2.0:
            print("⚠️ COMPLESSITÀ ELEVATA:")
            print("   • Ottimizzare le strutture dati utilizzate")
            print("   • Implementare caching per ipotesi ricorrenti")
            print("   • Migliorare l'ordinamento delle colonne")
            print("   • Considerare euristica di dominanza")
        elif growth_exponent > 1.5:
            print("🔶 COMPLESSITÀ MODERATA:")
            print("   • Monitorare la crescita su dataset più grandi")
            print("   • Implementare timeout adattivi")
            print("   • Considerare pre-processing della matrice")
        else:
            print("✅ COMPLESSITÀ ACCETTABILE:")
            print("   • Algoritmo scala bene con le dimensioni")
            print("   • Prestazioni lineari o quasi-lineari")
            print("   • Potature efficaci")
    
    # 7. SUMMARY FINALE COMPLESSITÀ
    print(f"\n📊 SUMMARY COMPLESSITÀ ASINTOTICA")
    print("="*60)
    if 'growth_exponent' in locals() and 'space_exponent' in locals():
        print(f"⏱️  Complessità Temporale: {complexity_class}")
        print(f"💾 Complessità Spaziale: {space_complexity_class}")
        print(f"🎯 Esponenti: T={growth_exponent:.2f}, S={space_exponent:.2f}")
        
        # Valutazione finale
        if growth_exponent < 2.0 and space_exponent < 2.0:
            print("🏆 VALUTAZIONE FINALE: Algoritmo con complessità gestibile")
        elif growth_exponent < 3.0 and space_exponent < 3.0:
            print("⚠️ VALUTAZIONE FINALE: Algoritmo con complessità accettabile ma da monitorare")
        else:
            print("🚨 VALUTAZIONE FINALE: Algoritmo con complessità problematica")
    
    return True

def analyze_theoretical_complexity(results_summary: list, output_dir: str):
    """
    Wrapper per l'analisi della complessità teorica asintotica
    """
    return analyze_algorithmic_complexity(results_summary, output_dir)

def main():
    """
    Funzione principale con argomenti da riga di comando
    """
    parser = argparse.ArgumentParser(
        description='Elaborato 2023-2024: Calcolo Minimal Hitting Set',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi d'uso:
  python main.py --all                           # Esegue tutto l'esperimento
  python main.py --compito1 file.matrix         # Solo calcolo MHS
  python main.py --compito2 benchmarks1/        # Solo sperimentazione
  python main.py --compito3 file.matrix         # Solo permutazioni
  python main.py --all --timeout 600 --max-size 100  # Con timeout e limiti personalizzati
        """
    )
    
    # Opzioni per i singoli compiti
    parser.add_argument('--compito1', metavar='FILE', 
                       help='Esegue Compito 1: calcolo MHS per il file specificato')
    parser.add_argument('--compito2', metavar='DIR', 
                       help='Esegue Compito 2: sperimentazione sui benchmark')
    parser.add_argument('--compito3', metavar='FILE', 
                       help='Esegue Compito 3: permutazioni e confronti')
    
    # Opzioni generali
    parser.add_argument('--all', action='store_true',
                       help='Esegue l\'esperimento completo (tutti i compiti)')
    parser.add_argument('--output', '-o', metavar='DIR', default='results',
                       help='Directory di output (default: results)')
    parser.add_argument('--num-permutations', type=int, default=5,
                       help='Numero di permutazioni per Compito 3 (default: 10)')
    
    # Nuove opzioni per timeout e limiti
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout in secondi per file (default: 300)')
    parser.add_argument('--max-size', type=int, default=50,
                       help='Dimensione massima file in MB (default: 50)')
    parser.add_argument('--max-files', type=int, default=10,
                       help='Numero massimo di file da elaborare nei benchmark (default: 10)')
    
    args = parser.parse_args()
    
    # Se nessun argomento, mostra help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    print(f"MHS Calculator - Configurazione:")
    print(f"Timeout: {args.timeout}s")
    print(f"Limite dimensione: {args.max_size}MB")
    print(f"Max file batch: {args.max_files}")
    print("-" * 50)
    
    # Esegui i compiti richiesti
    if args.all:
        run_complete_experiment(timeout=args.timeout, max_size=args.max_size)
    else:
        # Compiti individuali
        if args.compito1:
            compito_1_calcolo_mhs(args.compito1, timeout=args.timeout, max_size=args.max_size)
        
        if args.compito2:
            compito_2_sperimentazione(args.compito2, args.output, 
                                    timeout=args.timeout, max_size=args.max_size, 
                                    max_files=args.max_files)
        
        if args.compito3:
            compito_3_permutazioni(args.compito3, args.num_permutations, 
                                 timeout=args.timeout, max_size=args.max_size)

if __name__ == "__main__":
    main()
