#!/usr/bin/env python3
"""
Integrazione del selettore di entropia nel Compito 2
"""

# Import necessari
import os
import sys
import time
import glob
import numpy as np
from entropy_selector import select_matrices_by_entropy
from mhs_calculator import MHSCalculator

# Import delle funzioni di logging e salvataggio dal main
from main import create_task_logger, save_compito2

# Modifica la funzione compito_2_sperimentazione per integrare la selezione per entropia

def compito_2_sperimentazione_enhanced(benchmark_dir: str, output_dir: str = None, timeout: int = 300, max_size: int = 50, max_files: int = 30, use_entropy_selection: bool = True, logger=None):
    """
    Compito 2: Sperimentazione sui benchmark con selezione intelligente basata su entropia
    """
    # Crea logger per il task se non fornito
    if logger is None:
        logger = create_task_logger("compito_2")
        should_finalize = True
    else:
        should_finalize = False
    
    logger.info(f"Avvio Compito 2: Sperimentazione sui benchmark")
    logger.info(f"Directory benchmark: {benchmark_dir}")
    logger.info(f"Selezione per entropia: {use_entropy_selection}")
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
    
    # SELEZIONE INTELLIGENTE DEI FILE
    if use_entropy_selection:
        print(f"\nSELEZIONE INTELLIGENTE BASATA SU ENTROPIA")
        print("="*60)
        print("Analizzando le matrici per selezionare un campione rappresentativo...")
        
        try:
            # Usa il selettore di entropia per scegliere le matrici più diverse
            matrix_files = select_matrices_by_entropy(benchmark_dir, max_files)
            logger.info(f"Selezione per entropia completata: {len(matrix_files)} matrici")
            
        except Exception as e:
            print(f"Errore nella selezione per entropia: {e}")
            print("Fallback alla selezione standard...")
            logger.warning(f"Fallback selezione standard: {e}")
            
            # Fallback: selezione standard
            matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
            if matrix_files:
                matrix_files = sorted(matrix_files)[:max_files]
            use_entropy_selection = False
    else:
        # Selezione standard: primi N file
        matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
        if matrix_files:
            matrix_files = sorted(matrix_files)[:max_files]
            print(f"Selezione standard: primi {len(matrix_files)} file")
    
    if not matrix_files:
        print(f"Nessun file .matrix trovato in: {benchmark_dir}")
        return False
    
    print(f"\nELABORAZIONE {len(matrix_files)} MATRICI SELEZIONATE")
    if use_entropy_selection:
        print("Matrici selezionate per diversità di entropia")
    else:
        print("Matrici selezionate in ordine alfabetico")
    
    print(f"Timeout per file: {timeout}s")
    print(f"Limite dimensione: {max_size}MB")
    
    # Il resto della funzione rimane uguale...
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
                'ones_count': int(np.count_nonzero(calculator.matrix))
            }
            results_summary.append(result)
            
    except KeyboardInterrupt:
        print("\n--- Interruzione da tastiera intercettata! ---")
        print("Salvataggio dei dati in corso...")
        time.sleep(3)
        save_compito2(output_dir, logger, should_finalize, matrix_files, results_summary, total_start_time, interrupted=True)
        sys.exit(0)
    except Exception as e:
        print(f"Errore: {e}")
        results_summary.append({
            'file': os.path.basename(matrix_file),
            'error': str(e)
        })
            
    save_compito2(output_dir, logger, should_finalize, matrix_files, results_summary, total_start_time)
    return True
