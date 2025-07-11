#!/usr/bin/env python3
"""
Execution Manager for Unique Report Organization
===============================================

Gestore per organizzare i report di ogni esecuzione in directory univoche.
"""

import os
import datetime
import json
import shutil
from typing import Dict, List, Optional

class ExecutionManager:
    """
    Gestisce la creazione e organizzazione di directory univoche per ogni esecuzione
    """
    
    def __init__(self, base_dir: str = "results/analysis"):
        """
        Inizializza il gestore delle esecuzioni
        
        Args:
            base_dir: Directory base dove creare le cartelle di esecuzione
        """
        self.base_dir = base_dir
        self.execution_id = self._generate_execution_id()
        self.execution_dir = os.path.join(base_dir, self.execution_id)
        
        # Crea la directory principale
        os.makedirs(self.execution_dir, exist_ok=True)
        
        # Lista dei file generati durante l'esecuzione
        self.generated_files = []
        
        print(f"Nuova esecuzione avviata - ID: {self.execution_id}")
        print(f"Directory report: {self.execution_dir}")
    
    def _generate_execution_id(self) -> str:
        """Genera un ID univoco per l'esecuzione basato su timestamp"""
        timestamp = datetime.datetime.now()
        return f"esecuzione_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def get_execution_dir(self) -> str:
        """Restituisce il percorso della directory di esecuzione"""
        return self.execution_dir
    
    def get_execution_id(self) -> str:
        """Restituisce l'ID dell'esecuzione"""
        return self.execution_id
    
    def register_file(self, file_path: str, file_type: str = "unknown", description: str = ""):
        """
        Registra un file generato durante l'esecuzione
        
        Args:
            file_path: Percorso del file generato
            file_type: Tipo di file (json, csv, png, etc.)
            description: Descrizione del contenuto del file
        """
        if os.path.exists(file_path):
            self.generated_files.append({
                'path': file_path,
                'filename': os.path.basename(file_path),
                'type': file_type,
                'description': description,
                'size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'relative_path': os.path.relpath(file_path, self.execution_dir)
            })
    
    def move_file_to_execution_dir(self, source_path: str, target_subdir: str = "", 
                                 file_type: str = "unknown", description: str = "") -> Optional[str]:
        """
        Sposta un file nella directory di esecuzione
        
        Args:
            source_path: Percorso del file sorgente
            target_subdir: Sottodirectory opzionale dentro execution_dir
            file_type: Tipo di file
            description: Descrizione del file
            
        Returns:
            Nuovo percorso del file o None se errore
        """
        if not os.path.exists(source_path):
            print(f"File non trovato: {source_path}")
            return None
        
        # Crea sottodirectory se specificata
        target_dir = self.execution_dir
        if target_subdir:
            target_dir = os.path.join(self.execution_dir, target_subdir)
            os.makedirs(target_dir, exist_ok=True)
        
        # Determina il nome del file di destinazione
        filename = os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename)
        
        try:
            # Sposta il file
            shutil.move(source_path, target_path)
            
            # Registra il file
            self.register_file(target_path, file_type, description)
            
            return target_path
            
        except Exception as e:
            print(f"Errore nello spostamento del file {source_path}: {e}")
            return None
    
    def copy_file_to_execution_dir(self, source_path: str, target_subdir: str = "", 
                                 file_type: str = "unknown", description: str = "") -> Optional[str]:
        """
        Copia un file nella directory di esecuzione (mantiene l'originale)
        
        Args:
            source_path: Percorso del file sorgente
            target_subdir: Sottodirectory opzionale dentro execution_dir
            file_type: Tipo di file
            description: Descrizione del file
            
        Returns:
            Nuovo percorso del file o None se errore
        """
        if not os.path.exists(source_path):
            print(f"File non trovato: {source_path}")
            return None
        
        # Crea sottodirectory se specificata
        target_dir = self.execution_dir
        if target_subdir:
            target_dir = os.path.join(self.execution_dir, target_subdir)
            os.makedirs(target_dir, exist_ok=True)
        
        # Determina il nome del file di destinazione
        filename = os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename)
        
        try:
            # Copia il file
            shutil.copy2(source_path, target_path)
            
            # Registra il file
            self.register_file(target_path, file_type, description)
            
            return target_path
            
        except Exception as e:
            print(f"Errore nella copia del file {source_path}: {e}")
            return None
    
    def generate_execution_summary(self) -> str:
        """
        Genera un file di riepilogo dell'esecuzione
        
        Returns:
            Percorso del file di riepilogo generato
        """
        summary_data = {
            'execution_info': {
                'execution_id': self.execution_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'directory': self.execution_dir,
                'total_files': len(self.generated_files)
            },
            'files_generated': self.generated_files
        }
        
        summary_path = os.path.join(self.execution_dir, "execution_summary.json")
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            self.register_file(summary_path, "json", "Riepilogo completo dell'esecuzione")
            return summary_path
            
        except Exception as e:
            print(f"Errore nella generazione del riepilogo: {e}")
            return None
    
    def print_execution_summary(self):
        """Stampa il riepilogo finale dell'esecuzione"""
        print("\n" + "=" * 60)
        print("RIEPILOGO ESECUZIONE TASK 3")
        print("=" * 60)
        print(f"ID Esecuzione: {self.execution_id}")
        print(f"Directory: {self.execution_dir}")
        print(f"File generati: {len(self.generated_files)}")
        print()
        
        # Raggruppa file per tipo
        files_by_type = {}
        for file_info in self.generated_files:
            file_type = file_info['type']
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_info)
        
        # Stampa file per categoria
        type_descriptions = {
            'json': 'Report di Analisi (JSON)',
            'csv': 'Riepiloghi Tabulari (CSV)',
            'png': 'Grafici e Visualizzazioni (PNG)',
            'unknown': 'Altri File'
        }
        
        for file_type, files in files_by_type.items():
            type_desc = type_descriptions.get(file_type, f"File {file_type.upper()}")
            print(f"{type_desc}:")
            
            for file_info in files:
                size_str = f"{file_info['size_mb']:.2f}MB" if file_info['size_mb'] > 0.01 else "<0.01MB"
                print(f"   • {file_info['description']}")
                print(f"     File: {file_info['filename']} ({size_str})")
            print()
        
        # Stampa percorso completo per riferimento
        print(f"Tutti i file sono disponibili in:")
        print(f"   results\\analysis\\{self.execution_id}")
        print("=" * 60)
    
    def get_files_by_type(self, file_type: str) -> List[Dict]:
        """
        Restituisce tutti i file di un tipo specifico
        
        Args:
            file_type: Tipo di file da cercare
            
        Returns:
            Lista di informazioni sui file del tipo richiesto
        """
        return [f for f in self.generated_files if f['type'] == file_type]
    
    def cleanup_empty_dirs(self):
        """Rimuove directory vuote nella struttura di analisi"""
        for root, dirs, files in os.walk(self.base_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory vuota
                        os.rmdir(dir_path)
                        print(f"Rimossa directory vuota: {dir_path}")
                except OSError:
                    pass  # Directory non vuota o altri errori
