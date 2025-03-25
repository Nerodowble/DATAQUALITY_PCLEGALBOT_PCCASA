import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configurações do Selenium para rodar em modo headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Gerencia automaticamente o ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicializa o WebDriver
driver = webdriver.Chrome(service=service, options=options)

try:
    # Acessa a URL
    driver.get('https://www.bndes.gov.br/wps/portal/site/home/instituicoes-financeiras-credenciadas/normas/normas-operacoes-indiretas')
    
    # Encontra os elementos pelo XPath fornecido
    elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "titulo", " " ))]')
    
    # Extrai as datas das strings encontradas usando regex
    dates = []
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'  # padrão para datas dd.mm.aaaa
    
    for element in elements:
        text = element.text
        match = re.search(date_pattern, text)
        if match:
            # Converte a data para o formato 'xx/xx/xxxx'
            date = match.group().replace('.', '/')
            dates.append(date)
    
    # Imprime as datas convertidas
    for date in dates:
        print(date)
finally:
    # Fecha o WebDriver
    driver.quit()
