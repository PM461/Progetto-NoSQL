import requests
import random
import json

def get_random_session_key(bucket_url):
    """Recupera una chiave casuale da Riak e stampa i dettagli della sessione"""
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(f'{bucket_url}?keys=true', headers=headers)
    if response.status_code == 200:
        keys = response.json().get('keys', [])
        if not keys:
            print("Non ci sono chiavi nel bucket.")
            return

        # Prendi una chiave casuale
        random_key = random.choice(keys)
        print(f'Chiave casuale recuperata: {random_key}')

        session_response = requests.get(f'{bucket_url}/{random_key}', headers=headers)
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(json.dumps(session_data, indent=4))
        else:
            print(f'Errore nel recupero della sessione con ID: {random_key}. Status code: {session_response.status_code}, Risposta: {session_response.text}')
    else:
        print(f'Errore nel recupero delle chiavi dal bucket {bucket_url}. Status code: {response.status_code}, Risposta: {response.text}')

if __name__ == "__main__":
    bucket_url = 'http://localhost:32768/riak/UserSession'
    get_random_session_key(bucket_url)
