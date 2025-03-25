from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

def fetch_page_data(driver, button_xpath, data_xpaths):
    # Encontrar e clicar no botão
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        button.click()
    except Exception as e:
        print(f"Erro ao clicar no botão: {e}")
        return []

    # Esperar os dados da tabela carregar
    try:
        # XPath para todas as linhas da tabela
        rows_xpath = data_xpaths['rows']
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, rows_xpath))
        )

        # Extrair os dados das colunas especificadas
        rows = driver.find_elements(By.XPATH, rows_xpath)
        table_data = []
        for row in rows:
            try:
                cols = [row.find_elements(By.XPATH, col_xpath)[0].text for col_xpath in data_xpaths['cols']]
                table_data.append(tuple(cols))
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue
    except Exception as e:
        print(f"Erro ao extrair dados da tabela: {e}")
        table_data = []

    return table_data

def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    return date_obj.strftime("%d-%m-%Y")

def count_date_occurrences(data, target_date):
    count = 0
    for row in data:
        if target_date in row:
            count += 1
    return count

if __name__ == '__main__':
    url = 'http://www.ordenjuridico.gob.mx/leyes.php#gsc.tab=0'
    date_to_search = '24/04/1947'
    target_date = convert_date_format(date_to_search)
    print(f"Procurando pela data: {target_date}")

    # Setup do ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Abrir a URL
    driver.get(url)

    # Requisitar dados da primeira tabela
    button_xpath_1 = '//*[(@id = "myTable")]//td[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//button'
    data_xpaths_1 = {
        'rows': '//*[@id="myTable"]/tbody/tr',
        'cols': ['./td[3]', './td[4]']
    }
    data_1 = fetch_page_data(driver, button_xpath_1, data_xpaths_1)
    print("Dados da primeira tabela:")
    for item in data_1:
        print(item)

    # Requisitar dados da segunda tabela
    button_xpath_2 = '//*[@id="myTable"]/tbody/tr[2]/td[2]/div/a/button'
    data_xpaths_2 = {
        'rows': '//*[@id="myTabla"]/tbody/tr',
        'cols': ['./td[3]', './td[4]', './td[5]']
    }
    data_2 = fetch_page_data(driver, button_xpath_2, data_xpaths_2)
    print("Dados da segunda tabela:")
    for item in data_2:
        print(item)

    # Fechar o navegador
    driver.quit()

    # Comparar data informada com os dados extraídos
    occurrences_1 = count_date_occurrences(data_1, target_date)
    occurrences_2 = count_date_occurrences(data_2, target_date)
    total_occurrences = occurrences_1 + occurrences_2
    print(f"A data {target_date} aparece {total_occurrences} vezes.")
