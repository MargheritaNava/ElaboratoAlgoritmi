#!/usr/bin/env python3
"""
Performance Monitor for MHS Analysis
===================================

Modulo per il monitoraggio delle prestazioni hardware in tempo reale
durante l'esecuzione dell'algoritmo di calcolo dei Minimal Hitting Set.
"""

import os
import time
import psutil
import threading
import json
from typing import Dict

class PerformanceMonitor:
    """
    Classe per il monitoraggio delle prestazioni durante l'esecuzione dell'algoritmo MHS
    """
    
    def __init__(self, sample_interval: float = 0.5):
        """
        Inizializza il monitor delle prestazioni
        
        Args:
            sample_interval: Intervallo di campionamento in secondi
        """
        self.sample_interval = sample_interval
        self.monitoring = False
        self.monitor_thread = None
        
        # Statistiche raccolte
        self.start_time = 0
        self.end_time = 0
        self.cpu_samples = []
        self.memory_samples = []
        self.time_samples = []
        
        # Processo corrente
        self.process = psutil.Process()
        
        # Statistiche finali
        self.stats = {
            'execution_time': 0,
            'peak_memory_mb': 0,
            'avg_cpu_percent': 0,
            'max_cpu_percent': 0,
            'memory_growth_mb': 0,
            'initial_memory_mb': 0,
            'final_memory_mb': 0
        }
    
    def start_monitoring(self):
        """
        Inizia il monitoraggio delle prestazioni
        """
        self.monitoring = True
        self.start_time = time.time()
        self.cpu_samples = []
        self.memory_samples = []
        self.time_samples = []
        
        # Reset delle statistiche CPU
        self.process.cpu_percent()  # Prima chiamata per inizializzare

        # Avvia thread di monitoraggio
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"Monitoraggio prestazioni avviato (campionamento ogni {self.sample_interval}s)")
    
    def stop_monitoring(self):
        """
        Ferma il monitoraggio e calcola le statistiche finali
        """
        self.monitoring = False
        self.end_time = time.time()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        self._calculate_final_stats()
        print(f"Monitoraggio completato ({self.stats['execution_time']:.2f}s)")
    
    def _monitor_loop(self):
        """
        Loop principale di monitoraggio (eseguito in thread separato)
        """
        while self.monitoring:
            try:
                current_time = time.time() - self.start_time
                cpu_percent = self.process.cpu_percent()
                memory_mb = self.process.memory_info().rss / (1024 * 1024)
                
                self.time_samples.append(current_time)
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_mb)
                
                time.sleep(self.sample_interval)
            except KeyboardInterrupt:
                raise    
            except Exception as e:
                print(f"Errore nel monitoraggio: {e}")
                break
    
    def _calculate_final_stats(self):
        """
        Calcola le statistiche finali
        """
        self.stats['execution_time'] = self.end_time - self.start_time
        
        if self.memory_samples:
            self.stats['peak_memory_mb'] = max(self.memory_samples)
            self.stats['initial_memory_mb'] = self.memory_samples[0]
            self.stats['final_memory_mb'] = self.memory_samples[-1]
            self.stats['memory_growth_mb'] = self.stats['final_memory_mb'] - self.stats['initial_memory_mb']
        
        if self.cpu_samples:
            self.stats['avg_cpu_percent'] = sum(self.cpu_samples) / len(self.cpu_samples)
            self.stats['max_cpu_percent'] = max(self.cpu_samples)
    
    def get_stats(self) -> Dict:
        """
        Restituisce le statistiche delle prestazioni
        
        Returns:
            Dizionario con le statistiche
        """
        return self.stats.copy()
    
    def print_performance_summary(self):
        """
        Stampa un riassunto delle prestazioni
        """
        print("\nRIASSUNTO PRESTAZIONI")
        print("=" * 50)
        print(f"Tempo di esecuzione:     {self.stats['execution_time']:.3f} secondi")
        print(f"Picco memoria:           {self.stats['peak_memory_mb']:.1f} MB")
        print(f"Crescita memoria:        {self.stats['memory_growth_mb']:.1f} MB")
        print(f"CPU media:               {self.stats['avg_cpu_percent']:.1f}%")
        print(f"CPU massima:             {self.stats['max_cpu_percent']:.1f}%")
        print(f"Campioni raccolti:       {len(self.cpu_samples)}")
    
    def save_detailed_report(self, filename: str):
        """
        Salva un report dettagliato delle prestazioni
        
        Args:
            filename: Nome del file di output
        """
        report = {
            'summary': self.stats,
            'samples': {
                'time': self.time_samples,
                'cpu_percent': self.cpu_samples,
                'memory_mb': self.memory_samples
            },
            'metadata': {
                'sample_interval': self.sample_interval,
                'total_samples': len(self.cpu_samples),
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'total_memory_gb': psutil.virtual_memory().total / (1024**3)
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report dettagliato salvato in: {filename}")
