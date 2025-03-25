# noinspection PyUnresolvedReferences
from items import NormItemLoader
from scrapy import Spider, Request
from scrapy.http import Response
#Selenium imports
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from src.pdf_parser import parse_pdf_from_link
from src.text_work import get_num, get_date, get_norm_type_from_title
import time
import re



# class BlaBla_Utils:
#     @staticmethod




class BlaBla_Spider(Spider):
    pipeline = None
    name = "usar o nome da origem da base"
    start_urls = [
        "url"
    ]


    def __init__(self, *args, **kwargs):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("start-maximized")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.logger.debug("Initializing webdriver")
        super(SP_LeisMunicipais_Spider, self).__init__(*args, **kwargs)


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, callback=self.parse)


    def parse(self, response: Response, *args, **kwargs):
        self.logger.debug("Start parsing")
        self.driver.get("url")

        try:
            count = 0
            while count < 1:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "bla")))

                normas = self.driver.find_elements(By.CSS_SELECTOR, "bla")
                self.logger.debug(f"====> Found {len(normas)} norms")
            
                for norma in normas:
                    try:
                        loader = NormItemLoader(selector=norma)
                    
                        titulo = norma.find_element(By.CSS_SELECTOR, 'bla').text
                        data_emissao = norma.find_element(By.CSS_SELECTOR, 'bla').text
                        assunto = norma.find_element(By.CSS_SELECTOR, 'bla').text
                        link = norma.find_element(By.CSS_SELECTOR, 'td:nth-child(1)').find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
                        texto = parse_pdf_from_link(self.name, link, link)


                        loader.add_value("origem", self.name)
                        loader.add_value("titulo", titulo)
                        loader.add_value("data_emissao", data_emissao)
                        loader.add_value("assunto", assunto)
                        loader.add_value("link", link)
                        loader.add_value("texto", texto)
                        loader.add_value("tipo", get_norm_type_from_title(titulo))
                        loader.add_value("numero", get_num(titulo))

                        yield loader.load_item()

                    except Exception as e:
                        self.logger.error(f"Error processing norma: {e}")

                count += 1
                try:
                    next_page_button = self.driver.find_element(By.CSS_SELECTOR, "bla")
                    next_page_button.click()
                    self.wait.until(EC.staleness_of(normas[0]))
                except NoSuchElementException:
                    self.logger.debug("No more pages")
                    break


        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            self.logger.error(f"An error occurred: {e}")

        self.driver.quit()
        self.logger.debug("Finished parsing")
