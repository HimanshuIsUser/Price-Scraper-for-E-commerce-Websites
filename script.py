import pdb
import requests
import html5lib
from bs4 import BeautifulSoup
import html
import os
import csv
# selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import  NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
import time
import json

import logging
import datetime


logging.basicConfig(filename='script.log',
                    format='%(asctime)s %(message)s',
                    filemode='w',
                    level=logging.DEBUG
                    )

logger = logging.getLogger()
import pdb

class ECommerceWebsiteScrapping:

    def __init__(self):
        self.url = 'https://www.ebay.com'
        self.categories = {}
        self.driver = None

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

            self.categories = category_data
            return category_data
        except Exception as e:
            print('An Unexpected error : ', str(e))
        finally:
            if driver:
                driver.quit()

    # collect products
    def get_products(self,category_path='https://www.ebay.com/globaldeals/home/more-home-garden'):
        try:
            if self.driver is None:
                self.driver = webdriver.Chrome()
                self.driver.get(f'{category_path}')
            else:
                self.driver.get(f'{category_path}')
            time.sleep(2)
            products_details = []
            element_div = self.driver.find_element(by=By.CLASS_NAME,value='sections-container')
            if not element_div:
                print('No element found products')
            parent_div = element_div.find_element(by=By.CLASS_NAME,value='no-category-dropdown')
            products_div = parent_div.find_element(by=By.CLASS_NAME,value='spoke-itemgrid-container')
            container_div = products_div.find_element(by=By.ID, value='spokeResultSet')
            collection_div = container_div.find_element(by=By.CLASS_NAME,value='item-grid-spoke')
            products = collection_div.find_elements(by=By.CLASS_NAME,value='col')
            for i in products:

                # image extractor
                detail_element_image = i.find_element(by=By.CLASS_NAME,value='dne-itemtile-imagewrapper')
                image_element = detail_element_image.find_element(by=By.TAG_NAME,value='img')
                image_src = image_element.get_attribute('src')
        
                # details extractor
                detail_element = i.find_element(by=By.CLASS_NAME,value='dne-itemtile-detail')
                a_tag = detail_element.find_element(by=By.TAG_NAME,value='a')
                url = a_tag.get_attribute('href')

                # extract title
                title_element = a_tag.find_element(by=By.TAG_NAME,value='h3')
                title = title_element.get_attribute('title')

                # price extractor
                price_div = detail_element.find_element(by=By.CLASS_NAME,value='dne-itemtile-price')
                price_span = price_div.find_element(by=By.CLASS_NAME,value='first')
                price = price_span.text

                # append details in list
                products_details.append({'title':title,'url':url,'image_src':image_src,'price':price})

            logger.info('products scrap completed.')
        except Exception as e:
            print(str(e))
        finally:
            return products_details
                
    # Save data in csv file
    def store_data_in_csv(self,filename,content):
        try:
            with open(f'{filename}.csv','a') as file:
                fieldnames = ['title','url','image_src','price']
                writer = csv.DictWriter(file,fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(content)
            print('Product has been saved in csv file')
        except Exception as e:
            print('An Unexpected error occur : ',str(e))
            logger.error(f"Error generating CSV file: {e}", exc_info=True)

    # scrape data from categories link
    def data_collection_from_categories(self):
        try:
            list_of_products_details = []
            print(self.categories)
            for k,v in self.categories.items():
                for name, detail in v.items():
                    products_details = self.get_products(category_path = detail[1])
                    list_of_products_details += products_details
        except Exception as e:
            pass
        finally:
            print('driver got closed')
            if self.driver is not None:
                self.driver.quit()
                self.driver = None
            return list_of_products_details

    # handle the case if categories urls does not store yet
    def scrape_data(self):
        try:
            scrapped_data = []
            if len(self.categories) >0:
                scrapped_data = self.data_collection_from_categories()
            else:
                scrapped_data = self.get_products()
        except Exception as e:
            print(str(e))
        finally:
            return scrapped_data

    # save data in json
    def data_into_json(self,file_name, data):
        dump = json.dumps(data, indent=4)
        with open(f'{file_name}.json','a') as json_file:
            json_file.writelines(dump)
            json_file.close()


def main():
    # initialize our main class
    e_commerce_website = ECommerceWebsiteScrapping()

    # comment given line to extract data only for single url
    # collect_categories = e_commerce_website.get_deals_category()

    # will collect the data for all categories urls or pre_define url
    scrapped_data = e_commerce_website.scrape_data()

    # store data in csv file
    # store_data_in_csv = e_commerce_website.store_data_in_csv(f'Ebay_Products_{datetime.datetime.now().timestamp()}',scrapped_data)

    # store data in json file
    store_data_in_json = e_commerce_website.data_into_json(f'Ebay_Products_{datetime.datetime.now().timestamp()}',scrapped_data)

    # final results print here
    print('script executed..')


if __name__=="__main__":
    main()

