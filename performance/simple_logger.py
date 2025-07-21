#!/usr/bin/env python3
"""
Simple Logger for MHS Execution Tracking
========================================

Logger semplice che crea un file di log per ogni esecuzione con timestamp univoco.
"""

import os
import datetime
import time
from typing import Optional

class SimpleLogger:
    """Logger semplice per tracciare le esecuzioni"""
    
    def __init__(self, task_name: str = "mhs_execution"):
        """
        Inizializza il logger
        
        Args:
            task_name: Nome del task per identificare il tipo di esecuzione
        """
        self.task_name = task_name
        self.start_time = time.time()
        self.log_file = self._create_log_file()
        
        # Scrivi header del log
        self._write_header()
    
    def _create_log_file(self) -> str:
        """Crea il file di log con nome univoco"""
        # Crea directory logs se non esistente
        logs_dir = os.path.join("results", "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Genera nome file univoco
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{self.task_name}_{timestamp}.log"
        log_path = os.path.join(logs_dir, log_filename)
        
        return log_path
    
    def _write_header(self):
        """Scrive l'header del file di log"""
        start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""
{'='*60}
MHS EXECUTION LOG
{'='*60}
Task: {self.task_name}
Start Time: {start_time_str}
Log File: {os.path.basename(self.log_file)}
{'='*60}

"""
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log(self, message: str, level: str = "INFO"):
        """
        Scrive un messaggio nel log
        
        Args:
            message: Messaggio da scrivere
            level: Livello del log (INFO, WARNING, ERROR, etc.)
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        elapsed = time.time() - self.start_time
        
        log_entry = f"[{timestamp}] [{level:>7}] (+{elapsed:6.2f}s) {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Errore scrittura log: {e}")
    
    def info(self, message: str):
        """Scrive un messaggio di informazione"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Scrive un messaggio di warning"""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Scrive un messaggio di errore"""
        self.log(message, "ERROR")
    
    def success(self, message: str):
        """Scrive un messaggio di successo"""
        self.log(message, "SUCCESS")
    
    def section(self, title: str):
        """Scrive una sezione nel log"""
        separator = "-" * 40
        self.log(f"\n{separator}")
        self.log(f"{title}")
        self.log(f"{separator}")
    
    def finalize(self, success: bool = True):
        """Finalizza il log con statistiche finali"""
        total_time = time.time() - self.start_time
        end_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        footer = f"""
{'='*60}
EXECUTION COMPLETED
{'='*60}
End Time: {end_time_str}
Total Duration: {total_time:.2f} seconds
Status: {"SUCCESS" if success else "FAILED"}
{'='*60}
"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(footer)
        
        return self.log_file
    
    def get_log_path(self) -> str:
        """Restituisce il percorso del file di log"""
        return self.log_file


# Funzioni di utilità per creare logger facilmente
def create_task_logger(task_name: str) -> SimpleLogger:
    """
    Crea un logger per un task specifico
    
    Args:
        task_name: Nome del task (es: "compito_1", "compito_2", "compito_3")
    
    Returns:
        Istanza di SimpleLogger configurata
    """
    return SimpleLogger(task_name)

def create_complete_execution_logger() -> SimpleLogger:
    """
    Crea un logger per l'esecuzione completa di tutti i compiti
    
    Returns:
        Istanza di SimpleLogger configurata per l'esecuzione completa
    """
    return SimpleLogger("esecuzione_completa")
