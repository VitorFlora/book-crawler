from requests import Session
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from random import random
from urllib.parse import urljoin

BASE_URL = 'https://books.toscrape.com/catalogue/'
START_URL = BASE_URL + 'page-1.html'
books = []
session = Session()

def extract_book_info(book):
    h3 = book.find('h3')
    a_tag = h3.find('a')
    book_relative_url = a_tag.get('href')
    book_full_url = BASE_URL + book_relative_url

    title = a_tag.get('title')
    price = book.find('p', class_='price_color').text.replace('Â', '') # Remover caractere estranho Â
    availability_text = book.find('p', class_='instock availability').text.strip()
    availability = ''.join(filter(str.isdigit, availability_text))
    rating_tag = book.find('p', class_='star-rating')
    rating_classes = rating_tag.get('class', []) if rating_tag else []
    rating_class = rating_classes[1] if len(rating_classes) > 1 else ''
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating = rating_map.get(rating_class, 0)
    img_tag = book.find('img')
    image_relative_url = img_tag.get('src', '') if img_tag else ''
    image_full_url = urljoin('https://books.toscrape.com/', image_relative_url) if image_relative_url else ''
    book_id = book_relative_url.split('_')[-1].split('/')[0]

    try:
        book_response = session.get(book_full_url, timeout=5)
        book_soup = BeautifulSoup(book_response.content, 'html.parser')
        breadcrumb = book_soup.find('ul', class_='breadcrumb')
        links = book_soup.select('ul.breadcrumb a') if breadcrumb else []
        category = links[2].text if len(links) > 2 else ''
    except Exception:
        category = ''

    return {
        'id': book_id,
        'title': title,
        'price': price,
        'rating': rating,
        'availability': int(availability) if availability else 0,
        'category': category,
        'image_url': image_full_url
    }

current_url = START_URL
while current_url:
    print(f"Scraping... {current_url.split('.')[-2].split('/')[-1]}")
    try:
        response = session.get(current_url, timeout=10)
    except Exception as e:
        print(f"Erro ao acessar a página {current_url}: {e}")
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    books_on_page = soup.find_all('article', class_='product_pod')

    for book in books_on_page:
        books.append(extract_book_info(book))

    next_page_element = soup.select_one('li.next')
    if next_page_element:
        next_anchor = next_page_element.select_one('a')
        next_page_relative_url = next_anchor.get('href') if next_anchor else None
        current_url = BASE_URL + str(next_page_relative_url) if next_page_relative_url else None
    else:
        current_url = None

    time.sleep(random() * 0.1)

print("Salvando em 'books.csv'...")

df = pd.DataFrame(books)
df = df[['id', 'title', 'category', 'price', 'rating', 'availability', 'image_url']]
output_folder = 'data'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Pasta '{output_folder}' criada.")
else:
    print(f"Pasta '{output_folder}' já existe.")

file_path = os.path.join(output_folder, 'books.csv')
df.to_csv(file_path, index=False, encoding='utf-8')

print(f"Arquivo salvo com sucesso em: {file_path}")
print(f"Total de livros extraídos: {len(df)}")