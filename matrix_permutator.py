#!/usr/bin/env python3
"""
Matrix Permutation Generator
============================

Genera permutazioni di righe e/o colonne per file .matrix
come richiesto nel Compito 3 dell'elaborato.
"""

import os
import random
import argparse
from typing import List, Tuple
import itertools

class MatrixPermutator:
    """
    Classe per generare permutazioni di matrici
    """
    
    def __init__(self, matrix_file: str):
        """
        Inizializza il permutatore
        
        Args:
            matrix_file: Path al file .matrix di input
        """
        self.matrix_file = matrix_file
        self.header_lines = []
        self.matrix = []
        self.n_rows = 0
        self.n_cols = 0
    
    def load_matrix(self) -> bool:
        """
        Carica la matrice dal file
        
        Returns:
            True se caricamento riuscito, False altrimenti
        """
        try:
            with open(self.matrix_file, 'r') as f:
                lines = f.readlines()
            
            self.header_lines = []
            self.matrix = []
            
            # Separa header e matrice
            matrix_started = False
            for line in lines:
                line = line.strip()
                if line.startswith(';;;'):
                    self.header_lines.append(line)
                elif line and not matrix_started:
                    matrix_started = True
                    # Prima riga della matrice
                    if line.endswith('-'):
                        line = line[:-1].strip()
                    row = [int(x) for x in line.split() if x.isdigit()]
                    if row:
                        self.matrix.append(row)
                elif line:
                    # Altre righe della matrice
                    if line.endswith('-'):
                        line = line[:-1].strip()
                    row = [int(x) for x in line.split() if x.isdigit()]
                    if row:
                        self.matrix.append(row)
            
            self.n_rows = len(self.matrix)
            self.n_cols = len(self.matrix[0]) if self.matrix else 0
            
            print(f"Matrice caricata: {self.n_rows} righe, {self.n_cols} colonne")
            return True
            
        except Exception as e:
            print(f"Errore nel caricamento: {e}")
            return False
    
    def permute_rows(self, row_permutation: List[int]) -> List[List[int]]:
        """
        Permuta le righe della matrice
        
        Args:
            row_permutation: Lista degli indici di riga permutati
            
        Returns:
            Matrice con righe permutate
        """
        if len(row_permutation) != self.n_rows:
            raise ValueError("La permutazione deve avere la stessa lunghezza del numero di righe")
        
        permuted_matrix = []
        for new_row_idx in row_permutation:
            permuted_matrix.append(self.matrix[new_row_idx].copy())
        
        return permuted_matrix
    
    def permute_columns(self, col_permutation: List[int]) -> List[List[int]]:
        """
        Permuta le colonne della matrice
        
        Args:
            col_permutation: Lista degli indici di colonna permutati
            
        Returns:
            Matrice con colonne permutate
        """
        if len(col_permutation) != self.n_cols:
            raise ValueError("La permutazione deve avere la stessa lunghezza del numero di colonne")
        
        permuted_matrix = []
        for row in self.matrix:
            new_row = []
            for new_col_idx in col_permutation:
                new_row.append(row[new_col_idx])
            permuted_matrix.append(new_row)
        
        return permuted_matrix
    
    def permute_both(self, row_permutation: List[int], col_permutation: List[int]) -> List[List[int]]:
        """
        Permuta sia righe che colonne
        
        Args:
            row_permutation: Lista degli indici di riga permutati
            col_permutation: Lista degli indici di colonna permutati
            
        Returns:
            Matrice completamente permutata
        """
        # Prima permuta le righe
        temp_matrix = self.permute_rows(row_permutation)
        
        # Poi permuta le colonne
        permuted_matrix = []
        for row in temp_matrix:
            new_row = []
            for new_col_idx in col_permutation:
                new_row.append(row[new_col_idx])
            permuted_matrix.append(new_row)
        
        return permuted_matrix
    
    def generate_random_permutation(self, size: int) -> List[int]:
        """
        Genera una permutazione casuale
        
        Args:
            size: Dimensione della permutazione
            
        Returns:
            Lista di indici permutati casualmente
        """
        indices = list(range(size))
        random.shuffle(indices)
        return indices
    
    def save_permuted_matrix(self, permuted_matrix: List[List[int]], 
                           output_file: str, 
                           row_perm: List[int] = None, 
                           col_perm: List[int] = None):
        """
        Salva la matrice permutata su file
        
        Args:
            permuted_matrix: Matrice permutata
            output_file: Path del file di output
            row_perm: Permutazione delle righe (opzionale)
            col_perm: Permutazione delle colonne (opzionale)
        """
        try:
            with open(output_file, 'w') as f:
                # Scrivi header modificato
                for line in self.header_lines:
                    f.write(line + '\n')
                
                # Aggiungi informazioni sulla permutazione
                f.write(f";;; Permuted from: {os.path.basename(self.matrix_file)}\n")
                if row_perm:
                    f.write(f";;; Row permutation: {row_perm}\n")
                if col_perm:
                    f.write(f";;; Column permutation: {col_perm}\n")
                
                # Scrivi la matrice permutata
                for row in permuted_matrix:
                    f.write(' '.join(map(str, row)) + ' -\n')
            
            print(f"Matrice permutata salvata in: {output_file}")
            
        except Exception as e:
            print(f"Errore nel salvataggio: {e}")
    
    def generate_systematic_permutations(self, max_permutations: int = 10) -> List[Tuple[List[int], List[int]]]:
        """
        Genera permutazioni sistematiche per valutare le prestazioni
        
        Args:
            max_permutations: Numero massimo di permutazioni da generare
            
        Returns:
            Lista di tuple (row_permutation, col_permutation)
        """
        permutations = []
        
        # 1. Identità (nessuna permutazione)
        identity_rows = list(range(self.n_rows))
        identity_cols = list(range(self.n_cols))
        permutations.append((identity_rows, identity_cols))
        
        # 2. Permutazione solo righe (casuale)
        if max_permutations > 1:
            random_rows = self.generate_random_permutation(self.n_rows)
            permutations.append((random_rows, identity_cols))
        
        # 3. Permutazione solo colonne (casuale)
        if max_permutations > 2:
            random_cols = self.generate_random_permutation(self.n_cols)
            permutations.append((identity_rows, random_cols))
        
        # 4. Permutazione sia righe che colonne
        if max_permutations > 3:
            random_rows = self.generate_random_permutation(self.n_rows)
            random_cols = self.generate_random_permutation(self.n_cols)
            permutations.append((random_rows, random_cols))
        
        # 5. Reverse delle righe
        if max_permutations > 4:
            reverse_rows = list(reversed(range(self.n_rows)))
            permutations.append((reverse_rows, identity_cols))
        
        # 6. Reverse delle colonne
        if max_permutations > 5:
            reverse_cols = list(reversed(range(self.n_cols)))
            permutations.append((identity_rows, reverse_cols))
        
        # 7-10. Permutazioni casuali aggiuntive
        while len(permutations) < max_permutations:
            random_rows = self.generate_random_permutation(self.n_rows)
            random_cols = self.generate_random_permutation(self.n_cols)
            new_perm = (random_rows, random_cols)
            
            # Evita duplicati
            if new_perm not in permutations:
                permutations.append(new_perm)
        
        return permutations[:max_permutations]
    
    def generate_permutation_files(self, output_dir: str, max_permutations: int = 10):
        """
        Genera multiple permutazioni e le salva su file
        
        Args:
            output_dir: Directory di output
            max_permutations: Numero massimo di permutazioni da generare
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(self.matrix_file))[0]
        permutations = self.generate_systematic_permutations(max_permutations)
        
        print(f"Generazione di {len(permutations)} permutazioni...")
        
        for i, (row_perm, col_perm) in enumerate(permutations):
            # Genera matrice permutata
            permuted_matrix = self.permute_both(row_perm, col_perm)
            
            # Nome file di output
            output_file = os.path.join(output_dir, f"{base_name}_perm_{i:02d}.matrix")
            
            # Salva
            self.save_permuted_matrix(permuted_matrix, output_file, row_perm, col_perm)
            
            # Descrizione della permutazione
            perm_type = []
            if row_perm != list(range(self.n_rows)):
                perm_type.append("rows")
            if col_perm != list(range(self.n_cols)):
                perm_type.append("cols")
            
            if not perm_type:
                print(f"  Perm {i:02d}: Identity (no permutation)")
            else:
                print(f"  Perm {i:02d}: {' + '.join(perm_type)} permuted")


def main():
    """
    Funzione principale
    """
    parser = argparse.ArgumentParser(
        description='Genera permutazioni di file .matrix'
    )
    parser.add_argument('input_file', help='File .matrix di input')
    parser.add_argument('-o', '--output-dir', default='permutations', 
                       help='Directory di output (default: permutations)')
    parser.add_argument('-n', '--num-permutations', type=int, default=10,
                       help='Numero di permutazioni da generare (default: 10)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Seed per la generazione casuale (default: 42)')
    
    args = parser.parse_args()
    
    # Imposta seed per riproducibilità
    random.seed(args.seed)
    
    # Genera permutazioni
    permutator = MatrixPermutator(args.input_file)
    
    if permutator.load_matrix():
        permutator.generate_permutation_files(args.output_dir, args.num_permutations)
        print(f"Permutazioni generate in: {args.output_dir}")
    else:
        print("Impossibile caricare la matrice")


if __name__ == "__main__":
    main()
