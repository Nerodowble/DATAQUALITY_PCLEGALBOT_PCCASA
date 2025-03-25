from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Crie uma instância das opções do Chrome
chrome_options = Options()

# Adicione a opção headless
# chrome_options.add_argument("--headless")

# Inicialize o driver do navegador com as opções especificadas (neste caso, estou usando o Chrome)
driver = webdriver.Chrome(options=chrome_options)

# Navegue até a URL
driver.get("https://www.cnbv.gob.mx/Paginas/NORMATIVIDAD.aspx")

# Aguarde a página carregar completamente
time.sleep(2)

# A data que você está pesquisando
search_date = "04/03/2024"

# Encontre o campo de entrada usando o novo xpath fornecido e insira a data
input_field = driver.find_element(By.XPATH, "//*[@id='normatividadTable_filter']/label/input")
input_field.send_keys(search_date)

# Pressione ENTER para iniciar a pesquisa
input_field.send_keys(Keys.RETURN)

# Aguarde os resultados da pesquisa serem carregados
time.sleep(5)

# Encontre todos os dados usando o xpath fornecido
data_elements = driver.find_elements(By.XPATH, "//td[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]")

# Contabilize quantos elementos foram encontrados
total_elements = len(data_elements)
print(f"Total de elementos encontrados: {total_elements}")

# Contabilize quantas datas correspondem à data que você está pesquisando
matching_dates = sum(1 for data in data_elements if data.text == search_date)
print(f"Total de datas correspondentes à data pesquisada ({search_date}): {matching_dates}")

# Feche o navegador
driver.quit()
