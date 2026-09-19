from pymongo import MongoClient
import random
import json

def get_random_book():
    """Recupera un libro casuale da MongoDB e lo stampa"""
    # Connessione al database MongoDB
    client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
    db = client['lib-ita']
    collection = db['libri']

    # Recupera tutti i libri dalla raccolta
    books = list(collection.find())
    if not books:
        print("Non ci sono libri nella raccolta.")
        return

    # Seleziona un libro casuale
    random_book = random.choice(books)
    
    # Stampa i dettagli del libro
    print(json.dumps(random_book, indent=4, default=str))

if __name__ == "__main__":
    get_random_book()
