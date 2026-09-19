from pymongo import MongoClient, WriteConcern
from pymongo.read_concern import ReadConcern

# Connessione con write e read concern
uri = "mongodb://libreria1:27017,libreria2:27017,libreria3:27017/?replicaSet=ReplicaSetItalia"
client = MongoClient(uri, w=2, readConcernLevel='majority')

db = client['lib-ita']
collectionLibri = db['libri']
collectionLUtenti = db['utenti']
collectionLoridni = db['ordini']


db = client.get_database('lib-ita', write_concern=WriteConcern(w=2), read_concern=ReadConcern('linearizable'))
collectionLibri = db.get_collection('libri')
collectionLUtenti = db.get_collection('utenti')
collectionLoridni = db.get_collection('ordini')

# Verifica delle configurazioni
print("Write Concern:", db.write_concern.document)
print("Read Concern:", db.read_concern.document)