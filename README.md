Nel file requirements.txt sono presenti le librerie necessarie per utilizzare l'interfaccia Streamlit \n
Il file main.py imposta la navigazione tra pagine dell'interfaccia \n
Il file login.py imposta il login dell'interfaccia \n
Nella cartella pages sono presenti i file .py corrispondenti ognuno ad una pagina dell'interfaccia. I file utils.py, utilsm.py e test_statistici.py sono moduli di funzioni che vengono importati all'interno delle pagine \n
La cartella dataset contiene i file del dataset che sono stati utilizzati: alcuni sono stati processati rispetto a quelli presenti nel dataset originale su Synapse. Qui si trovano anche i file ottenuti dal signal processing di solette e tappeto sensorizzato per i task di balance \n
Gli script dataset_analysis.py, preprocessing_taskds.py e clean_walkwaydata.py sono il codice che è stato utilizzato per processare i dati grezzi dei sensori e pulire alcuni dei file .csv del dataset \n

