#!/usr/bin/env python3
"""
Selettore di matrici basato sull'entropia
=========================================

Modulo per selezionare un sottoinsieme rappresentativo di matrici
basato sulla distribuzione dell'entropia.
"""

import os
import glob
import numpy as np
import math
from typing import List, Tuple
import json

class MatrixEntropySelector:
    """Seleziona matrici basandosi sull'entropia per garantire diversità strutturale"""
    
    def __init__(self, benchmark_dir: str):
        self.benchmark_dir = benchmark_dir
        self.matrix_files = []
        self.entropy_data = []
    
    def calculate_matrix_entropy(self, matrix_file: str) -> float:
        """
        Calcola l'entropia di Shannon per una matrice binaria
        
        Args:
            matrix_file: Path del file matrice
            
        Returns:
            float: Valore di entropia (0 = perfettamente ordinata, ~1 = massima casualità)
        """
        try:
            # Carica la matrice
            with open(matrix_file, 'r') as f:
                lines = f.readlines()
            
            # Parse della matrice 
            matrix_data = []
            for line in lines:
                line = line.strip()
                # Ignora righe vuote, commenti e separatori
                if not line or line.startswith('#') or line.startswith(';') or ';;;' in line:
                    continue
                
                try:
                    # Prova a convertire ogni elemento della riga in intero
                    row = []
                    for element in line.split():
                        # Salta elementi non numerici
                        if element.isdigit() or (element.startswith('-') and element[1:].isdigit()):
                            row.append(int(element))
                        elif element in ['0', '1']:  # Specificamente per matrici binarie
                            row.append(int(element))
                    
                    # Aggiungi solo righe non vuote con elementi validi
                    if row:
                        matrix_data.append(row)
                        
                except ValueError:
                    # Salta righe con errori di parsing
                    continue
            
            if not matrix_data:
                print(f"Attenzione: {os.path.basename(matrix_file)} - nessun dato matrice valido trovato")
                return 0.0
            
            matrix = np.array(matrix_data)
            
            # Calcola l'entropia di Shannon con implementazione nativa
            # Conta 0 e 1 nella matrice
            unique, counts = np.unique(matrix, return_counts=True)
            probabilities = counts / counts.sum()
            
            # Entropia di Shannon (base 2 per matrici binarie)
            # H = -sum(p * log2(p)) dove p sono le probabilità
            matrix_entropy = 0.0
            for p in probabilities:
                if p > 0:  # Evita log(0)
                    matrix_entropy -= p * math.log2(p)
            
            return matrix_entropy
            
        except Exception as e:
            print(f"Errore nel calcolo entropia per {matrix_file}: {e}")
            return 0.0
    
    def analyze_all_matrices(self) -> List[Tuple[str, float, dict]]:
        """
        Analizza tutte le matrici nella directory e calcola le loro entropie
        
        Returns:
            Lista di tuple (filename, entropy, stats)
        """
        print("Analisi entropia delle matrici...")
        
        # Trova tutti i file .matrix
        pattern = os.path.join(self.benchmark_dir, "*.matrix")
        self.matrix_files = glob.glob(pattern)
        
        if not self.matrix_files:
            print(f"Nessun file .matrix trovato in {self.benchmark_dir}")
            return []
        
        print(f"Trovati {len(self.matrix_files)} file da analizzare")
        
        results = []
        
        for i, matrix_file in enumerate(self.matrix_files, 1):
            if i % 10 == 0:
                print(f"Progresso: {i}/{len(self.matrix_files)}")
            
            # Calcola entropia
            matrix_entropy = self.calculate_matrix_entropy(matrix_file)
            
            # Calcola statistiche aggiuntive
            try:
                with open(matrix_file, 'r') as f:
                    lines = f.readlines()
                
                matrix_data = []
                for line in lines:
                    line = line.strip()
                    # Ignora righe vuote, commenti e separatori
                    if not line or line.startswith('#') or line.startswith(';') or ';;;' in line:
                        continue
                    
                    try:
                        # Prova a convertire ogni elemento della riga in intero
                        row = []
                        for element in line.split():
                            # Salta elementi non numerici
                            if element.isdigit() or (element.startswith('-') and element[1:].isdigit()):
                                row.append(int(element))
                            elif element in ['0', '1']:  # Specificamente per matrici binarie
                                row.append(int(element))
                        
                        # Aggiungi solo righe non vuote con elementi validi
                        if row:
                            matrix_data.append(row)
                            
                    except ValueError:
                        # Salta righe con errori di parsing
                        continue
                
                if matrix_data:
                    matrix = np.array(matrix_data)
                    stats = {
                        'rows': matrix.shape[0],
                        'cols': matrix.shape[1],
                        'density': np.mean(matrix),  # Percentuale di 1
                        'file_size_mb': os.path.getsize(matrix_file) / (1024*1024)
                    }
                else:
                    stats = {'rows': 0, 'cols': 0, 'density': 0, 'file_size_mb': 0}
                    
            except:
                stats = {'rows': 0, 'cols': 0, 'density': 0, 'file_size_mb': 0}
            
            results.append((os.path.basename(matrix_file), matrix_entropy, stats))
        
        # Ordina per entropia
        results.sort(key=lambda x: x[1])
        self.entropy_data = results
        
        return results
    
    def select_diverse_matrices(self, target_count: int = 30) -> List[str]:
        """
        Seleziona matrici con entropia diversificata garantendo tutte le categorie di complessità
        
        Args:
            target_count: Numero di matrici da selezionare
            
        Returns:
            Lista dei path delle matrici selezionate
        """
        if not self.entropy_data:
            print("Devi prima eseguire analyze_all_matrices()")
            return []
        
        if len(self.entropy_data) <= target_count:
            print(f"Trovate solo {len(self.entropy_data)} matrici, seleziono tutte")
            return [os.path.join(self.benchmark_dir, item[0]) for item in self.entropy_data]
        
        # Strategia di selezione intelligente per garantire tutte le categorie
        print(f"\nSelezione intelligente di {target_count} matrici da {len(self.entropy_data)} totali")
        print("Strategia: garantire copertura di tutte le categorie di complessità")
        
        # Analizza le matrici per categorizzarle
        categorized_matrices = self._categorize_matrices_by_complexity()
        
        # Calcola quante matrici selezionare per categoria
        matrices_per_category = max(2, target_count // 4)  # Almeno 2 per categoria
        remaining = target_count - (matrices_per_category * 4)
        
        selected_matrices = []
        selected_info = []
        
        categories = ['semplici_veloci', 'semplici_lenti', 'complessi_veloci', 'complessi_lenti']
        
        for i, category in enumerate(categories):
            category_matrices = categorized_matrices.get(category, [])
            
            # Aggiungi matrici extra alle prime categorie se c'è resto
            count_for_this_category = matrices_per_category
            if i < remaining:
                count_for_this_category += 1
            
            # Seleziona matrici da questa categoria
            if category_matrices:
                # Distribuzione uniforme all'interno della categoria
                if len(category_matrices) <= count_for_this_category:
                    selected_from_category = category_matrices
                else:
                    step = len(category_matrices) / count_for_this_category
                    indices = [int(j * step) for j in range(count_for_this_category)]
                    selected_from_category = [category_matrices[idx] for idx in indices]
                
                for filename, entropy_val, stats in selected_from_category:
                    full_path = os.path.join(self.benchmark_dir, filename)
                    selected_matrices.append(full_path)
                    selected_info.append((filename, entropy_val, stats, category))
            
            # Non stampare qui per evitare duplicazione
        
        # Se non abbiamo abbastanza matrici, riempi con distribuzione uniforme per entropia
        if len(selected_matrices) < target_count:
            remaining_needed = target_count - len(selected_matrices)
            already_selected = {info[0] for info in selected_info}
            
            # Seleziona matrici rimanenti con distribuzione uniforme
            available_matrices = [(f, e, s) for f, e, s in self.entropy_data if f not in already_selected]
            if available_matrices:
                step = len(available_matrices) / remaining_needed
                indices = [int(i * step) for i in range(remaining_needed)]
                
                for idx in indices:
                    if idx < len(available_matrices):
                        filename, entropy_val, stats = available_matrices[idx]
                        full_path = os.path.join(self.benchmark_dir, filename)
                        selected_matrices.append(full_path)
                        selected_info.append((filename, entropy_val, stats, 'uniforme'))
        
        # Ordina per entropia per il report
        selected_info.sort(key=lambda x: x[1])
        
        # Stampa informazioni sulla selezione
        print(f"\nMatrici selezionate (ordinate per entropia):")
        print("-" * 90)
        print(f"{'File':<25} {'Entropia':<10} {'Dimensioni':<12} {'Densità':<8} {'Size(MB)':<8} {'Categoria':<15}")
        print("-" * 90)
        
        for filename, entropy_val, stats, category in selected_info:
            print(f"{filename:<25} {entropy_val:<10.4f} "
                  f"{stats['rows']}×{stats['cols']:<6} "
                  f"{stats['density']:<8.3f} {stats['file_size_mb']:<8.2f} {category:<15}")
        
        print("-" * 90)
        print(f"Range entropia: {selected_info[0][1]:.4f} → {selected_info[-1][1]:.4f}")
        print(f"Totale selezionate: {len(selected_matrices)} matrici")
        
        return selected_matrices
    
    def _categorize_matrices_by_complexity(self):
        """
        Categorizza le matrici in base a dimensioni e entropia per predire complessità
        
        Returns:
            Dict con liste di matrici per categoria
        """
        if not self.entropy_data:
            return {}
        
        # Calcola soglie per dimensioni
        all_sizes = [(stats['rows'] * stats['cols']) for _, _, stats in self.entropy_data]
        median_size = np.median(all_sizes)
        
        # Calcola soglie per entropia (predittore di complessità algoritmica)
        all_entropies = [entropy for _, entropy, _ in self.entropy_data]
        entropy_33 = np.percentile(all_entropies, 33)
        entropy_66 = np.percentile(all_entropies, 66)
        
        categories = {
            'semplici_veloci': [],    # Piccole + alta entropia (casuali, si risolvono velocemente)
            'semplici_lenti': [],     # Piccole + bassa entropia (ordinate, algoritmo lavora di più)
            'complessi_veloci': [],   # Grandi + alta entropia (casuali, si risolvono bene)
            'complessi_lenti': []     # Grandi + bassa entropia (grandi e ordinate, molto lenti)
        }
        
        for filename, entropy_val, stats in self.entropy_data:
            matrix_size = stats['rows'] * stats['cols']
            
            is_large = matrix_size > median_size
            
            # Logica di categorizzazione basata su dimensioni ed entropia
            if not is_large:  # Matrici piccole
                if entropy_val > entropy_66:
                    categories['semplici_veloci'].append((filename, entropy_val, stats))
                else:
                    categories['semplici_lenti'].append((filename, entropy_val, stats))
            else:  # Matrici grandi
                if entropy_val > entropy_33:
                    categories['complessi_veloci'].append((filename, entropy_val, stats))
                else:
                    categories['complessi_lenti'].append((filename, entropy_val, stats))
        
        # Stampa statistiche categorie solo una volta
        print(f"\nCategorizzazione automatica:")
        print(f"   Soglia dimensioni: {median_size:.0f} elementi")
        print(f"   Soglie entropia: {entropy_33:.3f} | {entropy_66:.3f}")
        for cat_name, matrices in categories.items():
            print(f"   {cat_name.replace('_', ' ').title()}: {len(matrices)} matrici")
        
        return categories
    
    def save_analysis_report(self, output_dir: str = "results"):
        """Salva un report dettagliato dell'analisi dell'entropia"""
        if not self.entropy_data:
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva dati JSON
        json_data = {
            'analysis_info': {
                'total_matrices': len(self.entropy_data),
                'benchmark_dir': self.benchmark_dir,
                'entropy_range': {
                    'min': min(item[1] for item in self.entropy_data),
                    'max': max(item[1] for item in self.entropy_data),
                    'mean': np.mean([item[1] for item in self.entropy_data])
                }
            },
            'matrices': [
                {
                    'filename': item[0],
                    'entropy': item[1],
                    'stats': item[2]
                }
                for item in self.entropy_data
            ]
        }
        
        json_file = os.path.join(output_dir, "entropy_analysis.json")
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"Report entropia salvato in: {json_file}")
        
        # Salva anche un CSV semplice per analisi
        csv_file = os.path.join(output_dir, "entropy_analysis.csv")
        with open(csv_file, 'w') as f:
            f.write("filename,entropy,rows,cols,density,file_size_mb\n")
            for item in self.entropy_data:
                filename, entropy_val, stats = item
                f.write(f"{filename},{entropy_val},{stats['rows']},{stats['cols']},{stats['density']},{stats['file_size_mb']}\n")
        
        print(f"Report CSV salvato in: {csv_file}")
        
        return json_file, csv_file


def select_matrices_by_entropy(benchmark_dir: str, target_count: int = 30) -> List[str]:
     
    selector = MatrixEntropySelector(benchmark_dir)
    selector.analyze_all_matrices()
    selected = selector.select_diverse_matrices(target_count)
    selector.save_analysis_report()
    
    return selected


if __name__ == "__main__":
    import sys
    import argparse
    
    # Parser degli argomenti
    parser = argparse.ArgumentParser(description="Selettore di matrici basato sull'entropia di Shannon")
    parser.add_argument("directory", nargs="?", default="benchmarks", 
                       help="Directory contenente i file .matrix (default: benchmarks)")
    parser.add_argument("--num-matrices", "-n", type=int, default=15,
                       help="Numero di matrici da selezionare (default: 15)")
    
    args = parser.parse_args()
    
    # Test del selettore
    if os.path.exists(args.directory):
        print(f"Test del selettore di entropia")
        print(f"Directory: {args.directory}")
        print(f"Target matrici: {args.num_matrices}")
        selected = select_matrices_by_entropy(args.directory, args.num_matrices)
        print(f"\nSelezionate {len(selected)} matrici")
    else:
        print(f"Directory {args.directory} non trovata")
