from pymongo import MongoClient
import random
import json

def get_random_order():
    """Recupera un ordine casuale da MongoDB e lo stampa"""
    # Connessione al database MongoDB
    client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
    db = client['lib-ita']
    collection = db['ordini']

    # Recupera tutti gli ordini dalla raccolta
    orders = list(collection.find())
    if not orders:
        print("Non ci sono ordini nella raccolta.")
        return

    # Seleziona un ordine casuale
    random_order = random.choice(orders)
    
    # Stampa i dettagli dell'ordine
    print(json.dumps(random_order, indent=4, default=str))

if __name__ == "__main__":
    get_random_order()
