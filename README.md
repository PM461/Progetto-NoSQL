# E-commerce di Libri con Database NoSQL

![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Riak KV](https://img.shields.io/badge/Riak_KV-8B0000.svg?style=for-the-badge&logo=riak&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

Progetto realizzato per il corso di **Modelli e Architetture Avanzati di Basi di Dati** (A.A. 2023/2024), Università degli Studi di Torino - Corso di Laurea Magistrale in Informatica.

**Autori:** Pasquale Manfredi, Alberto Alpe.

Per un'analisi dettagliata delle scelte progettuali, implementative e dei test, si rimanda al documento completo presente nel repository: **Relazione Manfredi-Alpe.pdf**.

## 📖 Descrizione del Progetto

Questo progetto propone l'infrastruttura backend per un e-commerce specializzato nella vendita globale di libri. Il sistema è progettato per gestire un ampio inventario e un elevato numero di transazioni, garantendo alta disponibilità, scalabilità orizzontale e flessibilità. 

L'architettura dati si basa su una persistenza poliglotta che sfrutta due sistemi NoSQL:
*   **MongoDB:** Gestione dell'inventario dei libri, dei profili utente e dello storico degli acquisti.
*   **Riak:** Gestione delle sessioni utente e di un sistema di raccomandazione di libri basato sugli acquisti precedenti (sfruttando l'Inverted Index).

## 🏗 Architettura e Scelte Tecnologiche

I database non sono considerati come magazzini fisici, ma come server distribuiti geograficamente. L'infrastruttura è stata pensata e simulata tramite **Docker** creando cluster separati per tre nazioni: Italia, Francia e Germania.

### MongoDB (Replica Set)
*   **Struttura:** 3 cluster geografici (es. `ReplicaSetItalia`), ciascuno composto da 3 nodi (es. `Libreria1`, `Libreria2`, `Libreria3`).
*   **Consistenza:** Configurato con diverse priorità sui nodi per l'elezione del Primary. `WriteConcern = 2` (scrittura su almeno 2 nodi su 3) e `ReadConcern = "linearizable"` per garantire l'ordine consistente delle operazioni.

### Riak KV
*   **Struttura:** 3 cluster geografici composti da 3 nodi ciascuno.
*   **Utilizzo:** Organizzato in bucket per regioni. Implementa un Inverted Index che mappa le parole chiave ai libri, permettendo al sistema di suggerire nuove letture in base allo storico dell'utente. I dati di sessione (es. preferenze di lingua e tema) sono gestiti qui.
*   **Consistenza:** Quorum di lettura/scrittura impostato a 2 su 3. Configurato con `dvv_enabled` (dot-version vectors) per un'efficiente gestione dei conflitti.

## ⚙️ Funzionalità Implementate

1.  **Gestione Inventario:** Inserimento e ricerca di libri (con dati reali ottenuti tramite Open Library API).
2.  **Gestione Utenti e Ordini:** Simulazione e registrazione degli acquisti.
3.  **Sistema di Raccomandazione:** Suggerimento di 5 libri basato sulle parole chiave estratte dagli acquisti precedenti dell'utente.
4.  **Gestione Sessioni:** Salvataggio delle preferenze utente (es. lingua) sul nodo geografico più vicino.

## 🐍 Script Python (Componenti del Progetto)

Il progetto include vari script Python per il popolamento e la visualizzazione dei dati, divisi nelle seguenti categorie:

### Script di Popolamento Dati
*   `populate_libri_mongodb.py`: Interroga Open Library API tramite ISBN per estrarre dettagli reali dei libri, generando valori fittizi per prezzo e disponibilità, e li salva in MongoDB.
*   `populate_users_mongodb.py`: Genera utenti fittizi realistici (tramite la libreria *Faker*) e li inserisce nel DB.
*   `populate_order_mongodb.py`: Genera ordini casuali associando utenti e libri esistenti nel DB.
*   `generate_inverted_index.py`: Recupera gli abstract dei libri, li tokenizza (rimuovendo stop-words e applicando stemming) e crea/aggiorna l'Inverted Index su Riak.
*   `populate_sessions_riak.py`: Simula le sessioni di login degli utenti (con TTL) salvandole nel bucket Riak.

### Script di Visualizzazione (Test)
*   `Book_suggested.py`: Il cuore del motore di raccomandazione. Incrocia gli acquisti dell'utente su MongoDB con l'Inverted Index su Riak per suggerire 5 titoli pertinenti.
*   `Book_view.py` / `Orders_view.py` / `User_view.py`: Script di utilità per recuperare in modo randomico e formattare in JSON un singolo libro, ordine o utente da MongoDB.
*   `Session_view.py`: Recupera e formatta una sessione attiva da Riak.
*   `Load_book_data.py`: Cerca un libro combinando i dati in tempo reale dell'API Open Library e quelli salvati in MongoDB.

## 🚀 Setup e Installazione

1.  Assicurarsi di avere **Docker** e **Python 3.x** installati.
2.  Installare le dipendenze Python necessarie: `pip install pymongo requests faker`.
3.  Creare le reti e istanziare i container Docker per MongoDB e Riak. Tutti i comandi CLI (reti, container, inizializzazione replica set) sono disponibili nel file **`Comandi-Mongo-Riak.txt`**.
4.  Una volta avviati i cluster e configurati i Replica Set, è possibile lanciare gli script di popolamento nell'ordine: Utenti -> Libri -> Ordini -> Index -> Sessioni.