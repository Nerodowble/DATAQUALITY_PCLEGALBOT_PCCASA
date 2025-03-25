from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.options import Options

def anbima_atividades_conveniadas(data_desejada):
    # Configurar as opções do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Instanciar o driver do Selenium com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)
    # Abra a URL desejada
    url = "https://www.anbima.com.br/pt_br/autorregular/codigos/atividades-conveniadas.htm"
    driver.get(url)

    # Encontre os elementos usando o JS Path fornecido
    elements1 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028B88155DF7F5D0155DF82689E03E3_bibliotecas-interna > li > a > small"))')
    elements2 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028B88155DF7F5D0155DF826FB303E6_bibliotecas-interna > li > a > small"))')

    elements = elements1 + elements2

    # Inicialize o contador
    contador = 0

    # Verifique cada elemento
    for element in elements:
        # Obtenha o texto do elemento
        texto_elemento = element.text

        # Verifique se o texto do elemento é uma data
        try:
            data_elemento = datetime.strptime(texto_elemento, "%d/%m/%Y").strftime("%d/%m/%Y")

            # Compare a data do elemento com a data desejada
            if data_elemento == data_desejada:
                contador += 1
        except ValueError:
            pass

    # Feche o navegador
    driver.quit()

    # Retorna o contador
    return contador
