from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Configura o webdriver
webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service)

try:
    # Navega até a página
    driver.get("https://www.dof.gob.mx/index.php#gsc.tab=0")

    # Obtém todos os links dentro da tabela relevante
    elements = driver.find_elements(By.XPATH, '//*[@id="tdcontent"]/table/tbody/tr/td[1]/table/tbody/tr/td[1]/table/tbody/tr/td/table[1]//td[3]/a')
    for element in elements:
        print(element.text)

finally:
    # Fecha o navegador
    driver.quit()
