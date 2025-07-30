# Elaborato 2023-2024: Calcolo Minimal Hitting Set

## Autore
**Mattia Pavlovic**  
Algoritmi e Strutture Dati - A.A. 2023-2024  
Prof.ssa Marina Zanella

## Descrizione del Progetto

Questo progetto implementa un algoritmo completo per il calcolo dei **Minimal Hitting Set (MHS)** con funzionalità avanzate di gestione timeout e limiti dimensionali. Il progetto è suddiviso in tre compiti principali:

### Compito 1: Algoritmo MHS
Implementazione dell'algoritmo per il calcolo dei Minimal Hitting Set seguendo il template fornito nelle specifiche. L'algoritmo:
- Carica matrici in formato `.matrix` con controllo dimensioni
- Riduce il dominio rimuovendo colonne vuote
- Esplora lo spazio delle ipotesi per cardinalità crescente
- Applica tecniche di potatura per ottimizzare le prestazioni
- **Gestisce timeout automatici** per prevenire hang su file complessi
- **Controlla limiti dimensionali** per evitare problemi di memoria
- Produce output in formato `.mhs` con informazioni dettagliate

### Compito 2: Sperimentazione
Sperimentazione sistematica sui file di benchmark forniti con:
- Analisi delle prestazioni temporali e spaziali
- **Gestione robusta di timeout** durante elaborazioni batch
- **Statistiche su interruzioni** e file saltati per dimensioni eccessive
- Statistiche dettagliate su ipotesi generate per livello
- Confronto delle prestazioni su matrici di diverse dimensioni
- **Selezione intelligente basata su entropia** per campionamento rappresentativo

#### Selezione Intelligente delle Matrici (Nuovo)
Il Compito 2 ora include un **sistema avanzato di selezione delle matrici** basato sull'entropia di Shannon:

**Caratteristiche principali:**
- **Analisi automatica dell'entropia** di tutte le matrici nella directory di benchmark
- **Selezione diversificata** di 30 matrici rappresentative del range completo di complessità
- **Distribuzione uniforme** lungo lo spettro di entropia per garantire copertura ottimale
- **Report dettagliati** con statistiche complete su ogni matrice analizzata

**Vantaggi tecnici:**
- **Efficienza computazionale**: Concentra il calcolo su matrici rappresentative invece di elaborare sequenzialmente tutti i file
- **Copertura scientifica completa**: Garantisce test su matrici con diversi livelli di "casualità" strutturale
- **Tempo di esecuzione ottimizzato**: Da potenziali ore a 20-60 minuti per dataset completi
- **Risultati più significativi**: Focus su casi di studio diversificati invece di pattern ripetitivi

**Implementazione dell'entropia:**
- Utilizza l'**entropia di Shannon** (H = -Σ p_i * log₂(p_i)) per quantificare la "casualità" di ogni matrice
- Range tipico: 0.0 (matrice perfettamente ordinata) → 1.0 (distribuzione casuale perfetta)
- **Implementazione nativa** senza dipendenze esterne per massima compatibilità

**Output generato:**
- **File JSON** (`results/entropy_analysis.json`) con analisi completa
- **File CSV** (`results/entropy_analysis.csv`) per analisi in Excel/Python
- **Report console** con tabella riassuntiva delle matrici selezionate
- **Integrazione trasparente** con il flusso esistente del Compito 2

### Compito 3: Permutazioni e Validazione
Generazione di permutazioni delle matrici e confronto dei risultati per:
- Validare la correttezza dell'algoritmo
- **Confronti con timeout** per evitare blocchi su permutazioni complesse
- Analizzare l'impatto delle permutazioni sulle prestazioni
- Identificare pattern nelle variazioni prestazionali

## Nuove Funzionalità (v2.0)

### Gestione Timeout
- **Timeout configurabile** per prevenire hang (default: 5 minuti)
- **Interruzione pulita** con salvataggio risultati parziali
- **Monitoraggio in tempo reale** del progresso

### Limiti Dimensionali
- **Controllo automatico** dimensioni file (default: 50MB)
- **Skip intelligente** di file troppo grandi
- **Feedback dettagliato** sui motivi di interruzione

### Output Organizzato
- **Cartelle output dedicate** (`benchmarks1/output/`)

### Sistema di Analisi Prestazioni Unificato (v2.1)
- **Modulo `performance/`** con analisi modulare e riutilizzabile
- **`BatchPerformanceAnalyzer`** per analisi critica unificata
- **Report JSON/CSV** con metriche dettagliate
- **Grafici di complessità** generati automaticamente
- **Analisi teorica** con stima della complessità computazionale
- **Monitoraggio sistema** (CPU, memoria) in tempo reale
- **Separazione pulita** tra input e output
- **Annotazioni complete** nei file .mhs su timeout e interruzioni

## Sistema di Analisi delle Prestazioni

Il progetto include un **sistema modulare di analisi delle prestazioni** nella cartella `performance/`:

### Moduli Principali
- **`PerformanceMonitor`**: Monitoraggio real-time di CPU e memoria
- **`PerformanceAnalyzer`**: Analisi statistiche e complessità computazionale
- **`PerformanceReporter`**: Generazione report e grafici
- **`BatchPerformanceAnalyzer`**: Analisi unificata per batch di file
- **`PermutationPatternAnalyzer`**: Identificazione pattern nelle variazioni prestazionali
- **`ExecutionManager`**: Gestore directory univoche per ogni esecuzione

### Output Generati
Per ogni esecuzione del **Task 3** viene creata una directory univoca `results/analysis/esecuzione_YYYYMMDD_HHMMSS/` contenente:

- **Report di Analisi (JSON)**
  - `advanced_performance_analysis_*.json` - Report completo prestazioni
  - `execution_summary.json` - Riepilogo dell'esecuzione
- **Riepiloghi Tabulari (CSV)**
  - `performance_summary_*.csv` - Dati prestazioni in formato tabellare
- **Grafici e Visualizzazioni (PNG)**
  - `permutation_analysis_report_*.png` - Report grafico generale
  - `performance_plots_*.png` - Grafici prestazioni dettagliati

### Log di Esecuzione
Ogni esecuzione genera un **file di log dettagliato** in `results/logs/` con nome univoco:
- `compito_1_YYYYMMDD_HHMMSS.log` - Log esecuzione Task 1
- `compito_2_YYYYMMDD_HHMMSS.log` - Log esecuzione Task 2  
- `compito_3_YYYYMMDD_HHMMSS.log` - Log esecuzione Task 3

I log contengono timestamp, statistiche di sistema, messaggi di progresso e informazioni di debug.

### Funzionalità Avanzate
- **Analisi critica** delle prestazioni con identificazione di bottleneck
- **Stima complessità teorica** basata su modelli matematici
- **Confronto empirico vs teorico** con grafici comparativi
- **Identificazione outlier** e file problematici
- **Raccomandazioni automatiche** per ottimizzazioni

## Struttura del Progetto

```
Elaborato2023/
├── main.py                 # Script principale
├── mhs_calculator.py       # Implementazione algoritmo MHS
├── matrix_permutator.py    # Generatore di permutazioni
├── mhs_comparator.py       # Comparatore di risultati
├── entropy_selector.py     # Selettore intelligente matrici basato su entropia
├── compito2_entropy_integration.py # Integrazione entropy selector nel Compito 2
├── test_mhs.py            # Script di test
├── requirements.txt        # Dipendenze Python
├── README.md              # Questa documentazione
├── performance/           # Moduli analisi prestazioni
│   ├── __init__.py        # Esportazione moduli
│   ├── batch_analyzer.py  # Analizzatore batch unificato
│   ├── execution_manager.py # Gestore directory univoche
│   ├── pattern_analyzer.py # Analisi pattern prestazionali
│   ├── performance_analyzer.py # Analisi complessità e statistiche
│   ├── performance_monitor.py  # Monitoraggio CPU/memoria
│   └── performance_reporter.py # Report e grafici
├── benchmarks1/           # File di benchmark (formato .matrix)
├── benchmarks2/           # File di benchmark aggiuntivi
├── permutations_*/        # Directory permutazioni (generate automaticamente)
└── results/               # Directory risultati (generata automaticamente)
    ├── analysis/          # Analisi e report dettagliati
    │   └── esecuzione_*   # Directory univoca per ogni esecuzione Task 3
    ├── logs/              # File di log per ogni esecuzione
    ├── entropy_analysis.json # Report completo analisi entropia
    └── entropy_analysis.csv  # Dati entropia in formato tabellare
```

## Installazione e Configurazione

### Prerequisiti
- Python 3.8 o superiore
- VS Code (raccomandato)

### Setup Ambiente
```bash
# Naviga nella directory del progetto
cd "/path/to/Elaborato2023"

# L'ambiente virtuale verrà configurato automaticamente
# I pacchetti necessari verranno installati quando richiesti
```

## Utilizzo

### Esecuzione Completa
Per eseguire tutti e tre i compiti automaticamente:
```bash
python main.py --all
```

### Compiti Individuali

#### Compito 1: Calcolo MHS per un singolo file
```bash
python main.py --compito1 benchmarks1/74181.000.matrix
```

#### Compito 2: Sperimentazione sui benchmark
```bash
# Sperimentazione standard (tutti i file)
python main.py --compito2 benchmarks1/

# Sperimentazione con selezione entropia (15 matrici - DEFAULT)
python main.py --compito2 benchmarks1/ --max-files 15

# Sperimentazione con selezione entropia (30 matrici)
python main.py --compito2 benchmarks1/ --max-files 30

# Solo analisi entropia senza calcolo MHS (15 matrici - DEFAULT)
python entropy_selector.py

# Solo analisi entropia con numero personalizzato
python entropy_selector.py --num-matrices 30

# Solo analisi entropia con directory e numero personalizzati
python entropy_selector.py benchmarks/ --num-matrices 25

# Forma abbreviata del parametro
python entropy_selector.py benchmarks/ -n 20
```

#### Compito 3: Permutazioni e confronti
```bash
python main.py --compito3 benchmarks1/74181.000.matrix --num-permutations 10
```

### Test Rapido
Per un test veloce con l'esempio del PDF:
```bash
python main.py --test
```

### Script Individuali

#### Calcolo MHS Diretto
```bash
# Con il mio algoritmo avanzato
python mhs_calculator.py benchmarks1/74181.000.matrix
# Output automatico in: benchmarks1/output/74181.000.mhs

# Con l'algoritmo originale MHSCalculator.py (elabora tutti i file della cartella)
python MHSCalculator.py benchmarks1
# Output automatico in: benchmarks1/output/
```

#### Generazione Permutazioni
```bash
python matrix_permutator.py benchmarks1/74181.000.matrix -o permutations/ -n 5
```

#### Confronto Risultati
```bash
python mhs_comparator.py "permutations/*.matrix"
```

## Struttura di Output

### Organizzazione File
Tutti i file `.mhs` generati vengono automaticamente salvati in una cartella `output` all'interno della directory dei benchmark:

```
benchmarks1/
├── 74181.000.matrix
├── 74181.001.matrix
├── ...
└── output/               # ← Cartella creata automaticamente
    ├── 74181.000.mhs
    ├── 74181.001.mhs
    └── ...

benchmarks2/
├── file1.matrix
├── file2.matrix
├── ...
└── output/               # ← Cartella creata automaticamente
    ├── file1.mhs
    ├── file2.mhs
    └── ...
```

## Formati di File

### File .matrix (Input)
```
;;; Header con metadati
;;; Map elemento1 elemento2 ...
0 1 0 1 0 -
1 0 1 0 1 -
0 0 1 1 1 -
```

### File .mhs (Output)
```
;;; Minimal Hitting Set Results
;;; Statistiche e metadati
1 0 0 1 0
0 1 1 0 0
```

## Caratteristiche Implementate

### Ottimizzazioni
- **Riduzione del dominio**: Rimozione automatica di colonne vuote
- **Potatura dello spazio**: Evita esplorazione di superseti di soluzioni note
- **Limite di cardinalità**: Esplorazione limitata a max{|N|, |M'|}
- **Generazione efficiente**: Solo successori sinistri per evitare duplicati

### Selezione Intelligente delle Matrici (Nuovo)
- **Analisi entropia automatica**: Calcolo entropia di Shannon per tutte le matrici
- **Selezione diversificata**: Distribuzione uniforme lungo il range di complessità
- **Ottimizzazione dei tempi**: Da ore a 20-60 minuti per dataset completi
- **Report scientifici**: Output JSON/CSV con statistiche dettagliate
- **Implementazione nativa**: Nessuna dipendenza esterna aggiuntiva

### Statistiche e Monitoraggio
- Tempo di calcolo dettagliato
- Conteggio ipotesi generate per livello
- Analisi occupazione memoria
- Metriche di confronto tra permutazioni

### Validazione e Test
- Test automatici con esempi noti
- Confronto risultati tra permutazioni
- Verifica consistenza algoritmo
- Analisi impatto ordinamento su prestazioni

## Risultati Sperimentali

### Prestazioni Tipiche
- **File piccoli** (< 10 righe): < 1 secondo
- **File medi** (10-50 righe): 1-30 secondi  
- **File grandi** (> 50 righe): Variabile, dipende dalla struttura

### Impatto Permutazioni
- I MHS rimangono identici tra tutte le permutazioni 
- Le prestazioni possono variare fino a 2-5x tra diverse permutazioni
- L'ordinamento delle colonne ha impatto maggiore delle righe

## Limitazioni e Note

### Limitazioni Attuali
- **Memoria**: Crescita esponenziale per matrici molto grandi
- **Tempo**: Problema NP-completo, alcuni casi richiedono molto tempo
- **Scalabilità**: Efficace fino a ~100 colonne con struttura favorevole

### Miglioramenti Futuri
- Implementazione algoritmi approssimati per casi grandi
- Parallelizzazione calcolo per livelli
- Ottimizzazioni specifiche per strutture sparse
- Cache intelligente per sottoproblemi ricorrenti

## Testing

### Test Automatici
```bash
python test_mhs.py
```

### Verifica Correttezza
1. Test con esempio del PDF (risultato noto)
2. Confronto permutazioni (devono essere identiche)
3. Verifica proprietà MHS (hitting + minimalità)

## Strutture Dati Utilizzate

- **Set**: Per rappresentare ipotesi e MHS (operazioni insiemistiche efficienti)
- **List**: Per matrici e sequenze ordinate
- **Dict**: Per mappature e statistiche
- **DefaultDict**: Per conteggi automatici per livello

## Algoritmi Implementati

### Algoritmo Principale (Template-based)
1. **Inizializzazione**: Carica e riduce matrice
2. **Esplorazione per livelli**: Breadth-first search
3. **Generazione successori**: Solo successori sinistri
4. **Verifica hitting set**: Controllo intersezione con ogni riga
5. **Test minimalità**: Confronto con soluzioni esistenti
6. **Potatura**: Elimina superseti di soluzioni note

### Algoritmo Permutazioni
1. **Permutazioni sistematiche**: Identità, casuali, reverse
2. **Generazione controllata**: Seed fisso per riproducibilità
3. **Mappatura indici**: Conversione tra formati originale/permutato

## Contatti e Supporto

Per domande o problemi relativi a questa implementazione:
- **Autore**: Mattia Pavlovic
- **Corso**: Algoritmi e Strutture Dati 2023-2024
- **Docente**: Prof.ssa Marina Zanella

## Licenza

Questo progetto è sviluppato per scopi didattici nell'ambito del corso di Algoritmi e Strutture Dati.