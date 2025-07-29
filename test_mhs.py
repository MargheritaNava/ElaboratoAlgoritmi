#!/usr/bin/env python3
"""
Script di test per MHSCalculator
"""

import os
import sys
import time
from mhs_calculator import MHSCalculator

def test_simple_example():
    """
    Test con l'esempio del PDF:
    N = { {B3,B4}, {A1,A2,B4}, {A2,A5,B3,B4} }
    MHS = { {B4}, {A1,B3}, {A2,B3} }
    """
    print("Test esempio semplice dal PDF")
    print("="*50)
    
    # Crea file temporaneo con l'esempio
    test_matrix = """;;; Test example from PDF
;;; Map A1(1) A2(2) A5(3) B3(4) B4(5)
0 0 0 1 1
1 1 0 0 1
0 1 1 1 1
"""
    
    with open('test_example.matrix', 'w') as f:
        f.write(test_matrix)
    
    # Esegui il calcolo
    calculator = MHSCalculator('test_example.matrix')
    mhs_list = calculator.run('test_example.mhs')
    
    print(f"\nTest completato")
    print(f"MHS trovati: {len(mhs_list)}")
    for i, mhs in enumerate(mhs_list):
        print(f"  MHS {i+1}: {sorted(mhs)}")
    
    # Cleanup
    os.remove('test_example.matrix')
    if os.path.exists('test_example.mhs'):
        os.remove('test_example.mhs')
    
    print()

def test_benchmark_file(benchmark_file: str):
    """
    Test con un file di benchmark
    """
    if not os.path.exists(benchmark_file):
        print(f"File {benchmark_file} non trovato")
        return
    
    print(f"Test file: {os.path.basename(benchmark_file)}")
    print("="*50)
    
    start_time = time.time()
    
    # Crea nome file di output
    base_name = os.path.splitext(benchmark_file)[0]
    output_file = f"{base_name}.mhs"
    
    # Esegui il calcolo
    calculator = MHSCalculator(benchmark_file)
    mhs_list = calculator.run(output_file)
    
    end_time = time.time()
    
    print(f"\nTest completato in {end_time - start_time:.3f} secondi")
    print(f"MHS trovati: {len(mhs_list) if mhs_list else 0}")
    
    # Mostra alcuni MHS di esempio
    if mhs_list and len(mhs_list) <= 10:
        print("MHS trovati:")
        for i, mhs in enumerate(mhs_list):
            print(f"  MHS {i+1}: {sorted(mhs)}")
    elif mhs_list:
        print("Primi 5 MHS:")
        for i, mhs in enumerate(mhs_list[:5]):
            print(f"  MHS {i+1}: {sorted(mhs)}")
    
    print()

def main():
    """
    Esegue i test
    """
    print("Avvio test MHS Calculator")
    print("="*60)
    
    # Test esempio semplice
    test_simple_example()
    
    # Test con file di benchmark
    benchmark_dir = "benchmarks"
    if os.path.exists(benchmark_dir):
        # Prova con alcuni file di benchmark
        test_files = [
            os.path.join(benchmark_dir, "74181.000.matrix"),
            os.path.join(benchmark_dir, "74181.001.matrix"),
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                test_benchmark_file(test_file)
            else:
                print(f"File {test_file} non trovato")
    else:
        print(f"Cartella {benchmark_dir} non trovata")

    print("Test completati")

if __name__ == "__main__":
    main()
