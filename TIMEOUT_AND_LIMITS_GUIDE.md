# Gestione Timeout e Limiti di Dimensione

## Panoramica

Il sistema MHS Calculator ora include funzionalità robuste per gestire timeout e limiti di dimensione file, prevenendo situazioni di blocco durante l'elaborazione di file grandi o complessi.

## Funzionalità Implementate

### 1. Timeout di Calcolo
- **Default**: 300 secondi (5 minuti) per file
- **Comportamento**: Se il calcolo supera il timeout, viene interrotto in modo pulito
- **Output**: Vengono salvati i risultati parziali con annotazioni nel file .mhs

### 2. Limite Dimensione File
- **Default**: 50 MB massimo per file
- **Comportamento**: File superiori al limite vengono saltati automaticamente
- **Output**: Viene creato un file .mhs con informazioni sul motivo del salto

### 3. Controlli di Complessità
- **Matrice grande**: Avviso automatico per matrici con alta complessità (righe × colonne > 10000)
- **Controlli periodici**: Durante il calcolo vengono effettuati controlli timeout ogni 100 ipotesi

## Parametri Configurabili

### Da Riga di Comando

```bash
# Timeout personalizzato (600 secondi = 10 minuti)
python mhs_calculator.py input.matrix --timeout 600

# Limite dimensione personalizzato (100 MB)
python mhs_calculator.py input.matrix --max-size 100

# Combinati
python mhs_calculator.py input.matrix --timeout 900 --max-size 200
```

### Script Main.py

```bash
# Esperimento completo con timeout e limiti personalizzati
python main.py --all --timeout 600 --max-size 100 --max-files 20

# Singoli compiti con limiti
python main.py --compito1 file.matrix --timeout 300 --max-size 50
python main.py --compito2 benchmarks1/ --timeout 180 --max-files 5
```

## Codici di Uscita

Il sistema restituisce codici di uscita specifici per diversi scenari:

- **0**: Successo completo
- **1**: Errore generico
- **2**: Timeout raggiunto (risultati parziali disponibili)
- **3**: File troppo grande (elaborazione saltata)

## Gestione degli Output

### File .mhs con Timeout

Quando si verifica un timeout, il file .mhs contiene:

```
;;; WARNING: Computation interrupted by timeout (300s)
;;; Results are INCOMPLETE - only partial solutions found
;;; Computation time: 300.000 seconds
;;; Hypotheses generated: 15420
;;; Max level reached: 4
```

### File .mhs con Limite Dimensione

Per file troppo grandi:

```
;;; WARNING: File too large (>50MB) - computation skipped
;;; No results due to interruption
```

## Raccomandazioni d'Uso

### Timeout Consigliati per Tipo di File

- **File piccoli** (< 1 MB): 60-180 secondi
- **File medi** (1-10 MB): 300-600 secondi  
- **File grandi** (10-50 MB): 600-1800 secondi

### Limiti Dimensione Consigliati

- **Sistema normale**: 50 MB
- **Sistema potente**: 100-200 MB
- **Server/cluster**: 500+ MB

## Monitoraggio Durante l'Esecuzione

Il sistema fornisce feedback in tempo reale:

```
📁 Caricamento file (15.23MB): 74181.042.matrix
⚠️  Matrice grande (45×512, complessità: 23040)
   Timeout impostato: 300s
🔍 Inizio calcolo MHS...
📊 Livello 1: 512 ipotesi
📊 Livello 2: 2341 ipotesi
⏰ Operazione interrotta per timeout (300s)
⚠️  Calcolo interrotto - risultati parziali disponibili
```

## Sperimentazione sui Benchmark

Per la sperimentazione sui benchmark, il sistema ora include:

- **Statistiche dettagliate** su timeout e interruzioni
- **Riassunto finale** con conteggi di successi/timeout/file troppo grandi
- **Controllo automatico** del numero massimo di file da elaborare

### Esempio Output Sperimentazione

```
📊 RIASSUNTO SPERIMENTAZIONE
================================================================================
File                 Matrice    Ridotta    MHS    Tempo(s) Ipotesi  Status    
--------------------------------------------------------------------------------
74181.001.matrix     12×45      12×32      3      0.045    234       OK        
74181.002.matrix     15×67      15×54      0      300.000  15420     TIMEOUT   
74181.003.matrix     8×23       8×18       2      0.012    89        OK        
large_file.matrix    -          -          -      -        -         TOO_BIG   

📈 STATISTICHE TOTALI:
   Successi: 2/4
   Timeout: 1
   File troppo grandi: 1
   Errori: 0
   Tempo totale: 300.1s
```

## Risoluzione Problemi

### Timeout Frequenti
- Aumentare il valore `--timeout`
- Ridurre `--max-files` per elaborazioni batch
- Verificare la complessità delle matrici

### File Troppo Grandi
- Aumentare `--max-size` se si ha RAM sufficiente
- Utilizzare sistemi più potenti per file molto grandi
- Considerare tecniche di riduzione della matrice

### Prestazioni Lente
- Monitorare l'uso di memoria durante l'esecuzione
- Verificare che non ci siano altri processi che consumano risorse
- Considerare timeout più bassi per prime esplorazioni

## Sicurezza e Stabilità

Il sistema implementa:

- **Gestione robuста delle eccezioni**: Ogni operazione è protetta da try/catch
- **Cleanup automatico**: Timer e risorse vengono sempre rilasciati
- **Thread safety**: Il sistema di timeout usa thread separati in modo sicuro
- **Interruzione pulita**: Il calcolo può essere interrotto senza corrompere dati

Questo garantisce che il sistema non vada mai in hang e che produca sempre output utilizzabili, anche in caso di interruzione.
