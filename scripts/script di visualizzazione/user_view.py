from pymongo import MongoClient
import random
import json

def get_random_user():
    """Recupera un utente casuale da MongoDB e lo stampa"""
    # Connessione al database MongoDB
    client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
    db = client['lib-ita']
    collection = db['utenti']

    # Recupera tutti gli utenti dalla raccolta
    users = list(collection.find())
    if not users:
        print("Non ci sono utenti nella raccolta.")
        return

    # Seleziona un utente casuale
    random_user = random.choice(users)
    
    # Stampa i dettagli dell'utente
    print(json.dumps(random_user, indent=4, default=str))

if __name__ == "__main__":
    get_random_user()
