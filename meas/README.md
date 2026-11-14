# Misure di laboratorio – cartella `meas`

Questo file descrive tutte le misure della cartella: cosa rappresenta ogni file, quando è stato registrato, con quale prova e con quali impostazioni. Le analisi sono nelle chat *GRAFICI MIM*, *GRAFICI STEP RESPONSE*, *GRAFICI ACCELEROMETRI* e *GRAFICI CURVE VELOCITÀ*; il riepilogo per giornata è nel documento *Log di laboratorio – chat GRAFICI*.

I nomi sono stati cambiati il 14/11/2026 con lo schema `<sistema>_<prova>_<parametri>_<data>_<ora>.csv`. Data e ora sono quelle dell'avvio dello script. Il nome originale di ogni file è indicato nelle tabelle (colonna *Nome originale*), così si ritrovano i riferimenti nelle chat.

---

## 1. Sistemi provati

| Sistema | Descrizione |
| --- | --- |
| **LS270** | Slitta lineare PI LS-270, asse **x** del banco, corsa provata 50–550 mm. Motore passo-passo 200 passi interi/giro, riduttore 5:1, vite a ricircolo di sfere passo 5 mm → 1 mm per giro motore, **5 µm per passo intero**. Morsetto Beckhoff **EL7047** in modalità velocità; anello di posizione chiuso nell'NC TwinCAT sull'encoder della slitta. |
| **LS180** | Slitta lineare PI LS-180, asse **y** del banco, corsa provata 50–250 mm. Stessa trasmissione e stesso morsetto dell'LS270. |
| **RS40** | Tavola rotante PI RS-40, versione con motore DC a spazzole. Riduttore 76:1 + vite senza fine 90:1 (6840:1). Drive **EL7342**, encoder 2048 cts/giro **sull'albero motore** letto da **EL5102** → risoluzione 0,026 m° (millesimi di grado). Specifiche PI: incremento minimo circa 5 m°, ripetibilità unidirezionale ±2,5 m°, bidirezionale circa 80 m°. |
| **Banco XY** | Le due slitte insieme, con accelerometro triassiale sulla board e accelerometro monoassiale z sul banco (NI cDAQ-9189, Mod1 ai0–ai2, Mod2 ai0). |

Comunicazione: PLC Beckhoff via pyads (AMS NetId 5.36.211.100.1.1, porta 851; porta 500 per l'NC).

## 2. Convenzioni

**Abbreviazioni nei nomi**

| Sigla | Significato |
| --- | --- |
| `scalette100nm` / `scalette300nm` | prova MIM: scaletta di gradini da 100 o 300 nm in salita e discesa |
| `11quote`, `9quote`, `quota150` … | numero di quote base lungo la corsa, o quota singola in mm |
| `attesa10s` | attesa di 10 s prima di ogni acquisizione |
| `errore-accumulato_100gradini300nm` | 100 gradini da 300 nm solo in avanti |
| `gradino1mm`, `gradino10mm`, `gradino5deg` | ampiezza del gradino della risposta al gradino |
| `v10`, `v4` | velocità comandata in mm/s |
| `11pos`, `3pos` | numero di posizioni di partenza |
| `rec2s`, `rec4s` | durata della registrazione per gradino |
| `Ka0.0075` … | precompensazione di accelerazione Ka in secondi |
| `P`, `Psolo` | regolatore di posizione P semplice |
| `PID-Tn0.1` | PID con tempo integrale 0,1 s |
| `zm1` | zona morta 1° |
| `senzaRiattivazione` | parametro cambiato con il solo Download, senza riattivare la configurazione TwinCAT |
| `cascata` | regolatore a cascata posizione + velocità (impostazione originale dell'RS40) |
| `dueP` | regolatore TwinCAT «Regolatore di posizione con due P costanti (con Ka)» |
| `Kv20-10` | Kv da fermo 20 / Kv in movimento 10 |
| `Vdyn0.7` | soglia di velocità per il passaggio tra i due Kv |
| `peso0.93` | peso della preregolazione (feedforward di velocità) |
| `Ifermo-Tn0.1` | integrale attivo solo da fermo, Tn 0,1 s |
| `zm0.003` | zona morta in gradi |
| `ciclo1ms`, `ciclo2ms` | tempo di ciclo del task NC SAF |
| `CONFIG-FINALE` | configurazione dell'RS40 impostata il 9/11 alle 17:08 (vedi §6) |
| `paramCasuali` | parametri del regolatore non documentati (provvisori) |

**Colonne dei file**

| Tipo di file | Colonne | Unità e note |
| --- | --- | --- |
| Scalette MIM | `target_x`/`target_y`, `direction` (up/down, assente nel file del 26/10 senza direzione), `actual_x`/`actual_y` | mm; 30 letture consecutive di `ActPos` per gradino (plateau) |
| Errore accumulato | `target_x`, `actual_x`, `following_error` (LS270) · `target_y`, `actual_y` (LS180) | mm; 30 letture per gradino |
| Risposta al gradino, slitte | `start_x`/`start_y`, `time`, `actual_x`/`actual_y`; dal 2/11 alle 10:01 anche `set_x`/`set_y` e `following_error` | mm, s dal comando; `following_error` = `PosDiff` = SetPos − ActPos; campioni ogni circa 6 ms |
| Temperature (`_temperature.csv`) | `time_s`, `clock`, `temp_motor`, `temp_ambient` | s dall'avvio, ora del giorno, **decimi di °C** (278 = 27,8 °C); 1 lettura al secondo |
| Risposta al gradino, RS40 | `start_pos`, `time`, `set_pos`, `actual_pos`, `following_error` | gradi, s dal comando; campioni ogni circa 9 ms |
| Registrazione RS40 | `time`, `set_pos`, `actual_pos`, `following_error` | s dall'avvio, gradi; campioni ogni circa 9 ms |
| Curva di velocità RS40 | `output_percent`, `actual_velo` | % di output del drive, velocità reale in °/s (`ActVelo`) |
| Accelerometri (`diag_…`) | `time`, `board_x`, `board_y`, `board_z`, `bench_z` | s, m/s²; 6 kHz |

**Script** (cartella superiore): `MIM_x_axis_LS270.py` e `MIM_y_axis_LS180.py` (scalette), `cumulative_error.py` (errore accumulato), `step_response_LS270.py` e `step_response_LS180.py` (gradino slitte, con temperature), `step_response_RS40.py` (gradino RS40), `record_RS40.py` (registrazione libera), `velocity_curve_RS40.py` (curva di velocità), `diagonal_accel_test.py` (accelerometri), `speed_test.py` (velocità di lettura ADS).

---

## 3. Velocità di lettura ADS – 27/10

| File | Nome originale | Cosa rappresenta |
| --- | --- | --- |
| `ADS_velocita-lettura_speed-test_2026-10-27.txt` | `speed test results.txt` | Test di 10 000 letture singole via pyads per misurare la frequenza di campionamento ottenibile da Python (27/10, circa 10:38) |

## 4. Slitte – errore di posizionamento su piccoli gradini (MIM)

**Prova a scalette**: a ogni quota base la slitta sale di 10 gradini e riscende; per ogni gradino si salvano 30 letture. Le quote LS270 sono 50–550 mm ogni 50 mm; le quote LS180 50–250 mm ogni 25 mm.

| File | Nome originale | Data | Cosa rappresenta |
| --- | --- | --- | --- |
| `LS270_scalette100nm_11quote_noDirezione_2026-10-26.csv` | `misure_LS270_2026-10-26.csv` (`misure0.csv` in chat) | 26/10 | Prima scaletta LS270, gradini 100 nm, 11 quote, 21 plateau per quota; senza colonna `direction` |
| `LS270_scalette100nm_11quote_2026-10-26_bis.csv` | `misure_LS270_2026-10-26_bis.csv` (`misure.csv`) | 26/10 | Ripetizione con colonna `direction`  |
| `LS270_scalette100nm_11quote_2026-10-27_10-45.csv` | `misure_LS270_2026-10-27_10-45.csv` | 27/10 10:45 | Stessa prova  |
| `LS270_scalette100nm_11quote_attesa10s_2026-10-27_11-29.csv` | `misure_LS270_2026-10-27_11-29.csv` | 27/10 11:29 | Script modificato: quota base non acquisita (19 plateau per quota) e attesa di 10 s prima di ogni acquisizione  |
| `LS270_scalette100nm_11quote_attesa10s_2026-10-27_13-39.csv` | `misure_LS270_2026-10-27_13-39.csv` | 27/10 13:39 | Come 11:29  |
| `LS270_scalette300nm_11quote_attesa10s_2026-10-27_15-07.csv` | `misure_LS270_2026-10-27_15-07.csv` | 27/10 15:07 | Come 11:29 ma gradini da 300 nm  |
| `LS180_scalette100nm_9quote_2026-10-29_12-48.csv` | `misure_LS180_2026-10-29_12-48.csv` | 29/10 12:48 | Prima scaletta LS180, gradini 100 nm, 9 quote  |
| `LS180_scalette300nm_9quote_2026-10-29_14-12.csv` | `misure_LS180_2026-10-29_14-12.csv` | 29/10 14:12 | Come sopra con gradini da 300 nm  |
| `LS270_scalette300nm_5quote_2026-11-02_12-08.csv` | `misure_LS270_2026-11-02_12-08.csv` | 2/11 12:08 | Scaletta 300 nm su 5 quote (100–500 mm), dopo le modifiche al regolatore della mattina  |
| `LS180_scalette300nm_3quote_2026-11-03_14-44.csv` | `misure_LS180_2026-11-03_14-44.csv` | 3/11 14:44 | Scaletta 300 nm a 100, 150, 200 mm  |

**Errore accumulato**: 100 gradini da 300 nm solo in avanti (30 µm totali), 30 letture per gradino, attesa 4 s.

| File | Nome originale | Data | Cosa rappresenta |
| --- | --- | --- | --- |
| `LS270_errore-accumulato_100gradini300nm_3quote_2026-11-03_09-29.csv` | `errore_accumulato_LS270_2026-11-03_09-29.csv` | 3/11 09:29 | LS270 a 100, 300 e 500 mm |
| `LS180_errore-accumulato_100gradini300nm_quota150_2026-11-03_15-11.csv` | `100_gradini_LS180_2026-11-03_15-11.csv` | 3/11 15:11 | LS180 a 150 mm |

## 5. Slitte – risposta al gradino e taratura del regolatore

Movimento a gradino da una posizione di partenza, registrando la posizione reale (e dal 2/11 anche setpoint ed errore di inseguimento) per 2 o 4 s dal comando. Asse fermo 5 s prima di ogni gradino; l'altra slitta a metà corsa.

### 29/10 – prime risposte al gradino, con temperature

Ogni prova ha il file `_temperature.csv` con lo stesso nome (temperatura del motore e ambiente, 1 Hz, per tutta la durata del test, dall'avvio dello script alla fine); il nome originale era `temperature_gradino_<asse>_<data>_<ora>.csv`. I file delle temperature sono:
`LS270_gradino1mm_v10_11pos_rec2s_2026-10-29_10-50_temperature.csv`, `LS270_gradino1mm_v10_11pos_rec2s_2026-10-29_10-55_temperature.csv`, `LS270_gradino10mm_v10_11pos_rec2s_2026-10-29_11-04_temperature.csv`, `LS270_gradino1mm_v10_3pos_rec4s_2026-10-29_11-15_temperature.csv`, `LS270_gradino10mm_v10_3pos_rec4s_2026-10-29_11-23_temperature.csv`, `LS180_gradino1mm_v10_3pos_rec4s_2026-10-29_12-00_temperature.csv`, `LS180_gradino10mm_v10_3pos_rec4s_2026-10-29_12-18_temperature.csv`, `LS270_gradino10mm_v10_3pos_rec4s_motoreFreddo_2026-10-29_12-25_temperature.csv`.

Regolatore originale (P, senza Ka). Le posizioni sono 50–550 mm ogni 50 mm (11pos) o 100/300/500 mm (LS270, 3pos) e 100/150/200 mm (LS180, 3pos).

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `LS270_gradino1mm_v10_11pos_rec2s_2026-10-29_10-50.csv` | `gradino_LS270_2026-10-29_10-50.csv` | 10:50 | Primo test completo, gradino 1 mm, 11 posizioni, 2 s |
| `LS270_gradino1mm_v10_11pos_rec2s_2026-10-29_10-55.csv` | `gradino_LS270_2026-10-29_10-55.csv` | 10:55 | Gradino 1 mm, 11 posizioni, 2 s |
| `LS270_gradino10mm_v10_11pos_rec2s_2026-10-29_11-04.csv` | `gradino_LS270_2026-10-29_11-04.csv` | 11:04 | Gradino 10 mm, 11 posizioni, 2 s |
| `LS270_gradino1mm_v10_3pos_rec4s_2026-10-29_11-15.csv` | `gradino_LS270_2026-10-29_11-15.csv` | 11:15 | Gradino 1 mm, 3 posizioni, 4 s |
| `LS270_gradino10mm_v10_3pos_rec4s_2026-10-29_11-23.csv` | `gradino_LS270_2026-10-29_11-23.csv` | 11:23 | Gradino 10 mm, 3 posizioni, 4 s |
| `LS180_gradino1mm_v10_3pos_rec4s_2026-10-29_12-00.csv` | `gradino_LS180_2026-10-29_12-00.csv` | 12:00 | LS180, gradino 1 mm, 3 posizioni, 4 s |
| `LS180_gradino10mm_v10_3pos_rec4s_2026-10-29_12-18.csv` | `gradino_LS180_2026-10-29_12-18.csv` | 12:18 | LS180, gradino 10 mm, 3 posizioni, 4 s |
| `LS270_gradino10mm_v10_3pos_rec4s_motoreFreddo_2026-10-29_12-25.csv` | `gradino_LS270_2026-10-29_12-25.csv` | 12:25 | LS270, gradino 10 mm dopo la pausa, motore raffreddato |

### 2/11 – taratura Ka sull'LS270 (3 posizioni 100/300/500 mm, 4 s)

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `LS270_gradino10mm_v4_Ka0_2026-11-02_09-18.csv` | `step_response_LS270_2026-11-02_09-18.csv` | 09:18 | Gradino 10 mm a 4 mm/s, regolatore originale |
| `LS270_gradino1mm_v4_Ka0_2026-11-02_09-24.csv` | `step_response_LS270_2026-11-02_09-24.csv` | 09:24 | Gradino 1 mm a 4 mm/s |
| `LS270_gradino10mm_v10_Ka0_PosDiff_2026-11-02_10-01.csv` | `step_response_LS270_2026-11-02_10-01.csv` | 10:01 | Primo test con `set_x` e `following_error`; riferimento senza Ka |
| `LS270_gradino10mm_v10_KvRidotto_2026-11-02_10-12.csv` | `step_response_LS270_2026-11-02_10-12.csv` | 10:12 | Kv di posizione ridotto |
| `LS270_gradino10mm_v10_Ka0.002_senzaRiattivazione_2026-11-02_10-42.csv` | `step_response_LS270_2026-11-02_10-42.csv` | 10:42 | Regolatore «due P con Ka», Ka 0,002, **senza riattivare la configurazione** |
| `LS270_gradino10mm_v10_Ka0.002_2026-11-02_10-59.csv` | `step_response_LS270_2026-11-02_10-59.csv` | 10:59 | Ka 0,002 dopo la riattivazione |
| `LS270_gradino10mm_v10_Ka0.004_2026-11-02_11-04.csv` | `step_response_LS270_2026-11-02_11-04.csv` | 11:04 | Ka 0,004 |
| `LS270_gradino10mm_v10_Ka0.006_2026-11-02_11-11.csv` | `step_response_LS270_2026-11-02_11-11.csv` | 11:11 | Ka 0,006 |
| `LS270_gradino10mm_v10_Ka0.0075_2026-11-02_11-14.csv` | `step_response_LS270_2026-11-02_11-14.csv` | 11:14 | Ka 0,0075 |
| `LS270_gradino10mm_v10_Ka0.0075_ripetizione_2026-11-02_14-06.csv` | `step_response_LS270_2026-11-02_14-06.csv` | 14:06 | Ripetizione con Ka 0,0075 |
| `LS270_gradino10mm_v10_KvMoto1_KvFermo5_Ka0_2026-11-02_16-01.csv` | `step_response_LS270_2026-11-02_16-01.csv` | 16:01 | Prova alternativa: Kv in movimento 1, da fermo 5, Ka 0 |

### 3/11 – verifica sull'LS180

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `LS180_gradino10mm_v10_Ka0.0075_2026-11-03_14-36.csv` | `step_response_LS180_2026-11-03_14-36.csv` | 14:36 | LS180, gradino 10 mm, regolatore «due P con Ka», Ka 0,0075; posizioni 100/150/200 mm |

**Configurazione delle slitte usata dal 2/11 alle 11:14**: regolatore «due P costanti con Ka», Kv da fermo = Kv in movimento (valore originale), Ka 0,0075 s, velocità 10 mm/s, jerk 500 mm/s³.

## 6. RS40 – taratura del regolatore (9/11)

Gradini relativi di **5° a 5°/s**, uno dopo l'altro (la posizione di partenza avanza di 5° a ogni gradino). Requisito: posizione finale letta dall'encoder entro **±1 m°**. I passi per file vanno da 1 a 30; la durata di registrazione per gradino da 3 a 10 s.

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `RS40_gradino5deg_3passi_cascata_Ka0_2026-11-09_11-31.csv` | `step_response_rotational_2026-11-09_11-31.csv` | 11:31 | Regolatore a cascata originale (Kv pos 10, Kv vel 2,7, Tn vel 0,046 s), Ka 0 |
| `RS40_gradino5deg_3passi_cascata_Ka0.003_2026-11-09_11-48.csv` | `…_11-48.csv` | 11:48 | Cascata, Ka 0,003 |
| `RS40_gradino5deg_3passi_cascata_Ka0.010_2026-11-09_11-51.csv` | `…_11-51.csv` | 11:51 | Cascata, Ka 0,010 |
| `RS40_gradino5deg_3passi_PID-Tn0.1_zm1_2026-11-09_11-58.csv` | `…_11-58.csv` | 11:58 | PID Kv 10, Tn 0,1 s con integrale sempre attivo, zona morta 1° |
| `RS40_gradino5deg_3passi_Psolo_Kv10_2026-11-09_12-14.csv` | `…_12-14.csv` | 12:14 | Solo P, Kv 10 |
| `RS40_gradino5deg_3passi_P_Ka0.006_2026-11-09_12-17.csv` | `…_12-17.csv` | 12:17 | P + Ka 0,006 |
| `RS40_gradino5deg_3passi_P_Ka0.012_2026-11-09_12-18.csv` | `…_12-18.csv` | 12:18 | P + Ka 0,012 |
| `RS40_gradino5deg_3passi_P_Ka0.018_2026-11-09_12-20.csv` | `…_12-20.csv` | 12:20 | P + Ka 0,018 |
| `RS40_gradino5deg_3passi_P_Ka0.018_ripetizione_2026-11-09_12-22.csv` | `…_12-22.csv` | 12:22 | Ripetizione |
| `RS40_gradino5deg_3passi_P_Ka0.018_Ifermo-Tn1_2026-11-09_12-26.csv` | `…_12-26.csv` | 12:26 | + integrale solo da fermo, Tn 1 s |
| `RS40_gradino5deg_3passi_P_Ka0.018_Ifermo-Tn0.1_2026-11-09_12-29.csv` | `…_12-29.csv` | 12:29 | Tn 0,1 s, registrazione 6 s |
| `RS40_gradino5deg_3passi_P_Ka0.018_Ifermo-Tn0.1_ripetizione_2026-11-09_12-32.csv` | `…_12-32.csv` | 12:32 | Ripetizione |
| `RS40_gradino5deg_10passi_P_Ka0.018_Ifermo-Tn0.1_zm0.003_2026-11-09_12-35.csv` | `…_12-35.csv` | 12:35 | P + Ka 0,018, integrale solo da fermo con Tn 0,1 s, zona morta 0,003°, 10 passi, 10 s |
| `RS40_gradino5deg_10passi_PID-Tn0.1_zm1_2026-11-09_12-48.csv` | `…_12-48.csv` | 12:48 | PID Kv 10, Tn 0,1 s con integrale sempre attivo, zona morta 1° (stesse impostazioni delle 11:58), 10 passi |
| `RS40_gradino5deg_1passo_cascata_Ka0_2026-11-09_15-19.csv` | `…_15-19.csv` | 15:19 | Ritorno alla cascata originale, 1 passo, 10 s |
| `RS40_gradino5deg_1passo_cascata_KvVel4_2026-11-09_15-21.csv` | `…_15-21.csv` | 15:21 | Cascata con Kv di velocità 4,0 |
| `RS40_gradino5deg_1passo_cascata_Ka0.03_2026-11-09_15-26.csv` | `…_15-26.csv` | 15:26 | Cascata con Ka 0,03 |
| `RS40_gradino5deg_1passo_cascata_Ka0.03_TnVel0.08_2026-11-09_15-29.csv` | `…_15-29.csv` | 15:29 | Cascata, Ka 0,03, Tn velocità 0,08 s |
| `RS40_gradino5deg_1passo_dueP-Ka_primaProva_2026-11-09_15-38.csv` | `…_15-38.csv` | 15:38 | Primo test con il regolatore «due P con Ka» (parametri non annotati) |
| `RS40_gradino5deg_1passo_dueP_Kv10-10_Ka0.018_peso1_2026-11-09_15-42.csv` | `…_15-42.csv` | 15:42 | Due P, Kv 10/10, Ka 0,018, peso 1,0 |
| `RS40_gradino5deg_1passo_dueP_Kv20-10_Ka0.025_peso0.93_2026-11-09_15-52.csv` | `…_15-52.csv` | 15:52 | Kv 20/10, Ka 0,025, peso 0,93 |
| `RS40_gradino5deg_1passo_dueP_Kv20-10_Ka0.035_peso0.93_2026-11-09_15-55.csv` | `…_15-55.csv` | 15:55 | Ka 0,035 |
| `RS40_gradino5deg_1passo_dueP_Kv20-10_Ka0.030_peso0.93_2026-11-09_15-57.csv` | `…_15-57.csv` | 15:57 | Ka 0,030 |
| `RS40_gradino5deg_10passi_dueP_Kv20-10_Ka0.030_ciclo2ms_2026-11-09_16-01.csv` | `…_16-01.csv` | 16:01 | 10 passi, ciclo NC 2 ms |
| `RS40_gradino5deg_5passi_dueP_Kv30-10_Ka0.030_ciclo2ms_2026-11-09_16-10.csv` | `…_16-10.csv` | 16:10 | Kv da fermo 30 |
| `RS40_gradino5deg_5passi_dueP_Kv22-10_Ka0.030_ciclo2ms_2026-11-09_16-13.csv` | `…_16-13.csv` | 16:13 | Kv da fermo 22 |
| `RS40_gradino5deg_5passi_dueP_Kv22-10_Ka0.030_ciclo1ms_2026-11-09_16-26.csv` | `…_16-26.csv` | 16:26 | **Cicli NC e PLC portati da 2 ms a 1 ms**, stessi parametri |
| `RS40_gradino5deg_5passi_dueP_Kv22-10_Ka0.020_ciclo1ms_2026-11-09_16-29.csv` | `…_16-29.csv` | 16:29 | Ka 0,020 |
| `RS40_gradino5deg_5passi_dueP_Kv22-10_Ka0.025_ciclo1ms_2026-11-09_16-31.csv` | `…_16-31.csv` | 16:31 | Ka 0,025 |
| `RS40_gradino5deg_5passi_dueP_Kv35-10_Ka0.025_ciclo1ms_2026-11-09_16-35.csv` | `…_16-35.csv` | 16:35 | Kv da fermo 35 |
| `RS40_gradino5deg_5passi_dueP_Kv45-10_Ka0.025_ciclo1ms_2026-11-09_16-37.csv` | `…_16-37.csv` | 16:37 | Kv da fermo 45 |
| `RS40_gradino5deg_5passi_dueP_Kv48-10_Ka0.025_ciclo1ms_2026-11-09_16-40.csv` | `…_16-40.csv` | 16:40 | Kv da fermo 48 |
| `RS40_gradino5deg_30passi_dueP_Kv48-10_Ka0.025_ciclo1ms_2026-11-09_16-43.csv` | `…_16-43.csv` | 16:43 | 30 passi, Kv da fermo 48 |
| `RS40_gradino5deg_30passi_dueP_Kv50-10_Ka0.025_ciclo1ms_2026-11-09_16-51.csv` | `…_16-51.csv` | 16:51 | 30 passi, Kv da fermo 50 |
| `RS40_gradino5deg_5passi_dueP_Kv50-10_Vdyn0.7_Ka0.025_2026-11-09_16-56.csv` | `…_16-56.csv` | 16:56 | Soglia V dyn da 0,5 a 0,7 |
| `RS40_gradino5deg_5passi_dueP_Kv50-15_Vdyn0.7_Ka0.025_2026-11-09_16-59.csv` | `…_16-59.csv` | 16:59 | Kv in movimento 15 |
| `RS40_gradino5deg_5passi_dueP_Kv50-20_Vdyn0.7_Ka0.025_2026-11-09_17-00.csv` | `…_17-00.csv` | 17:00 | Kv in movimento 20 |
| `RS40_gradino5deg_5passi_dueP_Kv47-20_Vdyn0.7_Ka0.025_2026-11-09_17-04.csv` | `…_17-04.csv` | 17:04 | Kv da fermo 47 |
| `RS40_gradino5deg_30passi_dueP_Kv47-20_Vdyn0.7_Ka0.025_CONFIG-FINALE_2026-11-09_17-08.csv` | `…_17-08.csv` | 17:08 | 30 passi con la configurazione finale (Kv da fermo 47, Kv in movimento 20, V dyn 0,7, Ka 0,025) |
| `RS40_gradino5deg_30passi_CONFIG-FINALE_zm0.0005_2026-11-09_17-18.csv` | `…_17-18.csv` | 17:18 | Configurazione finale con zona morta 0,0005° |
| `RS40_gradino5deg_30passi_CONFIG-FINALE_Vdyn0.9_peso0.92_2026-11-09_17-24.csv` | `…_17-24.csv` | 17:24 | V dyn 0,9 e peso 0,92 |

Nella colonna *Nome originale* `…` sta per `step_response_rotational_2026-11-09`.

**Configurazione finale dell'RS40 (CONFIG-FINALE)**: ciclo NC SAF e PlcTask 1 ms; regolatore «due P costanti con Ka»; Kv da fermo 47; Kv in movimento 20; soglia V dyn 0,7; Ka 0,025 s; peso preregolazione 0,93; zona morta 0,001°.

## 7. RS40 – registrazioni libere e curva di velocità (12/11)

Le registrazioni sono fatte con `record_RS40.py`, che legge SetPos, ActPos e PosDiff per N secondi senza comandare movimenti; i movimenti sono stati dati a parte. «Lenti» = passi di circa 0,17° a 1°/s; «veloci» = passi di circa 0,85° a 5°/s.

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `RS40_registrazione_3lenti-3veloci_paramCasuali_2026-11-12_10-02.csv` | `recorded_movement_RS40_2026-11-12_10-02.csv` | 10:02 | 20 s, 3 passi lenti + 3 veloci, parametri provvisori |
| `RS40_registrazione_7lenti-3veloci_paramCasuali_2026-11-12_10-09.csv` | `recorded_movement_RS40_2026-11-12_10-09.csv` | 10:09 | 20 s, 7 lenti + 3 veloci, parametri provvisori |
| `RS40_registrazione_1passo5.6deg_paramCasuali_2026-11-12_10-11.csv` | `recorded_movement_RS40_2026-11-12_10-11.csv` | 10:11 | 10 s, un passo da 5,57° a 5°/s, parametri provvisori |
| `RS40_registrazione_4lenti-3veloci_CONFIG-FINALE_2026-11-12_10-25.csv` | `recorded_movement_RS40_2026-11-12_10-25.csv` | 10:25 | 20 s, configurazione finale; l'ultimo passo è tagliato dalla fine della registrazione |
| `RS40_registrazione_4lenti-4veloci_CONFIG-FINALE_2026-11-12_10-28.csv` | `recorded_movement_RS40_2026-11-12_10-28.csv` | 10:28 | 25 s, configurazione finale |

La curva di velocità è misurata in **anello aperto** con `velocity_curve_RS40.py`: l'output del drive è impostato direttamente in % via ADS sulla porta 500 dell'NC e si legge la velocità reale.

| File | Nome originale | Ora | Cosa rappresenta |
| --- | --- | --- | --- |
| `RS40_curva-velocita_anelloAperto_output1-100pct_2026-11-12_12-28.csv` | `velocity_curve_RS40_2026-11-12_12-28.csv` | 12:28 | Output dall'1 % al 100 % a passi dell'1 % |
| `RS40_curva-velocita_anelloAperto_output1-15pct_passo0.2_2026-11-12_12-42.csv` | `velocity_curve_RS40_2026-11-12_12-42.csv` | 12:42 | Zona bassa dall'1 % al 14,8 % a passi dello 0,2 % |

## 8. Banco XY – vibrazioni durante il movimento diagonale (3/11)

**File**: `diag_v<velocità>_x<partenza x>_y<partenza y>_2026-11-03_16-32.csv`, 52 file.

Le due slitte si muovono insieme in diagonale per 5 s, con acquisizione di 2 s prima, 5 s di movimento e 2 s dopo (9 s in totale, 6 kHz). Velocità: 4,0–10,0 mm/s a passi di 0,5 mm/s (13 valori). Partenze: (x, y) = (100, 50), (200, 100), (300, 150), (400, 200) mm. Avvio della serie alle 16:32 del 3/11 (tutti i file hanno nel nome l'ora di avvio). Script `diagonal_accel_test.py`. Analisi dell'8–9/11 con `analisi_vibrazioni.py` e `fft_bande.py` (cartella `claudio/`).
