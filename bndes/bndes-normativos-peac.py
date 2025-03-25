from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re  # Importando o módulo de expressões regulares

# Configurações do Chrome para executar em modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# Inicialização do driver do Chrome
driver = webdriver.Chrome(options=chrome_options)

# URL alvo
url = "https://www.bndes.gov.br/wps/portal/site/home/financiamento/garantias/peac/normativos-peac"

# Acessa a página
driver.get(url)

# Localiza os elementos <li> dentro do elemento com ID "main"
elementos_li = driver.find_elements(By.XPATH, "//*[(@id = 'main')]//li")

# Expressão regular para extrair data no formato xx.xx.xxxx
data_regex = r'\d{2}\.\d{2}\.\d{4}'

# Extrai o texto de cada elemento <li> e extrai as datas
datas = []
for elemento in elementos_li:
    texto = elemento.text.strip()  # Remove espaços em branco antes e depois do texto
    
    # Extrai a data usando expressão regular
    data_match = re.search(data_regex, texto)
    if data_match:
        data = data_match.group(0)
        # Converte a data para o formato xx/xx/xxxx
        data_convertida = data.replace('.', '/')
        datas.append(data_convertida)

# Encerra o driver
driver.quit()

# Exibir as datas encontradas
for data in datas:
    print(data)
