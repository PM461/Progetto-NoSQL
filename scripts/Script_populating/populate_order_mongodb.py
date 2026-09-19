from pymongo import MongoClient
from faker import Faker
from bson import ObjectId
import random
import datetime

# Connetti a MongoDB
client = MongoClient('mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia')
db = client['lib-ita'] 

# Collezioni
collection_libri = db['libri']
collection_utenti = db['utenti']
collection_ordini = db['ordini']

# Generatore di dati fittizi
fake = Faker()

# Ottieni tutti gli ObjectId degli utenti e dei libri
utenti_ids = [user['_id'] for user in collection_utenti.find({}, {'_id': 1})]
libri_ids = [book['_id'] for book in collection_libri.find({}, {'_id': 1})]

# Funzione per convertire datetime.date a datetime.datetime
def to_datetime(date):
    return datetime.datetime(date.year, date.month, date.day)

# Funzione per generare ordini fittizi
def generate_order():
    user_id = random.choice(utenti_ids)
    num_books = random.randint(1, 5)
    books = random.sample(libri_ids, num_books)
    purchase_date = fake.date_between(start_date='-1y', end_date='today')
    total_spent = sum([round(random.uniform(5.0, 50.0), 2) for _ in range(num_books)])
    payment_made = random.choice([True, False])
    delivery_date = fake.date_between(start_date=purchase_date, end_date='today') if payment_made else None
    
    order = {
        "user_id": user_id,
        "books": books,
        "purchase_date": to_datetime(purchase_date),
        "total_spent": total_spent,
        "payment_made": payment_made,
        "delivery_date": to_datetime(delivery_date) if delivery_date else None
    }
    
    return order

# Genera e inserisci ordini
num_orders_to_generate = 100  # Numero di ordini da generare
orders = [generate_order() for _ in range(num_orders_to_generate)]

# Inserisci i dati in MongoDB
collection_ordini.insert_many(orders)
print("Ordini inseriti con successo.")

# Chiudi la connessione
client.close()
