import requests
from pymongo import MongoClient
from faker import Faker
import random

# Connetti a MongoDB
client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
db = client['lib-ita']
collection = db['libri']

# Generatore di dati fittizi
fake = Faker()

# Funzione per ottenere dati sui libri dall'API di Open Library
def get_books_data(isbn_list):
    base_url = "https://openlibrary.org/api/books"
    books_data = []

    for isbn in isbn_list:
        url = f"{base_url}?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            key = f"ISBN:{isbn}"
            if key in data:
                book_data = data[key]
                filtered_data = {
                    "titolo": book_data.get("title", "No title available"),
                    "autori": [author["name"] for author in book_data.get("authors", [])],
                    "copertina": book_data.get("cover", {}).get("large", "No cover available"),
                    "ISBN": isbn,
                    "prezzo": round(random.uniform(5.0, 50.0), 2),
                    "valutazione_media": round(random.uniform(1.0, 5.0), 1),
                    "disponibilità": random.randint(0, 1000)
                }
                books_data.append(filtered_data)
    
    return books_data

# Lista di ISBN per esempio
isbn_list = [
    "9780316769488",  # The Catcher in the Rye by J.D. Salinger
    "9780061120084",  # To Kill a Mockingbird by Harper Lee
    "9780743273565",  # The Great Gatsby by F. Scott Fitzgerald
    "9780747532743",  # Harry Potter and the Philosopher's Stone by J.K. Rowling
    "9780439139601",  # Harry Potter and the Goblet of Fire by J.K. Rowling
    "9780439064866",  # Harry Potter and the Chamber of Secrets by J.K. Rowling
    "9780439139595",  # Harry Potter and the Prisoner of Azkaban by J.K. Rowling
    "9780618260300",  # The Hobbit by J.R.R. Tolkien
    "9780544003415",  # The Lord of the Rings by J.R.R. Tolkien
    "9780451524935",  # 1984 by George Orwell
    "9780451526342",  # Animal Farm by George Orwell
    "9780141439518",  # Pride and Prejudice by Jane Austen
    "9780142437247",  # Moby-Dick by Herman Melville
    "9780140328721",  # The BFG by Roald Dahl
    "9780307474278",  # The Road by Cormac McCarthy
    "9780743273565",  # The Great Gatsby by F. Scott Fitzgerald
    "9780385737951",  # Looking for Alaska by John Green
    "9780316015844",  # Twilight by Stephenie Meyer
    "9780307277671",  # The Kite Runner by Khaled Hosseini
    "9780812981605",  # The Martian by Andy Weir
]

books_data = get_books_data(isbn_list)

# Inserisci i dati in MongoDB
if books_data:
    collection.insert_many(books_data)
    print("Dati inseriti con successo.")
else:
    print("Nessun dato trovato.")

# Chiudi la connessione
client.close()
