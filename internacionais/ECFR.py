from selenium import webdriver
import time

url = 'https://www.ecfr.gov/recent-changes?search%5Bdate%5D=current&search%5Bhierarchy%5D%5Btitle%5D=12'
js_script = 'return document.querySelector("body > div:nth-child(6) > div:nth-child(4) > div > div.row.recent-changes > div > h1:nth-child(1) > a").textContent'

driver = webdriver.Chrome()  # ou outro navegador de sua escolha
driver.get(url)

print("Aguardando a página carregar...")
time.sleep(5)  # espera por 5 segundos

print("Executando o script JavaScript...")
value = driver.execute_script(js_script)
print(value)

driver.quit()
