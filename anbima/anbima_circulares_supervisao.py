from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options

def anbima_circulares_supervisao(data_desejada):
    # Inicializa o navegador (certifique-se de ter o webdriver no seu PATH)
    # Configurar as opções do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Instanciar o driver do Selenium com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)

    # Abre a página desejada
    url = "https://www.anbima.com.br/pt_br/autorregular/supervisao/circulares-de-supervisao/"
    driver.get(url)

    # Espera o conteúdo dinâmico ser carregado (pode ser necessário ajustar o tempo)
    driver.implicitly_wait(10)

    # Define o seletor do botão de próxima página
    pagination_selector = "#Form_8A488AF057C002FA0157C4B5E1B66DA7 > div.card-body.full.circulares > footer > div > div > ul > li:nth-child(5) > a"

    # Define o número de vezes que você deseja paginar
    num_paginations = 1

    # Inicializa um contador para contabilizar as datas iguais à data desejada
    count_desired_date = 0

    # Loop para clicar no botão de próxima página o número desejado de vezes
    for _ in range(num_paginations):
        # Executar o script JavaScript para clicar no botão de próxima página
        driver.execute_script(f'document.querySelector("{pagination_selector}").click();')

        # Esperar o conteúdo ser carregado (pode ser necessário ajustar o tempo)
        time.sleep(3)

        # Extrair os textos da página
        elements = driver.find_elements(By.CSS_SELECTOR, "#lista-circulares > div > div > small > a")
        for element in elements:
            date_text = element.text.split('-')[-1].strip()
            # Converte a data do formato de texto para um objeto datetime
            date_obj = datetime.strptime(date_text, '%d/%m/%Y')
            # Compara se a data do elemento é igual à data desejada
            if date_obj.date() == data_desejada:
                count_desired_date += 1

    # Fecha o navegador
    driver.quit()

    # Retorna o contador
    return count_desired_date
