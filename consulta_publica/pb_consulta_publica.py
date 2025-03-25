import os
import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
from tqdm import tqdm

# Configuração do Selenium
def init_driver():
    options = Options()
    # Remova o comentário abaixo para executar sem interface gráfica
    # options.add_argument('--headless')
    service = Service(r"C:\Users\willi\OneDrive\Documentos\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(300)  # Timeout para carregamento da página
    driver.set_script_timeout(300)     # Timeout para execução de scripts
    return driver

# Carrega URLs e títulos da página principal
def get_urls(driver):
    base_url = "https://www.gov.br/participamaisbrasil/consultas-publicas"
    driver.get(base_url)
    time.sleep(2)

    # Variáveis para scroll
    scroll_pause_time = 0.5
    last_height = 0
    scroll_attempts = 0
    max_scroll_attempts = 20

    while scroll_attempts < max_scroll_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            last_height = new_height
            scroll_attempts = 0

    # Coleta URLs e títulos
    links = driver.find_elements(By.XPATH, '/html/body/div[4]/div[1]/main/div[2]/div/div[3]/div/div[1]/div/div/div[3]/div/a')
    titles = driver.find_elements(By.XPATH, '/html/body/div[4]/div[1]/main/div[2]/div/div[3]/div/div[1]/div/div/div[3]/div/a/div[2]/span')

    return [{"id": idx + 1, "title": title.text, "link": link.get_attribute("href"), "data": None} for idx, (title, link) in enumerate(zip(titles, links))]

# Extrai dados de uma URL
def extract_data(link_obj):
    for attempt in range(3):  # Tenta até 3 vezes
        try:
            driver = init_driver()
            url = link_obj["link"]
            driver.get(url)
            time.sleep(2)

            # XPaths primários e secundários
            xpaths_primary = {
                "Título": '/html/body/div[4]/div[1]/main/div[2]/div[1]/h1',
                "Órgão": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[1]',
                "Setor": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[2]',
                "Status": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[3]',
                "Abertura": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[4]',
                "Encerramento": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[5]',
                "Contribuições": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[6]',
                "Responsável": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[7]',
                "Contato": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[8]',
                "Texto": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[2]/div/div/div/div',
                "Contribuições Recebidas": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[3]/div/div/div/div/div/p',
            }
            xpaths_secondary = {
                "Título": '/html/body/div[4]/div[1]/main/div[2]/div[1]/h1',
                "Órgão": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[1]',
                "Setor": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[2]',
                "Status": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[3]',
                "Abertura": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[4]',
                "Encerramento": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[5]',
                "Processo": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[6]',
                "Contribuições": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[7]',
                "Responsável": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[8]',
                "Contato": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[1]/div/div/div/div/div/p[9]',
                "Texto": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[2]/div/div/div/div',
                "Contribuições Recebidas": '/html/body/div[4]/div[1]/main/div[2]/div[1]/div[3]/div[4]/div/div/div/div/div/p',
            }

            def try_extract(xpaths):
                data = {}
                for key, xpath in xpaths.items():
                    try:
                        data[key] = driver.find_element(By.XPATH, xpath).text
                    except:
                        data[key] = None
                return data

            data = try_extract(xpaths_primary)
            for key, value in data.items():
                if value is None:
                    data[key] = try_extract(xpaths_secondary).get(key)
            driver.quit()
            return {**link_obj, "data": data}

        except Exception as e:
            print(f"Erro no link {link_obj['link']} na tentativa {attempt + 1}: {e}")
            if attempt == 2:
                return {**link_obj, "data": None}

# Carrega JSON existente
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Salva JSON
def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Fluxo principal
if __name__ == "__main__":
    json_file = "consultas_publicas.json"
    existing_data = load_json(json_file)
    existing_links = {item["link"] for item in existing_data}

    # Carrega URLs da página principal
    driver = init_driver()
    all_links = get_urls(driver)
    driver.quit()

    # Filtra URLs ainda não processadas
    to_scrape = [link for link in all_links if link["link"] not in existing_links]

    # Scraping em paralelo
    with Pool(processes=4) as pool:
        new_data = list(tqdm(pool.imap(extract_data, to_scrape), total=len(to_scrape)))

    # Atualiza JSON com os novos dados
    combined_data = existing_data + new_data
    save_json(combined_data, json_file)

    # Exporta para Excel
    df = pd.DataFrame(combined_data)
    df.to_excel("consultas_publicas_completas.xlsx", index=False)

    print("Processo concluído!")
