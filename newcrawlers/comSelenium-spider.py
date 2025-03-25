# noinspection PyUnresolvedReferences
from items import NormItemLoader
from scrapy import Spider, Request
from scrapy.http import Response
# Selenium imports
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException

#A BAIXO SÃO AS FUNÇÕES PARA REALIZAR AS AÇÕES COMO 'parse_pdf_from_link' RETIRA O TEXTO DO PDF REFERENCIADO (URL)
from src.pdf_parser import 
# from src.text_work import get_num, get_date, get_norm_type_from_title

from datetime import datetime
import time
import re


# class ISS_Utils:
#     @staticmethod
#     def extract_date_from_pdf(text):
        
# Necessário mudar nome da spider
class ISS_Spider(Spider):
    pipeline = None
    #Mudar o nome conforme é informado no config.json
    name = "ISS_Governance"
    start_urls = [
        "https://www.issgovernance.com/policy-gateway/voting-policies/"
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
        self.wait = WebDriverWait(self.driver, 10)
        self.logger.debug("Initializing webdriver")
        super(ISS_Spider, self).__init__(*args, **kwargs)
        self.data_emissao = datetime.now().strftime('%d/%m/%Y')

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, callback=self.parse)

    def parse(self, response: Response, *args, **kwargs):
        self.logger.debug("Start parsing")
        self.driver.get("https://www.issgovernance.com/policy-gateway/voting-policies/")

        try:
            ### A BAIXO É EXEMPLO DE UM CLIQUE EM ALGUM BOTÃO COM SELENIUM ###
            # americas_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Americas"]')))
            # americas_tab.click()

            documents = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#list-32 > ul > li')))
            self.logger.debug(f"====> Found {len(documents)} documents")

            for doc in documents:
                try:
                    loader = NormItemLoader(selector=doc)

                    ### A BAIXO VAI OS XPATHS/SELECTORS DE ACORDO COM CADA ITEM QUE ENCONTRA-SE PARAMETRIZADO EM CONFIG.JSON ###

                    # titulo = doc.find_element(By.CSS_SELECTOR, 'a').text
                    # link = doc.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    # tipo = 'Voting Policy'
                    # texto = parse_pdf_from_link(self.name, link, link)
                    # assunto = texto[:1000]

                    # try:
                    #     extracted_date = ISS_Utils.extract_date_from_pdf(texto)
                    # except Exception as e:
                    #     self.logger.error(f"Error extracting date: {e}")
                    #     extracted_date = None

                    ### A BAIXO VAI AS CHAMADAS DOS XPATHS/SELECTORS PARA ENVIAR A SIRIUS ###

                    # # loader.add_value("origem", self.name)
                    # loader.add_value("origem", 'ISS')
                    # loader.add_value("titulo", titulo)
                    # loader.add_value("tipo", tipo)
                    # loader.add_value("numero", 'sn')
                    # loader.add_value("assunto", assunto)
                    # # loader.add_value("data_emissao", self.data_emissao)
                    # loader.add_value("data_emissao", extracted_date)
                    # loader.add_value("link", link)
                    # loader.add_value("texto", texto)

                    yield loader.load_item()

                except Exception as e:
                    self.logger.error(f"Error processing norma: {e}")

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            self.logger.error(f"An error occurred: {e}")

        finally:
            self.driver.quit()
            self.logger.debug("Finished parsing")



#REREFENCIA DE CHAMADAS:
#parse_pdf_from_link = Extrair o texto PDF referenciado, onde informando a URL, o PDF irá ser baixado, e o texto extraído.

#get_num = 

#get_date = 

#get_norm_type_from_title = Pega o TIPO do TÍTULO específicado. Ex de uso: tipo = loader.add_value("tipo", get_norm_type_from_title(titulo))
# onde ele vai tirar o TIPO da referencia do TITULO.
