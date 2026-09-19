import requests
from pymongo import MongoClient

def get_book_data_from_api(isbn):
    base_url = "https://openlibrary.org/api/books"
    params = {
        'bibkeys': f'ISBN:{isbn}',
        'format': 'json',
        'jscmd': 'data'
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        key = f'ISBN:{isbn}'
        if key in data:
            book_data = data[key]
            title = book_data.get('title', 'N/A')
            authors = [author['name'] for author in book_data.get('authors', [])]
            cover = book_data.get('cover', {}).get('large', 'N/A')
            publishers = [publisher['name'] for publisher in book_data.get('publishers', [])]
            language = book_data.get('languages', {})
            number_of_pages = book_data.get('number_of_pages', {})
            publish_date = book_data.get('publish_date', {})
            
            return title, authors, cover, publishers, language, number_of_pages, publish_date
        else:
            print(f"No data found for ISBN {isbn}")
            return None
    else:
        print(f"Error fetching data from API: {response.status_code}")
        return None

def get_book_data_from_mongodb(isbn):
    client = MongoClient('mongodb://localhost:27017/?directConnection=true')
    db = client['lib-ita']
    collection = db['libri']
    
    book_data = collection.find_one({'ISBN': isbn})
    if book_data:
        price = book_data.get('prezzo', 'N/A')
        average_rating = book_data.get('valutazione_media', 'N/A')
        availability = book_data.get('disponibilità', 'N/A')
        return price, average_rating, availability
    else:
        print(f"No data found in MongoDB for ISBN {isbn}")
        return None

def main(isbn):
    api_data = get_book_data_from_api(isbn)
    if api_data:
        title, authors, cover, publishers, language, number_of_pages, publish_date = api_data
        print(f"Titolo: {title}")
        print(f"Autori: {', '.join(authors)}")
        print(f"Copertina: {cover}")
        print(f"Editore: {publishers}")
        print(f"Lingua: {language}")
        print(f"N.Pagine: {number_of_pages}")
        print(f"Anno di pubblicazione: {publish_date}") 
    
    db_data = get_book_data_from_mongodb(isbn)
    if db_data:
        price, average_rating, availability = db_data
        print(f"Price: {price}")
        print(f"Average Rating: {average_rating}")
        print(f"Availability: {availability}")

if __name__ == "__main__":
    isbn = "0451526538"
    main(isbn)
