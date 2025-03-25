from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configurar o driver (certifique-se de ter o ChromeDriver instalado e configurado no PATH)
driver = webdriver.Chrome()

# URL alvo
url = "https://www.ibgc.org.br/blog/"

# Navegar para a URL
driver.get(url)

# Aguarde carregar o conteúdo (pode ajustar conforme necessário)
time.sleep(1.2)

# Requisição dos dados utilizando XPaths fornecidos
titulos = driver.find_elements(By.XPATH, '//*[(@id = "artigo")]//h2')
datas = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "subtitle", " " ))]')
subtitulos = driver.find_elements(By.XPATH, '//*[(@id = "artigo")]//p')
links = driver.find_elements(By.XPATH, '//*[(@id = "artigo")]//a')

# Data alvo para pesquisa
data_informada = "07/06/2024"

# Coletar dados em uma lista de dicionários
dados = []
for i in range(len(titulos)):
    dados.append({
        "Titulo": titulos[i].text,
        "Data": datas[i].text if i < len(datas) else '',
        "Subtitulo": subtitulos[i].text if i < len(subtitulos) else '',
        "Link": links[i].get_attribute('href') if i < len(links) else ''
    })

# Verificar se a data informada está nos dados coletados
dados_encontrados = None
for dado in dados:
    if dado["Data"] == data_informada:
        dados_encontrados = dado
        url_acessar = dado["Link"]
        break

# Fechar o navegador principal
driver.quit()

# Se a data informada for encontrada, acessar a URL correspondente e capturar o texto
if dados_encontrados:
    # Reabrir o navegador para acessar a URL correspondente
    driver = webdriver.Chrome()
    driver.get(url_acessar)

    # Aguarde carregar o conteúdo da nova página (pode ajustar conforme necessário)
    time.sleep(1.2)

    # Capturar os dados da nova página usando o XPath fornecido
    try:
        texto_capturado = driver.find_element(By.XPATH, '//*[@id="container"]/div[4]/div').text
        dados_encontrados["Texto"] = texto_capturado
    except Exception as e:
        print("Erro ao capturar o texto:", e)
        dados_encontrados["Texto"] = "Erro ao capturar o texto."

    # Fechar o navegador
    driver.quit()

    # Exibir os dados encontrados e o texto capturado
    print(f"Titulo: {dados_encontrados['Titulo']}")
    print(f"Data: {dados_encontrados['Data']}")
    print(f"Subtitulo: {dados_encontrados['Subtitulo']}")
    print(f"URL: {dados_encontrados['Link']}")
    print(f"Texto: {dados_encontrados['Texto']}")
    print("-" * 20)
else:
    print("Data informada não encontrada nos dados coletados.")

# # Exibir os dados coletados
# for dado in dados:
#     print(f"Titulo: {dado['Titulo']}")
#     print(f"Data: {dado['Data']}")
#     print(f"Subtitulo: {dado['Subtitulo']}")
#     print(f"Link: {dado['Link']}")
#     print("-" * 20)
