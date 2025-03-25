from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Configuração do WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Executa o Chrome em modo headless
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")
options.add_argument("start-maximized")

# Simulação de um user agent humano
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')

# Iniciando o WebDriver
driver = webdriver.Chrome(options=options)
driver.get("https://www.gov.ky/noticeboard#start_date=2023-09-01;end_date=2024-07-30;categories=676034306")

# Espera para garantir que a página carregue
time.sleep(4)  # Aguarde 4 segundos para garantir que a página e todos os elementos carreguem

# Tentando acessar os elementos de cookies com XPath
try:
    # Cookies funcionais
    functional_cookies_xpath = "/html/body/div[8]/div[1]/div/div/div[2]/div/div/div[2]/div[3]/div/div[2]/div/div/div[3]/span[2]/label"
    functional_cookies_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, functional_cookies_xpath))
    )
    driver.execute_script("arguments[0].click();", functional_cookies_button)
    print("Cookies funcionais aceitos.")
    
    # Cookies de publicidade
    advertising_cookies_xpath = "/html/body/div[8]/div[1]/div/div/div[2]/div/div/div[2]/div[3]/div/div[3]/div/div/div[3]/span[2]/label"
    advertising_cookies_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, advertising_cookies_xpath))
    )
    driver.execute_script("arguments[0].click();", advertising_cookies_button)
    print("Cookies de publicidade aceitos.")
    
    # Botão de aceitação final
    accept_all_xpath = "/html/body/div[8]/div[1]/div/div/div[2]/div/div/div[3]/div/button[1]"
    accept_all_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, accept_all_xpath))
    )
    driver.execute_script("arguments[0].click();", accept_all_button)
    print("Todos os cookies aceitos.")
    
    # Pausa aleatória após aceitar os cookies para simular comportamento humano
    time.sleep(random.uniform(2, 4))
except Exception as e:
    print(f"Erro ao aceitar os cookies: {e}")

# Tentando encontrar o elemento pelo seletor CSS fornecido
try:
    # Espera o elemento estar presente na página
    event_details = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#timely-event-list-77214146-20231129083000 > div.timely-stream-event-details > div.timely-stream-event-date"))
    )
    # Extraindo o texto do elemento
    event_date_text = event_details.text
    print("Data do Evento:", event_date_text)
    
except Exception as e:
    print(f"Erro ao encontrar o elemento: {e}")

# Fechando o WebDriver
driver.quit()
