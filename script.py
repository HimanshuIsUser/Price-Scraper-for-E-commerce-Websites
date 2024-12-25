import pdb
import requests
import html5lib
from bs4 import BeautifulSoup
import html


# selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import  NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
import time

import logging


logging.basicConfig(filename='script.log',
                    format='%(asctime)s %(message)s',
                    filemode='w',
                    level=logging.DEBUG
                    )

logger = logging.getLogger()


class ECommerceWebsiteScrapping:

    def __init__(self):
        self.url = 'https://www.ebay.com'
        self.categories = []

        # fetch all the available categories
        # self.fetch_categories()

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

    # Collect products categories from website
    def get_deals_category(self):
        try:
            driver = webdriver.Chrome()
            driver.get(f'{self.url}/globaldeals')
            time.sleep(2)
            element = driver.find_element(by=By.CLASS_NAME, value='navigation-desktop')
            ul = element.find_element(by=By.CLASS_NAME, value='ebayui-refit-nav-ul')
            list_li = ul.find_elements(by=By.XPATH, value='.//li')
            category_data = {}
            for i in list_li:
                category_data[i.text] = {}
                div_element = i.find_elements(by=By.CLASS_NAME,value='navigation-desktop-flyout-col')
                for div in div_element:
                    options = div.find_elements(by=By.TAG_NAME, value='a')

                    for option in options:                        
                        href = option.get_attribute('href')
                        inner_html = option.get_attribute('innerHTML')
                        text = html.unescape(inner_html)
                        category_data[i.text][text] = [text,href]
            return category_data
        except Exception as e:
            print('An Unexpected error : ', str(e))
        finally:
            if driver:
                driver.quit()

    # collect products
    def get_products(self):
        try:
            driver = webdriver.Chrome()
            driver.get(f'{self.url}/globaldeals/home/more-home-garden/')
            time.sleep(2)
            element_div = driver.find_element(by=By.CLASS_NAME,value='sections-container')
            if not element_div:
                print('No element found products')
            parent_div = element_div.find_element(by=By.CLASS_NAME,value='no-category-dropdown')
            products_div = parent_div.find_element(by=By.CLASS_NAME,value='spoke-itemgrid-container')
            container_div = products_div.find_element(by=By.ID, value='spokeResultSet')
            collection_div = container_div.find_element(by=By.CLASS_NAME,value='item-grid-spoke')
            products = collection_div.find_elements(by=By.CLASS_NAME,value='col')
            logger.info('products scrap completed.')
        except Exception as e:
            print(str(e))

    # Save data in csv file
    def store_data_in_csv(self,filename,content):
        try:
            with open(f'{filename}.csv','a') as file:
                file.writelines(content)
            print('Product has been saved in csv file')
        except Exception as e:
            print('An Unexpected error occur : ',str(e))
            logger.error(f"Error generating CSV file: {e}", exc_info=True)




def main():
    e_commerce_website = ECommerceWebsiteScrapping()
    category_data = e_commerce_website.get_products()
    print('script executed..',category_data)


if __name__=="__main__":
    main()

