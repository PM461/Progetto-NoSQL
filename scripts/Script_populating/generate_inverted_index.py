from pymongo import MongoClient
import requests
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Funzione per ottenere l'abstract da Open Library tramite ISBN
def get_abstract_from_isbn(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    data = response.json()
    
    # Estrai l'abstract se disponibile
    book_key = f"ISBN:{isbn}"
    if book_key in data and 'excerpts' in data[book_key]:
        return data[book_key]['excerpts'][0]['text']
    return None

# Funzione per creare l'inverted index dal testo dell'abstract
def create_inverted_index(abstract):
    tokens = word_tokenize(abstract)
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    filtered_tokens = [ps.stem(word) for word in tokens if word.isalnum() and word.lower() not in stop_words]
    filtered_tokens.append("prova")
    filtered_tokens.append("prova2")
    inverted_index = defaultdict(set)  # Utilizziamo un set invece di una lista per evitare duplicati di ISBN
    
    for idx, word in enumerate(filtered_tokens):
        inverted_index[word].add(idx)  # Utilizziamo un set invece di una lista per evitare duplicati di posizioni
    
    return inverted_index

# Funzione per inserire o aggiornare l'inverted index in Riak con una lista di ISBN
def update_inverted_index(word, isbn_list):
    url = f"http://localhost:8098/riak/InvertedIndex/{word}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        # Controlla se il documento per la parola esiste già
        response = requests.get(url)
        
        if response.status_code == 200:
            # Converti la risposta JSON in una lista di ISBN
            document = response.json()
            updated = False
            
            for isbn in isbn_list:
                if isbn not in document:
                    document.append(isbn)
                    updated = True
            
            # Esegui la richiesta PUT per aggiornare il documento solo se ci sono modifiche
            if updated:
                response = requests.put(url, json=document, headers=headers)
                response.raise_for_status()  # Solleva un'eccezione se la richiesta non ha successo
                
                if response.status_code == 204:
                    print(f"Updated Riak document for word '{word}' with ISBNs '{isbn_list}'.")
                else:
                    print(f"Unexpected status code: {response.status_code}")
            else:
                print(f"ISBNs already exist in Riak document for word '{word}'. No update needed.")
        
        elif response.status_code == 404:
            # Il documento non esiste, crea un nuovo documento
            data = list(isbn_list)  # Converto la lista in un normale elenco per la creazione del documento
            response = requests.put(url, json=data, headers=headers)
            response.raise_for_status()  # Solleva un'eccezione se la richiesta non ha successo
            
            if response.status_code == 204:
                print(f"Created new Riak document for word '{word}' with ISBNs '{isbn_list}'.")
            else:
                print(f"Unexpected status code: {response.status_code}")
        
        else:
            print(f"Unexpected status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

# Funzione principale per eseguire il processo
def main():
    # Connessione al server MongoDB
    client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')  # Assicurati di sostituire con il tuo URI MongoDB se necessario

    # Seleziona il database e la collezione
    db = client['lib-ita'] 
    collection = db['libri']  

    # Trova tutti i documenti nella collezione "libri" e raccogli gli ISBN
    isbn_list = []
    for document in collection.find({}, {"ISBN": 1, "_id": 0}):
        if "ISBN" in document:
            if isinstance(document["ISBN"], list):
                isbn_list.extend(document["ISBN"])
            else:
                isbn_list.append(document["ISBN"])

    # Rimuovi duplicati
    unique_isbn_list = list(set(isbn_list))

    # Stampa la lista degli ISBN
    print("Lista degli ISBN trovati nella collezione 'libri':")
    for isbn in unique_isbn_list:
        print(isbn)

    # Processa ciascun ISBN
    for isbn in unique_isbn_list:
        # Ottieni l'abstract da Open Library per l'ISBN corrente
        abstract = get_abstract_from_isbn(isbn)
        if not abstract:
            print(f"Abstract not found for ISBN: {isbn}")
            continue
        
        # Crea l'inverted index per l'abstract
        inverted_index = create_inverted_index(abstract)
        
        # Aggiorna l'inverted index in Riak per ogni parola trovata
        for word in inverted_index:
            update_inverted_index(word, [isbn])  # Passiamo una lista con un solo ISBN per ciascuna parola

    print(f"Inverted index successfully updated in Riak for ISBN list: {unique_isbn_list}")

    # Chiudi la connessione
    client.close()

# Esempio di utilizzo
if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    
    main()
