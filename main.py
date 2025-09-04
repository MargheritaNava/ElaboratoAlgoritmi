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
from performance.batch_analyzer import BatchPerformanceAnalyzer
from performance.simple_logger import create_task_logger, create_complete_execution_logger
from entropy_selector import select_matrices_by_entropy
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
import matplotlib.pyplot as plt
import json
import csv

def compito_1_calcolo_mhs(input_file: str, output_file: str = None, timeout: int = 300, max_size: int = 50, logger=None):
    """
    Compito 1: Calcolo dei Minimal Hitting Set con timeout impostato a 300s e limite relativo alla dimensione del file impostato a 50MB
    """
    # Crea logger per il task se non fornito
    if logger is None:
        logger = create_task_logger("compito_1")
        should_finalize = True
    else:
        should_finalize = False
    
    logger.info(f"Avvio Compito 1: Calcolo MHS")
    logger.info(f"File input: {input_file}")
    logger.info(f"Timeout: {timeout}s, Max size: {max_size}MB")
    
    print("COMPITO 1: Calcolo Minimal Hitting Set")
    print("="*50)
    
    if not os.path.exists(input_file):
        error_msg = f"File non trovato: {input_file}"
        print(error_msg)
        logger.error(error_msg)
        if should_finalize:
            logger.finalize(False)
        return False
    
    logger.info("File input validato correttamente")
    
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
                logger.info(f"Creata cartella output: {output_dir}")
            output_file = os.path.join(output_dir, f"{base_name}.mhs")
        else:
            output_file = f"{base_name}.mhs"
    
    logger.info(f"File output: {output_file}")
    logger.section("CALCOLO MHS")
    
    # Calcola MHS con timeout e limiti
    calculator = MHSCalculator(input_file, timeout_seconds=timeout, max_file_size_mb=max_size)
    mhs_list = calculator.run(output_file)
    
    # Verifica risultato e log
    success = True
    if calculator.statistics.get('interrupted_by_timeout', False):
        msg = f"Compito 1 completato con timeout. Risultati parziali in: {output_file}"
        print(msg)
        logger.warning("Calcolo interrotto per timeout")
        logger.info(f"Risultati parziali salvati: {output_file}")
    elif calculator.statistics.get('interrupted_by_size', False):
        msg = f"File troppo grande per Compito 1. Stato salvato in: {output_file}"
        print(msg)
        logger.warning("File troppo grande per elaborazione completa")
        logger.info(f"Stato salvato: {output_file}")
    else:
        msg = f"Compito 1 completato. Risultati in: {output_file}"
        print(msg)
        logger.success("Calcolo MHS completato con successo")
        logger.info(f"Risultati finali: {output_file}")
    
    # Finalizza log
    logger.info(f"MHS trovati: {len(mhs_list) if mhs_list else 0}")
    logger.info(f"Statistiche: {calculator.statistics}")
    
    if should_finalize:
        log_file = logger.finalize(success)
        print(f"Log salvato in: {log_file}")
    
    return True

def compito_2_sperimentazione(benchmark_dir: str, output_dir: str = None, timeout: int = 300, max_size: int = 50, max_files: int = 50, logger=None):
    """
    Compito 2: Sperimentazione sui benchmark con timeout e limiti
    """
    # Crea logger per il task se non fornito
    if logger is None:
        logger = create_task_logger("compito_2")
        should_finalize = True
    else:
        should_finalize = False
    
    logger.info(f"Avvio Compito 2: Sperimentazione sui benchmark")
    logger.info(f"Directory benchmark: {benchmark_dir}")
    logger.info(f"Timeout: {timeout}s, Max size: {max_size}MB, Max files: {max_files}")
    
    print("\nCOMPITO 2: Sperimentazione sui benchmark")
    print("="*50)
    
    if not os.path.exists(benchmark_dir):
        error_msg = f"Directory benchmark non trovata: {benchmark_dir}"
        print(error_msg)
        logger.error(error_msg)
        if should_finalize:
            logger.finalize(False)
        return False
    
    # Crea directory output dentro la cartella benchmark
    if not output_dir:
        output_dir = os.path.join(benchmark_dir, "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Creata cartella output: {output_dir}")
    else:
        print(f"Utilizzando cartella output: {output_dir}")
    
    # Trova tutti i file .matrix con selezione intelligente
    print(f"\nSELEZIONE INTELLIGENTE BASATA SU ENTROPIA")
    print("="*60)
    print("Analizzando le matrici per selezionare un campione rappresentativo...")
    
    try:
        # Usa il selettore di entropia per scegliere le matrici più diverse
        matrix_files = select_matrices_by_entropy(benchmark_dir, max_files)
        logger.info(f"Selezione per entropia completata: {len(matrix_files)} matrici")
        entropy_selection = True
        
    except Exception as e:
        print(f"Errore nella selezione per entropia: {e}")
        print("Fallback alla selezione standard...")
        logger.warning(f"Fallback selezione standard: {e}")
        
        # Fallback: selezione standard
        matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
        if matrix_files:
            matrix_files = sorted(matrix_files)[:max_files]
        entropy_selection = False
    
    if not matrix_files:
        print(f"Nessun file .matrix trovato in: {benchmark_dir}")
        return False
    
    print(f"\nELABORAZIONE {len(matrix_files)} MATRICI SELEZIONATE")
    if entropy_selection:
        print("Matrici selezionate per diversità di entropia")
    else:
        print("Matrici selezionate in ordine alfabetico")
    print(f"Elaborazione dei file selezionati...")
    print(f"Timeout per file: {timeout}s")
    print(f"Limite dimensione: {max_size}MB")
    
    results_summary = []
    total_start_time = time.time()
    try:
        for i, matrix_file in enumerate(matrix_files, 1):
            print(f"\n[{i}/{len(matrix_files)}] Elaborazione: {os.path.basename(matrix_file)}")

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
                'levels_explored': calculator.statistics.get('max_level_reached', 0),
                'max_level_size': max(calculator.statistics.get('hypotheses_by_level').values()) if calculator.statistics.get('max_level_reached') else 0,
                'timeout': calculator.statistics.get('interrupted_by_timeout', False),
                'size_limit': calculator.statistics.get('interrupted_by_size', False),
                'file_size_mb': os.path.getsize(matrix_file) / (1024*1024),
                'ones_count': int(np.count_nonzero(calculator.matrix)),  # Conteggio degli elementi non nulli della matrice
                'entropy_selected': entropy_selection  # Flag per indicare il metodo di selezione
            }
            results_summary.append(result)
            
    except KeyboardInterrupt:
        print("\n--- Interruzione da tastiera intercettata! ---")
        print("Salvataggio dei dati in corso...")
        time.sleep(3)
        save_compito2(output_dir, logger, should_finalize, matrix_files, results_summary, total_start_time)
        sys.exit(0)
    except Exception as e:
        print(f"Errore: {e}")
        results_summary.append({
            'file': os.path.basename(matrix_file),
            'error': str(e)
        })
            
    save_compito2(output_dir, logger, should_finalize, matrix_files, results_summary, total_start_time)
    return True

def save_compito2(output_dir, logger, should_finalize, matrix_files, results_summary, total_start_time, interrupted: bool = False):
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
    print(f"STATISTICHE TOTALI:")
    print(f"   Successi: {successes}/{len(matrix_files)}")
    print(f"   Timeout: {timeouts}")
    print(f"   File troppo grandi: {size_limits}")
    print(f"   Errori: {errors}")
    print(f"   Tempo totale: {total_time:.1f}s")
    
    # AGGIUNTA: VALUTAZIONE CRITICA DELLE PRESTAZIONI
    print(f"\nAVVIO VALUTAZIONE CRITICA DELLE PRESTAZIONI...")
    
    # Usa il nuovo analizzatore batch unificato
    batch_analyzer = BatchPerformanceAnalyzer(output_dir)
    json_file, csv_file = batch_analyzer.analyze_batch_results(results_summary)
            
    print(f"\nCompito 2 completato con valutazione critica!")
    print(f"   • Risultati MHS: {output_dir}")
            # if plots_dir:
            #     print(f"   • Analisi prestazioni: {plots_dir}")
    if json_file:
        print(f"   • Report JSON: {json_file}")
    if csv_file:
        print(f"   • Report CSV: {csv_file}")
    
    if not interrupted:
            # Finalizza log
        logger.success("Compito 2 completato con successo")

    else:
        logger.success("Compito 2 interrotto manualmente, risultati parziali salvati")
       
            
    logger.info(f"Risultati MHS: {output_dir}")
    logger.info(f"Report JSON: {json_file}")
    logger.info(f"Report CSV: {csv_file}")

    if should_finalize:
        log_file = logger.finalize(True)
        print(f"Log salvato in: {log_file}")
    
    return True

def compito_3_permutazioni(input_file: str, num_permutations: int = 5, timeout: int = 300, max_size: int = 50, logger=None):
    """
    Compito 3: Permutazioni e confronti con timeout e limiti
    """
    # Crea logger per il task se non fornito
    if logger is None:
        logger = create_task_logger("compito_3")
        should_finalize = True
    else:
        should_finalize = False
    
    logger.info(f"Avvio Compito 3: Permutazioni e confronti")
    logger.info(f"File input: {input_file}")
    logger.info(f"Permutazioni: {num_permutations}, Timeout: {timeout}s, Max size: {max_size}MB")
    
    print(f"\nCOMPITO 3: Permutazioni e confronti")
    print("="*50)

    # Traccia tempo totale del Compito 3
    compito3_start_time = time.time()
    
    if not os.path.exists(input_file):
        error_msg = f"File non trovato: {input_file}"
        print(error_msg)
        logger.error(error_msg)
        if should_finalize:
            logger.finalize(False)
        return False
    
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    perm_dir = f"permutations_{base_name}"
    analysis_dir = os.path.abspath(os.path.join("results", "analysis"))  # Cartella analysis dentro results

    try:
        # Carica la matrice originale e calcola le colonne da tenere
        print(f"Generazione di {num_permutations} permutazioni...")
        permutator = MatrixPermutator(input_file)
        if not permutator.load_matrix():
            return False
        # Calcola le colonne non vuote sull'originale
        from mhs_calculator import MHSCalculator
        calc = MHSCalculator(input_file)
        calc.load_matrix()
        calc.reduce_matrix()
        columns_to_keep = calc.statistics['reduced_to_original']
        # Passa columns_to_keep a tutte le permutazioni
        permutator.generate_permutation_files(perm_dir, num_permutations, columns_to_keep=columns_to_keep)
    except KeyboardInterrupt:
        print("\n--- Interruzione da tastiera intercettata! ---")
        print("Salvataggio dei dati in corso...")
        time.sleep(3)
    
        print(f"\nConfronto risultati delle permutazioni (timeout: {timeout}s)...")
        pattern = os.path.join(perm_dir, "*.matrix")
        matrix_files = glob.glob(pattern)
        
        if matrix_files:
            
            print(f"Avvio analisi enhanced con il comparatore integrato...")
            
            os.makedirs(analysis_dir, exist_ok=True)
            
            logger.section("ANALISI ENHANCED")
            relative_analysis_dir = os.path.relpath(analysis_dir, os.getcwd())
            logger.info(f"Directory di analisi: {relative_analysis_dir}")
            
            comparator = MHSComparator(enable_performance_monitoring=True)
            
            absolute_matrix_files = [os.path.abspath(f) for f in matrix_files]
            logger.info(f"File da analizzare: {len(absolute_matrix_files)}")
            
            comparator.run_enhanced_comparison_experiment(absolute_matrix_files, timeout)
            
        else:
            error_msg = f"Nessun file di permutazione trovato in: {perm_dir}"
            print(error_msg)
            logger.error(error_msg)
            if should_finalize:
                logger.finalize(False)
            return False
        
        print(f"Compito 3 completato.\n\n")
        
        comparator.print_analysis_files_summary()
        
        # Finalizza log
        total_time = time.time() - compito3_start_time
        logger.success("Compito 3 completato con successo")
        logger.info(f"Tempo totale esecuzione: {total_time:.2f}s")
        logger.info(f"Permutazioni elaborate: {len(matrix_files)}")
        
        if should_finalize:
            log_file = logger.finalize(True)

        return True


    # Confronta i risultati con timeout
    print(f"\nConfronto risultati delle permutazioni (timeout: {timeout}s)...")
    pattern = os.path.join(perm_dir, "*.matrix")
    matrix_files = glob.glob(pattern)
    
    if matrix_files:
        # Usa il comparatore integrato con funzionalità avanzate
        print(f"Avvio analisi enhanced con il comparatore integrato...")
        
        # Crea directory di analisi
        os.makedirs(analysis_dir, exist_ok=True)
        
        logger.section("ANALISI ENHANCED")
        # Mostra path relativo dalla directory del progetto
        relative_analysis_dir = os.path.relpath(analysis_dir, os.getcwd())
        logger.info(f"Directory di analisi: {relative_analysis_dir}")
        
        # Inizializza comparatore con monitoraggio prestazioni
        comparator = MHSComparator(enable_performance_monitoring=True)
        
        # Converti i percorsi in assoluti prima di elaborare
        absolute_matrix_files = [os.path.abspath(f) for f in matrix_files]
        logger.info(f"File da analizzare: {len(absolute_matrix_files)}")
        
        # Esegui analisi senza cambiare directory - i file saranno salvati nelle sottocartelle
        comparator.run_enhanced_comparison_experiment(absolute_matrix_files, timeout)
        
    else:
        error_msg = f"Nessun file di permutazione trovato in: {perm_dir}"
        print(error_msg)
        logger.error(error_msg)
        if should_finalize:
            logger.finalize(False)
        return False
    
    print(f"Compito 3 completato.\n\n")
    
    # Mostra riepilogo dei file di analisi generati
    comparator.print_analysis_files_summary()
    
    # Finalizza log
    total_time = time.time() - compito3_start_time
    logger.success("Compito 3 completato con successo")
    logger.info(f"Tempo totale esecuzione: {total_time:.2f}s")
    logger.info(f"Permutazioni elaborate: {len(matrix_files)}")
    
    if should_finalize:
        log_file = logger.finalize(True)
    
    return True

def run_complete_experiment(timeout: int = 300, max_size: int = 50):
    """
    Esegue l'esperimento completo su tutti e tre i compiti con timeout e limiti
    """
    # Crea logger per l'esecuzione completa
    logger = create_complete_execution_logger()
    logger.info("Avvio esecuzione completa di tutti i compiti")
    logger.info(f"Timeout: {timeout}s, Max size: {max_size}MB")
    
    print("ELABORATO 2023-2024: Calcolo Minimal Hitting Set")
    print("="*60)
    print("Autori: Mattia Pavlovic, Elena Margherita Nava e Jennifer Piangatelli")
    print("Data:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Timeout per file: {timeout}s")
    print(f"Limite dimensione: {max_size}MB")
    print("="*60)
    
    # Controlla se esistono i benchmark
    benchmark_dirs = ["benchmarks","benchmarks_test"]
    available_benchmarks = [d for d in benchmark_dirs if os.path.exists(d)]
    
    if not available_benchmarks:
        error_msg = "Nessuna directory di benchmark trovata"
        print(error_msg)
        logger.error(error_msg)
        logger.finalize(False)
        return False
    else:
        # Usa i benchmark 
        benchmark_dir = available_benchmarks[0]
        logger.info(f"Utilizzando benchmark directory: {benchmark_dir}")
        
        # Compito 2: Sperimentazione
        logger.section("COMPITO 2: SPERIMENTAZIONE")
        compito_2_sperimentazione(benchmark_dir, timeout=timeout, max_size=max_size, max_files=50, logger=logger)
        
        # Compito 1 e 3: Su un file specifico
        matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
        if matrix_files:
            test_file = matrix_files[0]  # Prendi il primo file
            logger.info(f"File di test per Compito 1 e 3: {test_file}")
            
            # Compito 1
            logger.section("COMPITO 1: CALCOLO MHS")
            compito_1_calcolo_mhs(test_file, timeout=timeout, max_size=max_size, logger=logger)
            
            # Compito 3
            logger.section("COMPITO 3: PERMUTAZIONI E CONFRONTI")
            compito_3_permutazioni(test_file, 20, timeout=timeout, max_size=max_size, logger=logger)
    
    print(f"\nESPERIMENTO COMPLETO TERMINATO")
    print("="*60)
    
    # Finalizza log dell'esecuzione completa
    logger.success("Esecuzione completa terminata con successo")
    log_file = logger.finalize(True)
    print(f"Log completo salvato in: {log_file}")

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
  python main.py --compito2 benchmarks/        # Solo sperimentazione
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
    parser.add_argument('--num-permutations', type=int, default=20,
                       help='Numero di permutazioni per Compito 3 (default: 20)')
    
    # Nuove opzioni per timeout e limiti
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout in secondi per file (default: 300)')
    parser.add_argument('--max-size', type=int, default=50,
                       help='Dimensione massima file in MB (default: 50)')
    parser.add_argument('--max-files', type=int, default=30,
                       help='Numero massimo di file da elaborare nei benchmark (default: 30)')
    
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
