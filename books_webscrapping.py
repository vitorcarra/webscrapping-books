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

    def _gen_books(self, page: int):
        catalog_page = f'{self.base_url}/catalogue/page-'
        url_books_page = catalog_page + str(page) + '.html'

        books_catalog = get(url_books_page)

        """
            books_list = books_catalog.find('section').find_all('li', {'class': 'col-xs-6 col-sm-4 col-md-3 col-lg-3'})

            for book in books_list 

            ### name, price, rating, availability
        """

    def _gen_category(self, url):
        page_index = get(url)
        total_books = int(first_page.find('form', {'class': 'form-horizontal'})
                                    .find('strong').text
                         ) #  first form shows the total books

        if total_books <= 20:
            total_pages = 1
        else:
            total_pages = total_books // 20 # we need to divide by 20 (max books in a page)
            if total_books % 20 > 0: #  we check if is there a last page with less then 20
                total_pages += 1
            

    def scrap(self):
        first_page = self._get_first_page()
        total_books = int(first_page.find('form', {'class': 'form-horizontal'})
                                    .find('strong').text
                         ) #  first form shows the total books

        print("Total books to process: {}".format(str(total_books)))
        

        books_categories = [self.base_url + link.get('href') for link in first_page.find('div', {'class' : 'side_categories'}).find('ul', {'class': 'nav nav-list'}).find_all('a')]
        print(books_categories)
        #print("Items per page: {}".format(str(self.items_per_page)))


if __name__ == '__main__':
    base_url = 'http://books.toscrape.com/'
    first_page = 'index.html'  #  where we will get the total of pages to process
    items_per_page = 20 #  this the default value of this site

    b = BookStore(url=base_url, first_page=first_page, items_per_page=items_per_page) #  all products list
    #b.scrap()
    
