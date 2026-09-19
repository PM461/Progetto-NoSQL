import requests
from pymongo import MongoClient
from bson import ObjectId


mongodb_url = 'mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia'
riak_url = 'http://localhost:8098'

# Funzione per ottenere la lista di ISBN dai libri con payment_made=True da MongoDB
def get_isbn_list_from_mongodb():
    client = MongoClient(mongodb_url)
    database = client['lib-ita']
    ordini_collection = database['ordini']  # Collezione degli ordini
    libri_collection = database['libri']  # Collezione dei libri

    user_id = ObjectId("667edc22a9607211554caabc")  # ObjectID dell'utente da cercare (hardcodato)

    isbn_list = []

    # Trova gli ordini dell'utente con l'ObjectID specificato
    ordini = ordini_collection.find({"user_id": user_id})

    # Itera sugli ordini dell'utente e recupera gli ObjectID dei libri se payment_made è True
    for ordine in ordini:
        if ordine.get('payment_made', False):
            book_ids = ordine.get('books', [])
            for book_id in book_ids:
                libro = libri_collection.find_one({"_id": book_id})
                if libro:
                    isbn = libro.get('ISBN')
                    if isbn:
                        isbn_list.append(isbn)

    client.close()  # Chiusura della connessione

    return isbn_list

# Funzione per ottenere gli ISBN associati da Riak per una parola
def get_keywords_and_isbns_from_riak(word):
    url = f"{riak_url}/riak/InvertedIndex/{word}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        document_data = response.json()

        # Verifica se il documento ha il formato atteso (lista di ISBN)
        if isinstance(document_data, list):
            return document_data  # Ritorna direttamente la lista di ISBN

        print(f"Unexpected response format for word '{word}': {response.text}")
        return []

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []

    except ValueError as e:
        print(f'ValueError: {e}')
        return []

# Funzione principale per eseguire l'integrazione
def main(libri_collection):
    # Ottieni la lista di ISBN da MongoDB
    isbn_list = get_isbn_list_from_mongodb()
    print('ISBN dei libri trovati:', isbn_list)

    # URL per la richiesta MapReduce su Riak
    mapreduce_url = f"{riak_url}/mapred"

    # Corpo della richiesta per il MapReduce
    payload = {
        "inputs": "InvertedIndex",
        "query": [
            {
                "map": {
                    "language": "javascript",
                    "source": "function(value) { return [value.key]; }"
                }
            }
        ]
    }

    # Invio della richiesta MapReduce
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(mapreduce_url, json=payload, headers=headers)
        response.raise_for_status()

        # Elaborazione della risposta MapReduce
        result = response.json()

        isbn_count_map = {}

        # Verifica gli ISBN ottenuti da MongoDB con i dati ottenuti da Riak
        for isbn_to_check in isbn_list:
            for word in result:
                try:
                    isbns = get_keywords_and_isbns_from_riak(word)

                    # Controlla se l'ISBN da verificare è presente nella lista di ISBN
                    if isbn_to_check in isbns:
                        # Aggiorna la mappa isbn_count_map con gli ISBN associati
                        for isbn in isbns:
                            if isbn != isbn_to_check:
                                if isbn not in isbn_count_map:
                                    isbn_count_map[isbn] = 0
                                isbn_count_map[isbn] += 1

                except Exception as e:
                    print(f"Error processing word '{word}': {e}")

    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
        exit()

    except ValueError as e:
        print(f'ValueError: {e}')
        exit()

    # Trova i 5 ISBN che compaiono più frequentemente
    top_isbns = sorted(isbn_count_map.items(), key=lambda item: item[1], reverse=True)[:5]

    # Stampa i titoli dei libri associati ai top 5 ISBN più frequenti
    print("\nTop 5 libri che compaiono più frequentemente:")
    for isbn, count in top_isbns:
        # Ottieni il titolo del libro associato all'ISBN
        try:
            titolo = libri_collection.find_one({"ISBN": isbn}).get('titolo')
            print(f"Titolo: {titolo}, ISBN: {isbn}, Frequenza: {count} volte")
        except AttributeError:
            print(f"ISBN: {isbn}, Frequenza: {count} volte (Titolo non disponibile)")

if __name__ == "__main__":
    client = MongoClient(mongodb_url)
    db = client['lib-ita']
    libri_collection = db['libri']
    main(libri_collection)
