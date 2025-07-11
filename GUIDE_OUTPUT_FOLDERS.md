# Guida Rapida: Salvare i File .mhs nella Cartella Output

## ✅ Modifiche Implementate

Tutti i file `.mhs` generati vengono ora automaticamente salvati in una cartella `output` all'interno della directory dei benchmark.

## 📁 Struttura Directory

### Prima (problema):
```
benchmarks1/
├── 74181.000.matrix
├── 74181.001.matrix
├── 74181.000.mhs        # ← File output mescolati con input
└── 74181.001.mhs        # ← File output mescolati con input
```

### Dopo (soluzione):
```
benchmarks1/
├── 74181.000.matrix
├── 74181.001.matrix
└── output/              # ← Cartella output separata
    ├── 74181.000.mhs    # ← File output organizzati
    └── 74181.001.mhs    # ← File output organizzati
```

## 🔧 File Modificati

1. **MHSCalculator.py** - Aggiunto supporto per cartella output
2. **mhs_calculator.py** - Aggiunta logica per directory benchmark
3. **main.py** - Aggiornati tutti i compiti per usare la struttura output

## 🚀 Comandi Aggiornati

### Calcolo Singolo File
```bash
# Il file viene automaticamente salvato in benchmarks1/output/
python mhs_calculator.py benchmarks1/74181.000.matrix
```

### Calcolo Multiplo (MHSCalculator.py)
```bash
# Tutti i file vengono salvati in benchmarks1/output/
python MHSCalculator.py benchmarks1
```

### Calcolo con Script Principale
```bash
# Usa automaticamente la struttura output corretta
python main.py --compito1 benchmarks1/74181.000.matrix
```

## ✅ Vantaggi

- **Organizzazione automatica**: Nessun intervento manuale richiesto
- **Separazione netta**: File input e output in cartelle separate
- **Facilità di gestione**: Facile backup e condivisione dei risultati
- **Compatibilità Git**: Cartelle output possono essere ignorate nel version control
- **Scalabilità**: Funziona con qualsiasi numero di file benchmark

## 📋 Verifiche

Per verificare che tutto funzioni correttamente:

```bash
# 1. Esegui un calcolo di test
python main.py --test

# 2. Verifica che i file siano nella cartella corretta
ls -la benchmarks1/output/

# 3. Controlla il contenuto di un file MHS
head benchmarks1/output/74181.001.mhs
```

## 🎯 Risultato

Ora tutti i file `.mhs` vengono automaticamente organizzati nella struttura corretta senza dover specificare percorsi di output manuali!

## ✅ IMPLEMENTAZIONE COMPLETATA

Tutte le modifiche per timeout e limiti sono state implementate con successo:

### 🚀 Funzionalità Aggiunte

1. **Timeout Management**:
   - Classe `TimeoutHandler` per gestione thread-safe dei timeout
   - Controlli periodici durante il calcolo MHS
   - Interruzione pulita con salvataggio risultati parziali
   - Timeout configurabile da riga di comando (default: 300s)

2. **File Size Limits**:
   - Controllo dimensioni pre-caricamento
   - Limite configurabile (default: 50MB)
   - Skip automatico file troppo grandi
   - Informazioni dettagliate nei file output

3. **Enhanced Output**:
   - Annotazioni complete nei file .mhs
   - Status di interruzione (timeout/size limit)
   - Statistiche avanzate con informazioni su interruzioni
   - Codici di uscita specifici per diversi scenari

4. **Batch Processing Robusto**:
   - Limite numero file elaborabili per batch
   - Statistiche aggregate con conteggi interruzioni
   - Continuazione elaborazione anche dopo timeout singoli

### 🔧 Script Aggiornati

- **`mhs_calculator.py`**: Core algorithm con timeout e limiti
- **`main.py`**: Tutti i compiti con parametri configurabili
- **`README.md`**: Documentazione aggiornata
- **`TIMEOUT_AND_LIMITS_GUIDE.md`**: Guida dettagliata nuove funzionalità

### ✅ Test Verificati

- ✅ Timeout su file complessi
- ✅ Limite dimensione file
- ✅ Sperimentazione batch con limiti
- ✅ Output parziali con annotazioni
- ✅ Compatibilità con workflow esistenti

Il sistema è ora robusto e pronto per gestire file di qualsiasi dimensione e complessità senza rischio di hang o problemi di memoria.
