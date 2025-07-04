#!/usr/bin/env python3
"""
Configurazione finale del progetto
"""

import os
import sys

def setup_project():
    """
    Configurazione finale del progetto
    """
    print("🚀 Configurazione finale del progetto MHS Calculator")
    print("="*60)
    
    # Verifica file principali
    required_files = [
        'main.py',
        'mhs_calculator.py',
        'matrix_permutator.py',
        'mhs_comparator.py',
        'test_mhs.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ File mancanti: {', '.join(missing_files)}")
        return False
    
    print("✅ Tutti i file principali sono presenti")
    
    # Verifica directory benchmark
    benchmark_dirs = ['benchmarks1', 'benchmarks2']
    found_benchmarks = []
    
    for dir_name in benchmark_dirs:
        if os.path.exists(dir_name):
            matrix_files = [f for f in os.listdir(dir_name) if f.endswith('.matrix')]
            if matrix_files:
                found_benchmarks.append(f"{dir_name}: {len(matrix_files)} file")
    
    if found_benchmarks:
        print(f"✅ Benchmark disponibili:")
        for info in found_benchmarks:
            print(f"   - {info}")
    else:
        print("⚠️  Nessuna directory di benchmark trovata")
    
    # Test rapido
    print("\n🧪 Test rapido del sistema...")
    try:
        from mhs_calculator import MHSCalculator
        print("✅ mhs_calculator importato correttamente")
        
        from matrix_permutator import MatrixPermutator
        print("✅ matrix_permutator importato correttamente")
        
        from mhs_comparator import MHSComparator
        print("✅ mhs_comparator importato correttamente")
        
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        return False
    
    print("\n📋 ISTRUZIONI D'USO:")
    print("="*40)
    print("1. Test rapido:")
    print("   python main.py --test")
    print()
    print("2. Calcolo MHS singolo file:")
    print("   python main.py --compito1 benchmarks1/74181.000.matrix")
    print()
    print("3. Sperimentazione completa:")
    print("   python main.py --compito2 benchmarks1/")
    print()
    print("4. Permutazioni e confronti:")
    print("   python main.py --compito3 benchmarks1/74181.000.matrix")
    print()
    print("5. Esperimento completo:")
    print("   python main.py --all")
    print()
    print("📚 Per maggiori dettagli: python main.py --help")
    print("📖 Documentazione completa: cat README.md")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    if success:
        print("\n🎉 PROGETTO CONFIGURATO CORRETTAMENTE!")
        print("="*60)
    else:
        print("\n❌ CONFIGURAZIONE FALLITA")
        sys.exit(1)
