from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os

def anbima_administracao_de_recursos_de_terceiros():
    # Inicializar o WebDriver (certifique-se de ter o driver adequado instalado)
    # Configurar as opções do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Instanciar o driver do Selenium com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)

    # Abrir a URL desejada
    url = "https://www.anbima.com.br/pt_br/autorregular/codigos/administracao-de-recursos-de-terceiros.htm"
    driver.get(url)

    # Encontrar os elementos usando o JS Path fornecido
    elements1 = driver.execute_script('return Array.from(document.querySelectorAll("#N_402880DC6340DBD40163418E6DD21950_bibliotecas-interna > li > a > p"))')
    elements2 = driver.execute_script('return Array.from(document.querySelectorAll("#N_402880DC6340DBD401634138AD160414_bibliotecas-interna > li > a > p"))')
    elements3 = driver.execute_script('return Array.from(document.querySelectorAll("#N_2C9B6A8163401DB0016340705B1F1DB1_bibliotecas-interna > li > a > p"))')
    elements4 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028D6388A610D47018A61DBA19C0AB0_bibliotecas-interna > li > a > p"))')
    elements5 = driver.execute_script('return Array.from(document.querySelectorAll("#N_4028D6388A610D47018A61FFBBFF0C6C_bibliotecas-interna > li > a > p"))')

    elements = elements1 + elements2 + elements3 + elements4 + elements5

    # Converter os elementos em uma lista de strings
    dados = [element.text for element in elements]

    # Verificar se o arquivo JSON já existe
    arquivo_json = "anbima_administracao_de_recursos_de_terceiros.json"
    if os.path.exists(arquivo_json):
        # Se o arquivo existir, carregar os dados
        with open(arquivo_json, "r") as arquivo:
            dados_json = json.load(arquivo)
    else:
        # Se o arquivo não existir, criar um novo arquivo com os dados atuais
        with open(arquivo_json, "w") as arquivo:
            json.dump(dados, arquivo)
        return 0

    # Verificar se algum dado na próxima requisição é diferente dos dados no arquivo JSON
    diferencas = 0
    novos_dados = []
    for dado in dados:
        if dado not in dados_json:
            diferencas += 1
            novos_dados.append(dado)

    # Se houver diferenças, adicionar os novos dados ao arquivo JSON
    if diferencas > 0:
        dados_json.extend(novos_dados)
        with open(arquivo_json, "w") as arquivo:
            json.dump(dados_json, arquivo)

    # Fechar o navegador
    driver.quit()

    # Retornar o número total de diferenças encontradas
    return diferencas

# Exemplo de uso
total_diferencas = anbima_administracao_de_recursos_de_terceiros()
print(f"Total de diferenças encontradas: {total_diferencas}")
