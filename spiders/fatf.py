import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Caminho para o ChromeDriver
chromedriver_path = r"C:\Users\willi\OneDrive\Documentos\RE-FastscreenNovo\chromedriver-win64\chromedriver.exe"

def main(data_entrada_str, data_fim_str):
    # Configuração do ChromeDriver usando webdriver_manager
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar o navegador em modo headless (sem interface gráfica)
    
    # Iniciar o WebDriver com o caminho para o ChromeDriver
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    
    # Navegar para a URL especificada
    url = "https://www.fatf-gafi.org/en/publications.html"
    driver.get(url)
    
    # Converter as datas de entrada e fim para objetos datetime
    try:
        data_entrada = datetime.strptime(data_entrada_str, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:fatf")
        print("TOTAL_COUNT:0")
        driver.quit()
        return
    
    # Esperar até que os elementos estejam presentes na página
    try:
        # Esperar até 10 segundos para os elementos aparecerem
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#container-168f00070e > div > div.faceted-search.container.responsivegrid.aem-GridColumn.aem-GridColumn--default--10 > div > div.cmp-faceted-search__results > div > div > ul > li"))
        )
        
        # Encontrar todos os elementos que correspondem ao seletor CSS
        date_elements = driver.find_elements(By.CSS_SELECTOR, "#container-168f00070e > div > div.faceted-search.container.responsivegrid.aem-GridColumn.aem-GridColumn--default--10 > div > div.cmp-faceted-search__results > div > div > ul > li > div > div.cmp-search-results__result__content > p.cmp-search-results__result__date")
        
        # Extrair o texto de cada elemento e converter para datetime
        dates = []
        for date_element in date_elements:
            date_text = date_element.text.replace("Publication date :", "").strip()
            try:
                date = datetime.strptime(date_text, "%d %b %Y")
                dates.append(date)
            except ValueError:
                continue
        
        # Contar quantas datas estão dentro do intervalo especificado
        count = sum(data_entrada <= date <= data_fim for date in dates)
        
        # Exibir o resultado
        print("ORIGIN:fatf")
        print(f"TOTAL_COUNT:{count}")

    except Exception as e:
        print(f"Erro ao capturar as datas: {e}")
        print("ORIGIN:fatf")
        print("TOTAL_COUNT:0")

    # Fechar o WebDriver
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script_base.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:fatf")
        print("TOTAL_COUNT:0")
        sys.exit(1)
    
    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]
    
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:fatf")
        print("TOTAL_COUNT:0")
        sys.exit(1)
    
    main(data_inicio, data_fim)
