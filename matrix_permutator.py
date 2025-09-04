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
            
        except KeyboardInterrupt:
            raise
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
        
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Errore nel salvataggio: {e}")
    
    def generate_systematic_permutations(self, max_permutations: int = 10) -> List[Tuple[List[int], List[int]]]:
        """
        Genera solo permutazioni delle colonne (righe identità).
        Args:
            max_permutations: Numero massimo di permutazioni da generare
        Returns:
            Lista di tuple (row_permutation, col_permutation)
        """
        permutations = []
        identity_rows = list(range(self.n_rows))
        identity_cols = list(range(self.n_cols))
        # 1. Identità (nessuna permutazione)
        permutations.append((identity_rows, identity_cols))
        # 2+. Solo permutazioni colonne (righe identità)
        seen_cols = {tuple(identity_cols)}
        while len(permutations) < max_permutations:
            random_cols = self.generate_random_permutation(self.n_cols)
            tcols = tuple(random_cols)
            if tcols not in seen_cols:
                permutations.append((identity_rows, random_cols))
                seen_cols.add(tcols)
        return permutations[:max_permutations]
    
    def generate_permutation_files(self, output_dir: str, max_permutations: int = 10, columns_to_keep=None):
        """
        Genera multiple permutazioni e le salva su file, riducendo solo sulle colonne specificate se columns_to_keep è fornito.
        Args:
            output_dir: Directory di output
            max_permutations: Numero massimo di permutazioni da generare
            columns_to_keep: lista di colonne (indici originali) da tenere dopo la permutazione
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        base_name = os.path.splitext(os.path.basename(self.matrix_file))[0]
        permutations = self.generate_systematic_permutations(max_permutations)
        print(f"Generazione di {len(permutations)} permutazioni...")
        for i, (row_perm, col_perm) in enumerate(permutations):
            # Genera matrice permutata
            permuted_matrix = self.permute_both(row_perm, col_perm)
            # Se columns_to_keep è fornito, riduci la matrice permutata sulle stesse colonne dell'originale
            if columns_to_keep is not None:
                # Calcola la mappatura delle colonne permutate rispetto all'originale
                # columns_to_keep sono indici rispetto all'originale
                # col_perm è la permutazione applicata (posizione permutata -> indice originale)
                # Dobbiamo trovare, nella matrice permutata, quali colonne corrispondono a quelle da tenere
                permuted_cols_to_keep = [col_perm.index(orig) for orig in columns_to_keep]
                # Riduci la matrice permutata
                reduced_matrix = []
                for row in permuted_matrix:
                    reduced_row = [row[j] for j in permuted_cols_to_keep]
                    reduced_matrix.append(reduced_row)
                permuted_matrix = reduced_matrix
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
