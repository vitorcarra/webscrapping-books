from requests import get
from bs4 import BeautifulSoup as bs
from collections import namedtuple
import sys

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
        page_source = get(url=url)
        return bs(page_source.text, 'html.parser')
        
    def _gen_books(self, books_urls, category):
        book = namedtuple('Book', 'name category price rating available')

        for url in books_urls:
            book_url = f'{self.base_url}url'
            book_content = self._get_page(book_url)
            name = ''
            price = ''
            rating = ''
            available = 0
            yield book(name, category, price, rating, available)

        """
            books_list = books_catalog.find('section').find_all('li', {'class': 'col-xs-6 col-sm-4 col-md-3 col-lg-3'})

            for book in books_list 

            ### name, price, rating, availability
        """

    def _gen_books_category(self, url):
        try:
            page_index = self._get_page(url)
            total_books = int(page_index.find('form', {'class': 'form-horizontal'})
                                        .find('strong').text
                            ) #  first form shows the total books
            category_name = url.split('/')[6].split('_')[0] #  category name is at 6th position in the URL
            
            if total_books <= 20:
                total_pages = 1
            else:
                total_pages = total_books // 20 # we need to divide by 20 (max books in a page)
                if total_books % 20 > 0: #  we check if is there a last page with less then 20
                    total_pages += 1

            books_links = []
            for page_number in range(1,total_pages+1):
                print("{} - page {}".format(category_name, str(page_number)))
                if page_number > 1:
                    page_url = url.replace('index', 'page-' + str(page_number))
                else:
                    page_url = url
                print(page_url)
                page_content = self._get_page(page_url)
                product_boxes = page_content.find_all('article',{'class': 'product_pod'})
            
                for book_link in product_boxes:
                    books_links.append(book_link.find('a').get('href').replace('../',''))

                #_gen_books(books_links, category_name)
                print('Category: {}'.format(category_name))
                print('books_links: {}'.format(books_links))
                    

            return True
        except Exception as e:
            print("Error: {}".format(e))
            return False
            

    def scrap(self):
        first_page = self._get_first_page()
        total_books = int(first_page.find('form', {'class': 'form-horizontal'})
                                    .find('strong').text
                         ) #  first form shows the total books

        print("Total books to process: {}".format(str(total_books)))
        #print("Items per page: {}".format(str(self.items_per_page)))

        books_categories = [self.base_url + link.get('href') for link in first_page.find('div', {'class' : 'side_categories'}).find('ul', {'class': 'nav nav-list'}).find('ul').find_all('a')]
        #print(books_categories)

        for category in books_categories:
            all_books = self._gen_books_category(category)


if __name__ == '__main__':
    base_url = 'http://books.toscrape.com/'
    first_page = 'index.html'  #  where we will get the total of pages to process
    items_per_page = 20 #  this the default value of this site

    b = BookStore(url=base_url, first_page=first_page, items_per_page=items_per_page) #  all products list
    #b.scrap()
    
