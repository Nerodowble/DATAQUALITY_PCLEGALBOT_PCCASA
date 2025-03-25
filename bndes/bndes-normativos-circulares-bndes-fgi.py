import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do Selenium em modo headless
options = Options()
options.add_argument('--headless')  # Rodar em modo headless, sem abrir navegador
options.add_argument('--disable-gpu')  # Desabilitar aceleração de GPU também

# Configurar o serviço do ChromeDriver
service = Service(ChromeDriverManager().install())

# Iniciar o driver do Chrome
driver = webdriver.Chrome(service=service, options=options)

# URL alvo
url = "https://www.bndes.gov.br/wps/portal/site/home/financiamento/garantias/bndes-fgi/normativos-circulares-bndes-fgi"

# Abrir a página
driver.get(url)

# Extrair dados usando XPath
elementos = driver.find_elements(By.XPATH, '//*[(@id = "main")]//li')

# Preparar regex para encontrar datas no formato xx.xx.xxxx
pattern = r'\d{2}\.\d{2}\.\d{4}'
dates_found = []

# Buscar e imprimir apenas as datas encontradas
for elemento in elementos:
    text = elemento.text
    matches = re.findall(pattern, text)
    if matches:
        for match in matches:
            # Converte a data para o formato 'xx/xx/xxxx'
            formatted_date = match.replace('.', '/')
            dates_found.append(formatted_date)

# Imprimir resultados encontrados
for date in dates_found:
    print(date)

# Fechar o navegador
driver.quit()
