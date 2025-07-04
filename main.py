#!/usr/bin/env python3
"""
Main Script per l'Elaborato 2023-2024
======================================

Script principale che integra tutti i componenti:
- Compito 1: Calcolo MHS
- Compito 2: Sperimentazione
- Compito 3: Permutazioni e confronti

Autore: Mattia Pavlovic
"""

import os
import sys
import argparse
import time
import glob
from mhs_calculator import MHSCalculator
from matrix_permutator import MatrixPermutator
from mhs_comparator import MHSComparator

def compito_1_calcolo_mhs(input_file: str, output_file: str = None, timeout: int = 300, max_size: int = 50):
    """
    Compito 1: Calcolo dei Minimal Hitting Set con timeout e limiti
    """
    print("🎯 COMPITO 1: Calcolo Minimal Hitting Set")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
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
                print(f"✓ Creata cartella output: {output_dir}")
            output_file = os.path.join(output_dir, f"{base_name}.mhs")
        else:
            output_file = f"{base_name}.mhs"
    
    # Calcola MHS con timeout e limiti
    calculator = MHSCalculator(input_file, timeout_seconds=timeout, max_file_size_mb=max_size)
    mhs_list = calculator.run(output_file)
    
    # Verifica risultato
    if calculator.statistics.get('interrupted_by_timeout', False):
        print(f"⚠️  Compito 1 completato con timeout. Risultati parziali in: {output_file}")
        return True  # Comunque considerato successo per continuare
    elif calculator.statistics.get('interrupted_by_size', False):
        print(f"⚠️  File troppo grande per Compito 1. Stato salvato in: {output_file}")
        return True
    else:
        print(f"✅ Compito 1 completato. Risultati in: {output_file}")
        return True

def compito_2_sperimentazione(benchmark_dir: str, output_dir: str = None, timeout: int = 300, max_size: int = 50, max_files: int = 10):
    """
    Compito 2: Sperimentazione sui benchmark con timeout e limiti
    """
    print("\n🧪 COMPITO 2: Sperimentazione sui benchmark")
    print("="*50)
    
    if not os.path.exists(benchmark_dir):
        print(f"❌ Directory benchmark non trovata: {benchmark_dir}")
        return False
    
    # Crea directory output dentro la cartella benchmark
    if not output_dir:
        output_dir = os.path.join(benchmark_dir, "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Creata cartella output: {output_dir}")
    else:
        print(f"✓ Utilizzando cartella output: {output_dir}")
    
    # Trova tutti i file .matrix
    matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
    
    if not matrix_files:
        print(f"❌ Nessun file .matrix trovato in: {benchmark_dir}")
        return False
    
    print(f"📁 Trovati {len(matrix_files)} file di benchmark")
    
    # Limita il numero di file per evitare tempi eccessivi
    matrix_files = sorted(matrix_files)[:max_files]
    print(f"🎯 Elaborazione dei primi {len(matrix_files)} file...")
    print(f"⏰ Timeout per file: {timeout}s")
    print(f"📊 Limite dimensione: {max_size}MB")
    
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
            
            # Raccogli risultati
            result = {
                'file': os.path.basename(matrix_file),
                'matrix_size': f"{calculator.n_rows}×{calculator.n_cols}",
                'reduced_size': f"{calculator.n_rows}×{calculator.n_cols_reduced}",
                'mhs_count': len(mhs_list) if mhs_list else 0,
                'computation_time': end_time - start_time,
                'hypotheses_generated': calculator.statistics.get('hypotheses_generated', 0),
                'timeout': calculator.statistics.get('interrupted_by_timeout', False),
                'size_limit': calculator.statistics.get('interrupted_by_size', False)
            }
            results_summary.append(result)
            
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            results_summary.append({
                'file': os.path.basename(matrix_file),
                'error': str(e)
            })
    
    total_time = time.time() - total_start_time
    
    # Stampa riassunto
    print(f"\n📊 RIASSUNTO SPERIMENTAZIONE")
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
    print(f"✅ Compito 2 completato. Risultati in: {output_dir}")
    return True

def compito_3_permutazioni(input_file: str, num_permutations: int = 5, timeout: int = 300, max_size: int = 50):
    """
    Compito 3: Permutazioni e confronti con timeout e limiti
    """
    print(f"\n🔄 COMPITO 3: Permutazioni e confronti")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        return False
    
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    perm_dir = f"permutations_{base_name}"
    
    # Genera permutazioni
    print(f"🔄 Generazione di {num_permutations} permutazioni...")
    permutator = MatrixPermutator(input_file)
    
    if not permutator.load_matrix():
        return False
    
    permutator.generate_permutation_files(perm_dir, num_permutations)
    
    # Confronta i risultati con timeout
    print(f"\n🔍 Confronto risultati delle permutazioni (timeout: {timeout}s)...")
    pattern = os.path.join(perm_dir, "*.matrix")
    matrix_files = glob.glob(pattern)
    
    if matrix_files:
        # Calcola MHS per ogni permutazione con timeout
        print(f"📊 Calcolando MHS per {len(matrix_files)} permutazioni...")
        
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
                print(f"   ❌ Errore su {matrix_file}: {e}")
                results.append({
                    'file': os.path.basename(matrix_file),
                    'error': str(e)
                })
        
        # Stampa riassunto confronti
        print(f"\n📊 RIASSUNTO CONFRONTO PERMUTAZIONI")
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
            print(f"⚠️  Errore nel comparatore: {e}")
    else:
        print(f"❌ Nessun file di permutazione trovato in: {perm_dir}")
        return False
    
    print(f"✅ Compito 3 completato. File in: {perm_dir}")
    return True

def run_complete_experiment(timeout: int = 300, max_size: int = 50):
    """
    Esegue l'esperimento completo su tutti e tre i compiti con timeout e limiti
    """
    print("🚀 ELABORATO 2023-2024: Calcolo Minimal Hitting Set")
    print("="*60)
    print("Autore: Mattia Pavlovic")
    print("Data:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"⏰ Timeout per file: {timeout}s")
    print(f"📊 Limite dimensione: {max_size}MB")
    print("="*60)
    
    # Controlla se esistono i benchmark
    benchmark_dirs = ["benchmarks1", "benchmarks2"]
    available_benchmarks = [d for d in benchmark_dirs if os.path.exists(d)]
    
    if not available_benchmarks:
        print("⚠️  Nessuna directory di benchmark trovata")
        print("Creazione di un esempio di test...")
        
        # Crea esempio di test
        test_matrix = """;;; Test example for MHS calculation
;;; Example from course material
0 0 0 1 1
1 1 0 0 1
0 1 1 1 1
"""
        with open('test_example.matrix', 'w') as f:
            f.write(test_matrix)
        
        # Compito 1: Test con esempio
        if compito_1_calcolo_mhs('test_example.matrix', timeout=timeout, max_size=max_size):
            # Compito 3: Permutazioni dell'esempio
            compito_3_permutazioni('test_example.matrix', 3, timeout=timeout, max_size=max_size)
        
        # Cleanup
        if os.path.exists('test_example.matrix'):
            os.remove('test_example.matrix')
        if os.path.exists('test_example.mhs'):
            os.remove('test_example.mhs')
    else:
        # Usa i benchmark reali
        benchmark_dir = available_benchmarks[0]
        
        # Compito 2: Sperimentazione
        compito_2_sperimentazione(benchmark_dir, timeout=timeout, max_size=max_size, max_files=5)
        
        # Compito 1 e 3: Su un file specifico
        matrix_files = glob.glob(os.path.join(benchmark_dir, "*.matrix"))
        if matrix_files:
            test_file = matrix_files[0]  # Prendi il primo file
            
            # Compito 1
            compito_1_calcolo_mhs(test_file, timeout=timeout, max_size=max_size)
            
            # Compito 3
            compito_3_permutazioni(test_file, 3, timeout=timeout, max_size=max_size)
    
    print(f"\n🎉 ESPERIMENTO COMPLETO TERMINATO")
    print("="*60)

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
  python main.py --test                         # Test con esempio semplice
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
    parser.add_argument('--test', action='store_true',
                       help='Esegue un test con l\'esempio del PDF')
    parser.add_argument('--output', '-o', metavar='DIR', default='results',
                       help='Directory di output (default: results)')
    parser.add_argument('--num-permutations', type=int, default=5,
                       help='Numero di permutazioni per Compito 3 (default: 5)')
    
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
    
    print(f"🚀 MHS Calculator - Configurazione:")
    print(f"   ⏰ Timeout: {args.timeout}s")
    print(f"   📊 Limite dimensione: {args.max_size}MB")
    print(f"   📁 Max file batch: {args.max_files}")
    print("-" * 50)
    
    # Esegui i compiti richiesti
    if args.all:
        run_complete_experiment(timeout=args.timeout, max_size=args.max_size)
    elif args.test:
        # Test con esempio semplice
        test_matrix = """;;; Test example from PDF
0 0 0 1 1
1 1 0 0 1
0 1 1 1 1
"""
        with open('test_example.matrix', 'w') as f:
            f.write(test_matrix)
        
        compito_1_calcolo_mhs('test_example.matrix', timeout=args.timeout, max_size=args.max_size)
        
        # Cleanup
        for f in ['test_example.matrix', 'test_example.mhs']:
            if os.path.exists(f):
                os.remove(f)
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
