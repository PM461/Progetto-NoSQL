import requests
import uuid
import random
import datetime
from pymongo import MongoClient

def get_mongo_client():
    """Configura il client MongoDB"""
    client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
    return client

def fetch_random_user_ids(mongo_client, db_name, collection_name, count):
    """Recupera un numero casuale di user_id dal database MongoDB"""
    db = mongo_client[db_name]
    collection = db[collection_name]
    user_ids = list(collection.find({}, {"_id": 1}))
    if not user_ids:
        raise ValueError(f"La raccolta {collection_name} è vuota")
    return [str(random.choice(user_ids)["_id"]) for _ in range(count)]

def fetch_random_books(mongo_client, db_name, collection_name, max_books):
    """Recupera un numero casuale di libri dal database MongoDB"""
    db = mongo_client[db_name]
    collection = db[collection_name]
    books = list(collection.find({}, {"_id": 1}))
    if not books:
        raise ValueError(f"La raccolta {collection_name} è vuota")
    num_books = random.randint(1, max_books)
    return [str(random.choice(books)["_id"]) for _ in range(num_books)]

def set_bucket_ttl(bucket_url, ttl_seconds):
    """Imposta il TTL per un bucket"""
    props = {
        "props": {
            "ttl": ttl_seconds
        }
    }
    response = requests.put(f'{bucket_url}/props', json=props)
    if response.status_code == 200:
        print(f'TTL impostato a {ttl_seconds} secondi per il bucket {bucket_url}')
    else:
       #print(f'Errore nell\'impostare il TTL per il bucket {bucket_url}. Status code: {response.status_code}, Risposta: {response.text}')#
        print("!")
def save_session_to_riak(bucket_url, session_data):
    """Salva una sessione in Riak usando richieste HTTP POST"""
    session_id = str(session_data["user_id"])
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{bucket_url}/{session_id}', json=session_data, headers=headers)
    if response.status_code == 204:
        print(f'Sessione salvata con ID: {session_id}')
    else:
        print(f'Errore nel salvataggio della sessione con ID: {session_id}. Status code: {response.status_code}, Risposta: {response.text}')

def simulate_sessions():
    """Simula la creazione e il salvataggio di sessioni"""
    # Configura il client MongoDB
    mongo_client = get_mongo_client()
    
    # URL del bucket Riak
    bucket_url = 'http://localhost:32768/riak/UserSession'
    
    # TTL per le sessioni (ad esempio, 3600 secondi = 1 ora)
    ttl_seconds = 3600
    
    # Imposta il TTL per il bucket
    set_bucket_ttl(bucket_url, ttl_seconds)
    
    # Numero di sessioni da creare
    num_sessions = 5
    
    for _ in range(num_sessions):
        try:
            # Recupera un user_id casuale
            user_id = fetch_random_user_ids(mongo_client, 'lib-ita', 'utenti', 1)[0]
            
            # Recupera un numero casuale di libri (massimo 5)
            cart_books = fetch_random_books(mongo_client, 'lib-ita', 'libri', 5)
            
            # Dati della sessione
            session_data = {
                'user_id': user_id,
                'login_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'last_activity': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'session_data': {
                    'preferences': {'theme': 'dark', 'language': 'it'}
                }
            }
            
            # Salva la sessione simulata in Riak
            save_session_to_riak(bucket_url, session_data)
        except ValueError as e:
            print(e)
            break

if __name__ == "__main__":
    simulate_sessions()
