from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.options import Options

def anbima_servicos_qualificados(data_desejada):
    # Configurar as opções do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Instanciar o driver do Selenium com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)
    
    # Converter a data desejada para o tipo datetime
    try:
        data_desejada = datetime.strptime(data_desejada, '%d/%m/%Y')
    except ValueError as e:
        print(f"Erro ao converter a data: {e}")
        driver.quit()
        return 0

    # Abra a URL desejada
    url = "https://www.anbima.com.br/pt_br/autorregular/codigos/servicos-qualificados.htm"
    driver.get(url)

    # Encontre os elementos usando os JS Paths fornecidos
    elements1 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028B88155DF85870155DF869DA402CB_bibliotecas-interna > li > a > small"))')
    elements2 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028B88155DF85870155DF8697C302C0_bibliotecas-interna > li > a > small"))')

    # Combine as listas de elementos
    elements = elements1 + elements2

    # Inicialize o contador
    contador_desired_date = 0

    # Compare cada data com a data desejada e atualize o contador
    for element in elements:
        # Obtenha o texto do elemento
        texto_elemento = element.text

        # Verifique se o texto do elemento é uma data
        try:
            data_elemento = datetime.strptime(texto_elemento, "%d/%m/%Y")

            # Compare a data do elemento com a data desejada
            if data_elemento == data_desejada:
                contador_desired_date += 1
        except ValueError:
            pass

    # Feche o navegador
    driver.quit()

    # Retorna o contador
    return contador_desired_date

# Adicione esta linha no final do script
if __name__ == "__main__":
    data_desejada = "14/12/2023"  # Substitua com a data desejada
    resultado = anbima_servicos_qualificados(data_desejada)
    print(f"servicos_qualificados: {resultado}")
