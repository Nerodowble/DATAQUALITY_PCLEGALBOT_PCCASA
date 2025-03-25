from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
import sys
import re

# Caminho para o ChromeDriver
chromedriver_path = r"C:\Users\willi\OneDrive\Documentos\RE-FastscreenNovo\chromedriver-win64\chromedriver.exe"

# Função para configurar e iniciar o driver do Selenium
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless (sem interface gráfica)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Simula uma janela de tamanho normal
    driver.set_window_size(1920, 1080)
    return driver

# Função para pesquisar uma data específica
def search_date(driver, search_date):
    driver.get("https://www.cnbv.gob.mx/Paginas/NORMATIVIDAD.aspx")
    time.sleep(2)  # Aguarde a página carregar completamente

    input_field = driver.find_element(By.XPATH, "//*[@id='normatividadTable_filter']/label/input")
    input_field.clear()  # Limpar o campo de entrada antes de inserir a nova data
    input_field.send_keys(search_date)
    input_field.send_keys(Keys.RETURN)
    time.sleep(5)  # Aguarde os resultados da pesquisa serem carregados

    data_elements = driver.find_elements(By.XPATH, "//td[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]")
    matching_dates = sum(1 for data in data_elements if data.text == search_date)
    return matching_dates

# Função principal que itera sobre o intervalo de datas e acumula o total de itens
def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:cnbv")
        print("TOTAL_COUNT:0")
        return

    driver = init_driver()  # Inicializa o driver do navegador
    total_count = 0  # Inicializa a contagem total

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%Y")
        count = search_date(driver, date_str)
        total_count += count
        current_date += timedelta(days=1)

    driver.quit()  # Fecha o navegador

    # Imprime a origem e a contagem total, no formato esperado pelo script pai
    print("ORIGIN:cnbv")
    print(f"TOTAL_COUNT:{total_count}")

# Ponto de entrada do script
if __name__ == "__main__":
    if len(sys.argv) != 3:  # Verifica se o número de argumentos é correto
        print("Uso: python script_cnbv.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:cnbv")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    data_inicio = sys.argv[1]  # Obtém a data de início dos argumentos
    data_fim = sys.argv[2]  # Obtém a data de fim dos argumentos
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):  # Verifica o formato das datas
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:cnbv")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    main(data_inicio, data_fim)  # Chama a função principal com as datas fornecidas
