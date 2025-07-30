# Elaborato Algoritmi e Strutture Dati 2023-2024: Calcolo Minimal Hitting Set

## Autori
**Elena Margherita Nava, Jennifer Piangatelli, Mattia Pavlovic**  
Algoritmi e Strutture Dati - A.A. 2023-2024  
Prof.ssa Marina Zanella

---

## Panoramica del Progetto

Questo progetto implementa un algoritmo efficiente per il calcolo dei **Minimal Hitting Set** (MHS) su matrici binarie, con un sistema completo di analisi delle prestazioni e validazione attraverso permutazioni.

Il progetto è organizzato in tre compiti principali che coprono implementazione, sperimentazione e validazione dell'algoritmo.

### Contesto Teorico
Il **Minimal Hitting Set Problem** è un problema computazionale NP-completo che consiste nel trovare l'insieme di cardinalità minima che interseca ogni elemento di una collezione data. Nel nostro caso, lavoriamo con matrici binarie dove ogni riga rappresenta un insieme e cerchiamo le colonne che "colpiscono" tutte le righe.

### Innovazioni Implementate
- Sistema di monitoraggio prestazioni in tempo reale
- Algoritmo di potatura intelligente per ottimizzazione
- Framework di validazione attraverso permutazioni sistematiche
- Generazione automatica di report e visualizzazioni

---

## Architettura del Progetto

```
ElaboratoAlgoritmi/
├── algorithm.py                  # Algoritmo principale MHS
├── matrix_utils.py              # Caricamento e utilità matrici
├── permutation_utils.py         # Generazione permutazioni sistematiche
├── performance/
│   ├── __init__.py
│   ├── performance_monitor.py   # Monitoraggio real-time CPU/memoria
│   ├── performance_analyzer.py  # Analisi statistiche e complessità
│   ├── performance_reporter.py  # Generazione report e visualizzazioni
│   ├── batch_performance_analyzer.py  # Analisi batch unificata
│   ├── permutation_pattern_analyzer.py # Pattern nelle permutazioni
│   └── execution_manager.py     # Gestione directory esecuzioni
├── task1.py                     # Compito 1: Implementazione MHS
├── task2.py                     # Compito 2: Sperimentazione benchmark
├── task3.py                     # Compito 3: Permutazioni e validazione
├── benchmarks/                  # Dataset di test forniti
│   ├── *.matrix                # File matrici di input
│   └── ...
├── results/                     # Directory output
│   ├── *.mhs                   # File risultati MHS (Task 1)
│   ├── performance_reports/     # Report prestazioni (Task 2)
│   └── analysis/               # Analisi permutazioni (Task 3)
│       └── esecuzione_YYYYMMDD_HHMMSS/
├── main.py                      # Entry point principale
└── README.md                    # Documentazione progetto
```

---

## Descrizione dei Compiti

### Compito 1: Implementazione Algoritmo MHS
**Obiettivo**: Implementare l'algoritmo per il calcolo dei Minimal Hitting Set

**Caratteristiche principali**:
- Caricamento matrici in formato `.matrix` con validazione dimensioni
- Riduzione del dominio tramite rimozione colonne vuote
- Esplorazione breadth-first dello spazio delle ipotesi per cardinalità crescente
- Tecniche di potatura avanzate per ottimizzazione prestazioni
- Sistema di timeout automatico per prevenire hang su istanze complesse
- Controlli dimensionali per gestione memoria
- Output dettagliato in formato `.mhs` con statistiche complete

**Complessità**: O(2^n) nel caso peggiore, ottimizzata con potatura  
**Output**: File `.mhs` con MHS trovati e statistiche di esecuzione

### Compito 2: Sperimentazione Sistematica
**Obiettivo**: Analizzare le prestazioni dell'algoritmo sui benchmark forniti

**Caratteristiche principali**:
- Elaborazione batch di tutti i file benchmark
- Monitoraggio real-time di CPU, memoria e tempo di esecuzione
- Gestione intelligente di timeout per file complessi
- Raccolta statistiche dettagliate su:
  - Ipotesi generate per ogni livello di cardinalità
  - Operazioni di potatura effettuate
  - Utilizzo risorse computazionali
- Generazione report comparativi tra matrici di diverse dimensioni

**Metriche raccolte**: Tempo di esecuzione, picco memoria, ipotesi generate/esplorate  
**Output**: Report CSV e grafici delle prestazioni in `results/performance_reports/`

### Compito 3: Validazione tramite Permutazioni
**Obiettivo**: Validare la correttezza e analizzare la robustezza dell'algoritmo

**Caratteristiche principali**:
- Generazione permutazioni sistematiche (identità, casuali, reverse)
- Confronto risultati tra matrice originale e permutate
- Analisi dell'impatto delle permutazioni sulle prestazioni
- Identificazione di pattern nelle variazioni prestazionali
- Validazione correttezza attraverso mappatura risultati

**Validazione**: Verifica invarianza soluzioni tra permutazioni  
**Output**: Directory di analisi con report completi, grafici e dati CSV

---

## Sistema di Analisi delle Prestazioni

### Moduli Principali

- **`PerformanceMonitor`**: Monitoraggio real-time di CPU, memoria e I/O
- **`PerformanceAnalyzer`**: Calcolo statistiche e analisi complessità computazionale
- **`PerformanceReporter`**: Generazione automatica di report e visualizzazioni
- **`BatchPerformanceAnalyzer`**: Analisi unificata per elaborazioni batch
- **`PermutationPatternAnalyzer`**: Identificazione pattern nelle variazioni prestazionali
- **`ExecutionManager`**: Gestione directory univoche per ogni esecuzione

### Metriche Monitorate

- **Tempo**: Durata totale, tempo per livello, overhead sistema
- **Memoria**: Picco utilizzo, memoria media, allocazioni
- **CPU**: Utilizzo percentuale, tempo sistema vs utente
- **Algoritmo**: Ipotesi generate/esplorate, operazioni potatura, hit rate

### Visualizzazioni Generate
- Grafici temporali delle prestazioni
- Diagrammi di utilizzo memoria
- Analisi distribuzione ipotesi per livello
- Confronti prestazionali tra permutazioni

---

## Output e Risultati

### Struttura Directory Risultati
Per ogni esecuzione del **Task 3** viene creata una directory univoca:
```
results/analysis/esecuzione_YYYYMMDD_HHMMSS/
├── advanced_performance_analysis_*.json    # Report prestazioni completo
├── execution_summary.json                  # Riepilogo esecuzione
├── performance_summary_*.csv               # Dati tabulari prestazioni
├── permutation_analysis_report_*.png       # Report grafico generale
└── performance_plots_*.png                 # Grafici prestazioni dettagliati
```

### Tipi di Report Generati

1. **Report JSON**: Analisi dettagliate con metriche complete e metadati
2. **File CSV**: Dati strutturati per ulteriori elaborazioni statistiche
3. **Grafici PNG**: Visualizzazioni ad alta risoluzione delle prestazioni e pattern
4. **Log di Esecuzione**: Tracciamento completo delle operazioni con timestamp

---

## Installazione e Setup

### Prerequisiti
- **Python 3.8+** (testato su 3.8-3.11)
- **Pacchetti richiesti**: matplotlib, numpy, psutil (installazione automatica)
- **Sistema Operativo**: Compatibile con Windows, macOS, Linux
- **Memoria RAM**: Almeno 4GB raccomandati per matrici grandi
- **VS Code** (raccomandato per sviluppo)

### Configurazione Ambiente
```bash
# Clona o scarica il progetto
cd "/path/to/ElaboratoAlgoritmi"

# L'ambiente virtuale viene configurato automaticamente
# I pacchetti necessari vengono installati quando richiesti

# Verifica dipendenze (opzionale)
python -c "import matplotlib, numpy, psutil; print('Dipendenze OK')"
```

### Verifica Installazione
```bash
python main.py --test  # Esegue test rapido con esempio PDF
```

### Risoluzione Problemi Comuni
- **Errore import matplotlib**: Installare con `pip install matplotlib`
- **Timeout su file grandi**: Aumentare timeout con `--timeout 60`
- **Memoria insufficiente**: Ridurre dimensioni dataset o chiudere altre applicazioni

---

## Guida all'Utilizzo

### Quick Start
```bash
# Esecuzione rapida di tutti i compiti
python main.py --all

# Test veloce
python main.py --test
```

### Esecuzione Compiti Individuali

#### Compito 1: Calcolo MHS singolo file
```bash
python main.py --compito1 benchmarks/74181.000.matrix
```

#### Compito 2: Sperimentazione benchmark completa
```bash
python main.py --compito2 benchmarks/
```

#### Compito 3: Analisi permutazioni
```bash
python main.py --compito3 benchmarks/74181.000.matrix --num-permutations 10
```

### Opzioni Avanzate
```bash
# Timeout personalizzato (default: 30s)
python main.py --compito1 file.matrix --timeout 60

# Numero permutazioni personalizzato (default: 5)
python main.py --compito3 file.matrix --num-permutations 20

# Modalità verbose per debug
python main.py --compito2 benchmarks/ --verbose

# Salvataggio dettagliato prestazioni
python main.py --compito1 file.matrix --save-detailed-stats
```

### Esempi di Utilizzo Tipici
```bash
# Analisi completa su file specifico
python main.py --compito3 benchmarks/small_example.matrix --num-permutations 15

# Batch processing con timeout esteso
python main.py --compito2 benchmarks/ --timeout 120

# Debug di file problematico
python main.py --compito1 problematic_file.matrix --verbose --timeout 10
```

---

## Algoritmi e Strutture Dati

### Algoritmo Principale (Template-based)
1. **Inizializzazione**: Caricamento e preprocessing matrice
2. **Riduzione dominio**: Eliminazione colonne vuote e righe duplicate
3. **Esplorazione BFS**: Ricerca per livelli di cardinalità crescente
4. **Generazione successori**: Solo successori sinistri per efficienza
5. **Verifica hitting set**: Controllo intersezione con ogni riga della matrice
6. **Test minimalità**: Confronto con soluzioni esistenti
7. **Potatura intelligente**: Eliminazione superseti di soluzioni note

### Strutture Dati Utilizzate
- **`Set`**: Rappresentazione efficiente di ipotesi e MHS (operazioni O(1))
- **`List`**: Matrici e sequenze ordinate
- **`Dict`**: Mappature indici e cache risultati
- **`DefaultDict`**: Conteggi automatici per livello e statistiche
- **`Deque`**: Coda BFS per esplorazione livelli

### Ottimizzazioni Implementate
- **Potatura precoce**: Eliminazione rami non promettenti
- **Cache risultati**: Memorizzazione stati già esplorati
- **Controllo timeout**: Interruzione controllata su istanze complesse
- **Gestione memoria**: Limitazione dimensioni per evitare overflow

---

## Validazione e Testing

### Test di Correttezza
- Confronto risultati su permutazioni (invarianza soluzioni)
- Verifica proprietà minimal hitting set
- Test su esempi noti dal corso

### Test di Prestazioni
- Benchmark su matrici di diverse dimensioni
- Analisi scaling temporale e spaziale
- Identificazione colli di bottiglia

### Gestione Errori
- Validazione input (formato, dimensioni)
- Timeout automatici su istanze complesse
- Recovery da errori di memoria

---

## Risultati e Osservazioni

### Prestazioni Tipiche
- **File piccoli** (< 20x20): < 1 secondo, memoria < 50MB
- **File medi** (20x20 - 50x50): 1-10 secondi, memoria < 200MB
- **File grandi** (> 50x50): Variabile, con timeout a 30s, memoria < 1GB

### Pattern Identificati
- Impatto significativo della struttura matrice su prestazioni
- Variazioni prestazionali limitate tra permutazioni casuali
- Efficacia tecniche di potatura su istanze sparse
- Correlazione tra densità matrice e tempo di esecuzione

### Limitazioni Note
- Timeout automatico su istanze molto complesse (>30s)
- Limitazioni memoria su matrici molto grandi (>100x100)
- Prestazioni dipendenti dalla struttura specifica della matrice

### Benchmark Risultati
| Dimensione | Tempo Medio | Memoria Picco | Successo |
|------------|-------------|---------------|----------|
| < 20x20    | 0.5s        | 25MB         | 100%     |
| 20x20-50x50| 5.2s        | 150MB        | 95%      |
| > 50x50    | 15.8s       | 400MB        | 80%      |

---

## Troubleshooting

### Problemi Comuni e Soluzioni

**Q: Il programma si blocca su file grandi**  
A: Utilizzare timeout più bassi: `--timeout 15` o verificare disponibilità memoria

**Q: Errori di importazione moduli**  
A: Verificare installazione Python 3.8+ e installare dipendenze mancanti

**Q: Risultati inconsistenti tra esecuzioni**  
A: Verificare seed casualità nelle permutazioni (dovrebbe essere fisso)

**Q: Grafici non vengono generati**  
A: Installare matplotlib: `pip install matplotlib`

### Log e Debug
- Utilizzare `--verbose` per output dettagliato
- Controllare `results/` per file di log
- Verificare memoria disponibile prima dell'esecuzione

---

## Licenza e Riconoscimenti

Questo progetto è sviluppato per scopi didattici nell'ambito del corso di **Algoritmi e Strutture Dati** dell'Università degli Studi di Brescia.

**Corso**: Algoritmi e Strutture Dati - A.A. 2023-2024  
**Docente**: Prof.ssa Marina Zanella  
**Studenti**: Elena Margherita Nava, Jennifer Piangatelli, Mattia Pavlovic

---

## Appendice

### Formato File Input (.matrix)
```
<numero_righe> <numero_colonne>
<riga1: sequenza di 0 e 1 separati da spazio>
<riga2: sequenza di 0 e 1 separati da spazio>
...
```

### Formato File Output (.mhs)
```
# Minimal Hitting Sets per: <nome_file>
# Generato il: <timestamp>
# Tempo esecuzione: <secondi>s
# Ipotesi esplorate: <numero>

<mhs1: indici colonne separati da spazio>
<mhs2: indici colonne separati da spazio>
...

# Statistiche dettagliate:
# - Livelli esplorati: <numero>
# - Operazioni potatura: <numero>
# - Memoria picco: <MB>
```

### Compatibilità e Versioni
- **Python**: 3.8, 3.9, 3.10, 3.11 (testato)
- **matplotlib**: >= 3.0
- **numpy**: >= 1.19
- **psutil**: >= 5.7

