from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
import sys
import re

# Caminho para o ChromeDriver
chromedriver_path = r"C:\Users\willi\OneDrive\Documentos\RE-FastscreenNovo\chromedriver-win64\chromedriver.exe"

def fetch_page(url):
    # Configuração do ChromeDriver usando webdriver_manager
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar o navegador em modo headless (sem interface gráfica)
    
    # Iniciar o WebDriver com o caminho para o ChromeDriver
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    
    # Navegar para a URL especificada
    driver.get(url)
    
    # Esperar um tempo para garantir que a página carregue completamente
    time.sleep(5)
    
    # Extrair os dados usando o seletor CSS fornecido
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "#tdcontent > table > tbody > tr > td:nth-child(1) > table > tbody > tr > td:nth-child(1) > table > tbody > tr > td > table:nth-child(1) > tbody > tr > td:nth-child(3) > a")
        data = [element.text.strip() for element in elements]
        return data
    except Exception as e:
        print(f"Erro ao acessar a URL {url}: {e}")
        return []
    finally:
        driver.quit()

def count_items_in_date_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

    total_count = 0
    current_date = start_date

    while current_date <= end_date:
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')
        
        url = f"https://www.dof.gob.mx/index_111.php?year={year}&month={month}&day={day}#gsc.tab=0"
        data = fetch_page(url)
        total_count += len(data)
        
        current_date += timedelta(days=1)
    
    return total_count

def main():
    if len(sys.argv) != 3:
        print("Uso: python mxdof.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:mxdof")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]

    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:mxdof")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    total_count = count_items_in_date_range(data_inicio, data_fim)
    print("ORIGIN:mxdof")
    print(f"TOTAL_COUNT:{total_count}")

if __name__ == '__main__':
    main()
