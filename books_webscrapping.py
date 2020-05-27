from requests import get
from bs4 import BeautifulSoup as bs
from collections import namedtuple
import sys
import csv
import argparse
import json

class BookStore:

    def __init__(self, url: str, first_page: str, items_per_page: int):
        self.base_url = url
        self.first_page_prefix = first_page
        self.items_per_page = items_per_page

    def _get_first_page(self):
        self.books_store = get(url=self.base_url + self.first_page_prefix) 

        if self.books_store.status_code != 200:
            print("Error while navigating to the url <{}>".format(self.url))
            print("Error code: {} - Reason: {}".format(self.books_store.status_code,
                                                       self.books_store.reason))
            sys.exit(1)
        else:
            books_store_page = bs(self.books_store.text, 'html.parser')

        return books_store_page

    def _get_page(self, url:str):
        page_source = get(url=url, timeout=60)
        page_source.encoding = 'utf-8'
        return bs(page_source.text, 'html.parser')
        
    def _get_book_details(self, url:str):
        book = namedtuple('Book', 'name category price rating available')

        book_url = self.base_url + 'catalogue/' + url
        try:
            book_content = self._get_page(book_url)
            product_data = book_content.find('div', {'class': 'product_main'})
            name = product_data.find('h1').text
            price = product_data.find('p', {'class': 'price_color'}).text
            rating = product_data.find('p', {'class': 'star-rating'}).attrs.get('class')[1] # number of stars is in the class
            available = product_data.find('p', {'class': 'instock availability'}).text.strip()
            in_stock = available[available.index('(')+1:available.index('available')-1]
            category = book_content.find('ul', {'class': 'breadcrumb'}).find_all('li')[2].text.strip()

            return book(name, category, price, rating, in_stock)
        except Exception as e:
            print(e)
            return None

    def _gen_books(self, url:str):
        book = namedtuple('Book', 'name category price rating available')

        try:    
            books_links = []
            page_content = self._get_page(url)
            product_boxes = page_content.find_all('article',{'class': 'product_pod'})
        
            for book_link in product_boxes:
                books_links.append(book_link.find('a').get('href').replace('../',''))

            return map(self._get_book_details, books_links)

        except Exception as e:
            print("Error: {}".format(e))
            return False
            

    def scrap(self):
        first_page = self._get_first_page()
        total_books = int(first_page.find('form', {'class': 'form-horizontal'})
                                    .find('strong').text
                         ) #  first form shows the total books

        #print("Total books to process: {}".format(str(total_books)))
        #print("Items per page: {}".format(str(self.items_per_page)))

        if total_books <= 20:
                total_pages = 1
        else:
            total_pages = total_books // 20 # we need to divide by 20 (max books in a page)
            if total_books % 20 > 0: #  we check if is there a last page with less then 20
                total_pages += 1
        
        pages_urls = [self.base_url + 'catalogue/category/books_1/page-{}.html'.format(str(page_num))
                                            for page_num in range(total_pages + 1)]
                                            

        all_books = []
        for page in pages_urls:
            all_books += self._gen_books(page)
        
        return all_books
        

        #books_categories = [self.base_url + link.get('href') for link in first_page.find('div', {'class' : 'side_categories'}).find('ul', {'class': 'nav nav-list'}).find('ul').find_all('a')]
        #print(books_categories)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', help='Output format (json/csv)', required=True)
    parser.add_argument('-o', '--output', help='Output file', required=True)
    args = parser.parse_args()
    
    base_url = 'http://books.toscrape.com/'
    first_page = 'index.html'  #  where we will get the total of pages to process
    items_per_page = 20 #  this the default value of this site

    b = BookStore(url=base_url, first_page=first_page, items_per_page=items_per_page) #  all products list
    result = b.scrap()

    if args.format == 'csv':
        with open(args.output, 'w', newline='', encoding='utf8') as f:
            csv_wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            csv_wr.writerow(['name', 'category', 'price', 'rating', 'available'])
            for row in result:
                csv_wr.writerow(list(row))
    
    if args.format == 'json':
        json_output = {}
        json_output['data'] = []
        with open(args.output, 'w', newline='', encoding='utf8') as f:
            for row in result:
                json_output['data'].append({
                    'name': row.name,
                    'category': row.category,
                    'price': row.price,
                    'rating': row.rating,
                    'available': row.available
                })

            json.dump(json_output, f, ensure_ascii=False)
    
