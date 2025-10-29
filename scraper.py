#%%
from random import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

URL = 'https://books.toscrape.com/catalogue/'
current_url = URL + 'page-1.html'
books = []

book_counter = 0
BOOK_LIMIT = 5

while URL:
    print(f"Scraping... {current_url}")
    
    try:
        response = requests.get(current_url)
        response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página {current_url}: {e}")
        break

    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontra todos os 'artigos' de livros na página
    books_on_page = soup.find_all('article', class_='product_pod')

    # Itera sobre cada livro encontrado na página
    for book in books_on_page:
        book_relative_url = book.find('h3').find('a').get('href')
        if not book_relative_url:
            continue
        book_full_url = URL + book_relative_url
        
        # Acessa a página de detalhes
        try:
            book_response = requests.get(book_full_url)
            book_response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página do livro {book_full_url}: {e}")
            continue # Pula para o próximo livro

        book_soup = BeautifulSoup(book_response.content, 'html.parser')

        # Extração dos dados
        # Id, Título, Preço, Disponibilidade, Categoria, Avaliação e Imagem
        id = book_relative_url.split('_')[ -1].split('/')[0]
        title = book_soup.find('h1').text
        price = book_soup.find('p', class_='price_color').text.replace('Â', '')
        availability_text = book_soup.find('p', class_='instock availability').text.strip()
        availability = ''.join(filter(str.isdigit, availability_text))        
        category = book_soup.find('ul', class_='breadcrumb').find_all('a')[2].text
        rating_tag = book_soup.find('p', class_='star-rating')
        rating_classes = rating_tag.get('class', []) if rating_tag else []
        rating_class = rating_classes[1] if len(rating_classes) > 1 else ''
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        rating = rating_map.get(rating_class, 0)
        img_container = book_soup.find('div', class_='item active')
        img_src = ''
        if img_container:
            img_tag = img_container.find('img')
            if img_tag:
                img_src = img_tag.get('src', '') or ''
        image_relative_url = img_src
        image_full_url = image_relative_url.replace('../../', 'https://books.toscrape.com/') if image_relative_url else ''

        #Adiciona os dados na lista
        books.append({
            'id': id,
            'title': title,
            'price': price,
            'rating': rating,
            'availability': int(availability),
            'category': category,
            'image_url': image_full_url
        })
        
        time.sleep(random() * 0.1)

    # Begin Debug
        book_counter += 1
        print(f"Livro {book_counter} de {BOOK_LIMIT} extraído: {title}")
        if book_counter >= BOOK_LIMIT:
            break

        time.sleep(0.1)

    if book_counter >= BOOK_LIMIT:
        break

    # End Debug

    # Paginação
    next_page_element = soup.find('li', class_='next')
    if next_page_element:
        next_anchor = next_page_element.find('a')
        next_page_relative_url = next_anchor.get('href') if next_anchor else None
        if next_page_relative_url:
            current_url = URL + next_page_relative_url
        else:
            current_url = None
    else:
        current_url = None

print("Salvando os dados em 'books.csv'...")

df = pd.DataFrame(books)
df = df[['id', 'title', 'category', 'price', 'rating', 'availability', 'image_url']]
output_folder = 'data'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Pasta '{output_folder}' criada.")
else :
    print(f"Pasta '{output_folder}' já existe.")

file_path = os.path.join(output_folder, 'books.csv')
df.to_csv(file_path, index=False, encoding='utf-8')

print(f"Arquivo salvo com sucesso em: {file_path}")
print(f"Total de livros extraídos: {len(df)}")