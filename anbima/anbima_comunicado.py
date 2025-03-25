from datetime import datetime
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options

def anbima_comunicado(data_desejada):
    # Converta a string data_desejada para um objeto datetime
    data_desejada = datetime.strptime(data_desejada, '%d/%m/%Y')
    # Inicialize o driver do navegador (neste caso, Chrome)
    # Configurar as opções do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Instanciar o driver do Selenium com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)

    # Inicialize a lista de datas
    datas = []

    # Abra a URL
    driver.get('https://www.anbima.com.br/pt_br/autorregular/comunicados/')

    # Paginação 5 vezes
    for _ in range(5):
        # Execute o JS Path para obter todos os dados
        datas_pagina = driver.execute_script('''
            var datas = [];
            for (var i = 1; i <= 5; i++) {
                var data = document.querySelector("#dt" + i);
                if (data) {
                    datas.push(data.innerText);
                }
            }
            return datas;
        ''')
        
        # Adicione as datas à lista de datas
        datas.extend(datas_pagina)
        
        # Execute o JS Path para clicar no botão de paginação
        driver.execute_script('document.querySelector("#Form_4028B881565BE00401565C1F8AB83883 > div.card-body.full.comunicados > footer > div > div > ul > li:nth-child(8) > a").click()')
        
        # Aguarde um pouco para a página carregar
        time.sleep(2)

    # Feche o navegador
    driver.quit()

    # Inicialize o contador
    contador = 0

    # Compare cada data com a data desejada e atualize o contador
    for data_elemento in datas:
        if data_elemento == data_desejada.strftime('%d/%m/%Y'):
            contador += 1

    # Retorna o contador
    resultado = contador
    return resultado