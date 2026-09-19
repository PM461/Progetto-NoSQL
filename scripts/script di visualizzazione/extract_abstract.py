import requests
import nltk
from rake_nltk import Rake
nltk.download('stopwords')
nltk.download('punkt')

query = "0451526538"  # ISBN del libro da cui ottenere l'abstract
search_url = f"https://openlibrary.org/search.json?q={query}"
response = requests.get(search_url)
data = response.json()

if 'docs' in data:
    books = data['docs']
    if books:
        first_book = books[0]
        book_id = first_book['key']  # es. "/works/OL7353617M"
        print(f"Book ID: {book_id}")
        
book_url = f"https://openlibrary.org{book_id}.json"
response = requests.get(book_url)
book_details = response.json()

if 'description' in book_details:
    if isinstance(book_details['description'], dict):
        abstract = book_details['description'].get('value', '')
    else:
        abstract = book_details['description']
    print(f"Abstract: {abstract}")
else:
    print("Abstract not available.")
    
    
    
# KEYWORD EXTRACTION

rake_nltk_var = Rake()
rake_nltk_var.extract_keywords_from_text(abstract)
keyword_extracted = rake_nltk_var.get_ranked_phrases()
print('Parole chiave')
print(keyword_extracted)
