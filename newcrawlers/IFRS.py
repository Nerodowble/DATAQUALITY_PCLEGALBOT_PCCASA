import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar o navegador em modo headless
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Adiciona cabeçalhos personalizados
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Configura o WebDriver Manager para gerenciar o ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicia o navegador
driver = webdriver.Chrome(service=service, options=chrome_options)

# Lista para armazenar os dados extraídos
extracted_data = []

try:
    # Acessa a URL inicial
    driver.get("https://www.ifrs.org/issued-standards/list-of-standards/ifrs-17-insurance-contracts.html/content/dam/ifrs/publications/html-standards/english/2024/issued/ifrs17/#news")
    
    # Aceita os cookies
    try:
        accept_cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cc-accept-cookies"]')))
        accept_cookies.click()
        print("Cookies aceitos.")
    except:
        print("Não foi possível encontrar o botão de aceitar cookies.")
    
    # Espera até que os elementos de título estejam presentes
    try:
        title_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="news_table"]/tbody/tr/td[3]/a'))
        )
        print("Elementos de título encontrados.")
    except:
        print("Não foi possível encontrar os elementos de título.")
    
    # Extrai os textos dos títulos e suas URLs
    titles_and_urls = [(title.text, title.get_attribute('href')) for title in title_elements]
    
    # Exibe os resultados
    for title, url in titles_and_urls:
        print(f"Title: {title}, URL: {url}")
        
        # Abre cada URL e extrai os dados usando os seletores XPath fornecidos
        driver.get(url)
        
        try:
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "col-md-8", " " ))] | //*[contains(concat( " ", @class, " " ), concat( " ", "font-weight-bold", " " ))] | //*[contains(concat( " ", @class, " " ), concat( " ", "header-publish-date", " " ))]'))
            )
            data_texts = [element.text for element in elements]
            print(f"Data from {url}: {data_texts}")
            
            # Armazena os dados extraídos
            extracted_data.append({
                "title": title,
                "url": url,
                "data": data_texts
            })
        except:
            print(f"Não foi possível encontrar os elementos na URL: {url}")

finally:
    # Fecha o navegador
    driver.quit()

# Salva os dados extraídos em um arquivo JSON
with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted_data, f, ensure_ascii=False, indent=4)

print("Dados salvos em extracted_data.json")
