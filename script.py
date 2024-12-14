import pdb
import requests
import html5lib
from bs4 import BeautifulSoup

# selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import  NoSuchElementException, TimeoutException, WebDriverException
import time


class ECommerceWebsiteScrapping:

    def __init__(self):
        self.url = 'https://www.ebay.com/'
        self.categories = []

        # fetch all the available categories
        self.fetch_categories()

    # request call to provided url and return its response
    def call_url(self,url=None):
        try:
            if url is not None and isinstance(url,str):
                response = requests.get(url)
            else:
                if self.url is None:
                    return {'status':False,'error':'Url is not set'}
                response = requests.get(self.url)
            response.raise_for_status()
            return {'status':True,'response':response}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            return {'status':False,'error':f'A connection error or timeout occurred : {str(e)}'}
        except requests.exceptions.HTTPError as e:
            return {'status':False,'error':f'HTTP Error :{ str(e)}'}
        except Exception as e:
            return {'status':False,'error':f'An error occurred: {str(e)}'}

    # Prepare a soup from html content
    def html_to_soup(self,content):
        try:
            soup = BeautifulSoup(content,'html5lib')
            return soup
        except Exception as e:
            print('Unexpected error occour : ', str(e))
            return ''

    # update self.categories through selenium
    def fetch_categories(self):
        try:
            driver = webdriver.Chrome()
            driver.get(self.url)
            time.sleep(3)
            dropdown_element = driver.find_element('id', 'gh-cat')
            select = Select(dropdown_element)

            # Get all options
            options = select.options

            list_of_categories = [option.text.strip() for option in options]
            self.categories = list_of_categories
            return self.categories
        except NoSuchElementException as e:
            print('No select element found : ', str(e))
            return self.categories
        
        except TimeoutException as e:
            print('Pages takes too long time to load : ', str(e))
            return self.categories
        
        except WebDriverException as e:
            print('webdriver encounter an issue :', str(e))
            return self.categories
        
        except Exception as e:
            print('An unexpected issue : ',str(e))
            return self.categories
        
        finally:
            if driver:
                driver.quit()


def main():
    e_commerce_website = ECommerceWebsiteScrapping()
    print('script executed..',e_commerce_website.categories)


if __name__=="__main__":
    main()

