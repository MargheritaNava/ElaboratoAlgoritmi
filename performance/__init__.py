"""
Performance Analysis Package for MHS
====================================

Modulo modulare per il monitoraggio, analisi e report delle prestazioni
degli algoritmi Minimal Hitting Set.

Componenti:
- PerformanceMonitor: Monitoraggio real-time CPU e memoria
- PerformanceAnalyzer: Analisi statistiche e complessità computazionale
- PerformanceReporter: Generazione report e grafici
- BatchPerformanceAnalyzer: Analisi unificata per batch di file
- PermutationPatternAnalyzer: Identificazione pattern nelle variazioni prestazionali
"""

from .performance_monitor import PerformanceMonitor
from .performance_analyzer import PerformanceAnalyzer
from .performance_reporter import PerformanceReporter
from .batch_analyzer import BatchPerformanceAnalyzer
from .pattern_analyzer import PermutationPatternAnalyzer
from .execution_manager import ExecutionManager
from .simple_logger import SimpleLogger, create_task_logger

__all__ = ['PerformanceMonitor', 'PerformanceAnalyzer', 'PerformanceReporter', 'BatchPerformanceAnalyzer', 'PermutationPatternAnalyzer', 'ExecutionManager', 'SimpleLogger', 'create_task_logger']
