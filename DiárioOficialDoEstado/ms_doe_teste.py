from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests

# Defina as datas aqui
data_inicial = "30/05/2024"
data_final = "05/06/2024"

# Configurações do Chrome para rodar em modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Inicialize o driver com as opções configuradas
driver = webdriver.Chrome(options=chrome_options)

# Função para converter tamanho do arquivo para uma string legível
def convert_file_size(file_size):
    if file_size < 1024:
        return f'{file_size} bytes'
    elif file_size < 1024 * 1024:
        return f'{file_size / 1024:.2f} KB'
    elif file_size < 1024 * 1024 * 1024:
        return f'{file_size / (1024 * 1024):.2f} MB'
    else:
        return f'{file_size / (1024 * 1024 * 1024):.2f} GB'

# Variável para armazenar os dados
dados = []

try:
    # Abra a URL
    driver.get("https://www.spdo.ms.gov.br/diariodoe")
    
    # Aguarde a página carregar completamente
    time.sleep(2)

    # Insira a data inicial
    data_inicial_input = driver.find_element(By.XPATH, '//*[@id="Filter_DataInicial"]')
    data_inicial_input.clear()
    data_inicial_input.send_keys(data_inicial)

    # Insira a data final
    data_final_input = driver.find_element(By.XPATH, '//*[@id="Filter_DataFinal"]')
    data_final_input.clear()
    data_final_input.send_keys(data_final)

    # Clique no botão de buscar
    buscar_button = driver.find_element(By.XPATH, '//*[@id="btnBuscar"]')
    buscar_button.click()

    # Aguarde os resultados carregarem
    time.sleep(2)

    # Extraia todos os títulos, datas e os IDs dos links de download
    rows = driver.find_elements(By.XPATH, '//*[@id="tbDiarios"]/tbody/tr')
    
    for row in rows:
        title_element = row.find_element(By.XPATH, 'td[1]/a')
        date_element = row.find_element(By.XPATH, 'td[2]')
        
        title = title_element.text
        date = date_element.text
        pdf_id = title_element.get_attribute('id')
        pdf_url = f'https://www.spdo.ms.gov.br/diariodoe/Index/Download/{pdf_id}'
        
        # Faça uma solicitação HEAD para obter o tamanho do arquivo
        response = requests.head(pdf_url)
        file_size = int(response.headers.get('Content-Length', 0))
        size_str = convert_file_size(file_size)
        
        # Armazene os dados em um dicionário
        dados.append({
            'title': title,
            'date': date,
            'pdf_url': pdf_url,
            'size_str': size_str
        })

finally:
    # Feche o driver
    driver.quit()

# Remover dados repetidos
dados_unicos = []
for item in dados:
    if item not in dados_unicos:
        dados_unicos.append(item)

# Imprimir os dados únicos
for dado in dados_unicos:
    print(f'Título: {dado["title"]}')
    print(f'Data: {dado["date"]}')
    print(f'URL do PDF: {dado["pdf_url"]}')
    print(f'Tamanho do PDF: {dado["size_str"]}')
    print('---')

# Imprimir a contagem total de dados únicos
print(f'Total de dados encontrados: {len(dados_unicos)}')
