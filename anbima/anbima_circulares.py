from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import re

def anbima_circulares(data_desejada):
    # Configurar o WebDriver (utilizando o Chrome neste exemplo)
    driver = webdriver.Chrome()

    # Converter a data desejada para o tipo datetime
    try:
        data_desejada = datetime.strptime(data_desejada, '%d/%m/%Y').date()
    except ValueError as e:
        print(f"Erro ao converter a data: {e}")
        driver.quit()
        return 0

    # Navegar para a URL fornecida
    url = "https://www.anbima.com.br/pt_br/institucional/comunicados-oficiais/circulares/"
    driver.get(url)

    try:
        # Aguardar um tempo razoável para garantir que a página seja carregada completamente
        driver.implicitly_wait(10)

        # Definir o número máximo de iterações (páginas)
        max_iteracoes = 5

        # Contador para datas iguais à data desejada
        datas_iguais_desejada = 0

        for iteracao in range(max_iteracoes):
            # Aguardar a presença dos elementos usando WebDriverWait
            titulos_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#lista-circulares a'))
            )

            # Obter os textos dos elementos
            titulos = [element.text.strip() for element in titulos_elements]

            # Imprimir todos os títulos encontrados na página
            for titulo in titulos:
                # Verificar se a data está presente no texto
                data_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', titulo)
                if data_match:
                    data_string = data_match.group()
                    data_encontrada = datetime.strptime(data_string, "%d/%m/%Y").date()

                    # Comparar com a data desejada
                    if data_encontrada == data_desejada:
                        print(f"Requisição encontrada: {titulo}")  # Adicionado
                        datas_iguais_desejada += 1

            # Utilizar execute_script para clicar no botão de próxima página
            paginacao_js_path = '#Form_4028B88155A8219E0155A889F13B3AE1 > div.card-body.full.circulares > footer > div > div > ul > li:nth-child(8) > a'
            driver.execute_script(f'document.querySelector("{paginacao_js_path}").click();')

            # Aguardar 1 segundo antes de prosseguir para a próxima iteração
            time.sleep(1)

    except Exception as e:
        # Quando não houver mais páginas, a exceção ElementClickInterceptedException será levantada, indicando o final da paginação
        print("Final da paginação.")

    finally:
        # Fechar o navegador no final
        driver.quit()

        # Retornar o resultado final
        return datas_iguais_desejada

# Adicione esta linha no final do script
if __name__ == "__main__":
    data_desejada = "14/12/2023"  # Substitua com a data desejada
    resultado = anbima_circulares(data_desejada)
    print(f"circulares: {resultado}")
