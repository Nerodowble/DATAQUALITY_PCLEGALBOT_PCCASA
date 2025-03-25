from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re

# Configurações do Selenium para modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# Configuração do serviço do ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicializa o driver do Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL alvo
url = "https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/programa-emergencial-de-suporte-a-empregos"

try:
    # Abre a página
    driver.get(url)
    
    # Espera até que os elementos carreguem (opcional)
    driver.implicitly_wait(10)  # Ajuste conforme necessário

    # Encontra todos os elementos com base no XPath fornecido
    elements = driver.find_elements(By.XPATH, '//*[@id="main"]/div/ul[1]/li')

    # Lista para armazenar as datas convertidas
    datas_convertidas = []

    # Itera sobre os elementos encontrados
    for element in elements:
        # Extrai o texto do elemento
        text = element.text
        
        # Usa regex para encontrar a data no formato 'xx.xx.xxxx'
        match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
        if match:
            data = match.group()
            # Converte a data para o formato 'xx/xx/xxxx'
            data_convertida = data.replace('.', '/')
            datas_convertidas.append(data_convertida)

finally:
    # Fecha o driver
    driver.quit()

# Exibe as datas convertidas
for data in datas_convertidas:
    print(data)
