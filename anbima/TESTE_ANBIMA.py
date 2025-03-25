import http.client
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def generate_token():
    conn = http.client.HTTPSConnection("api.legalbot.com.br")
    payload = json.dumps({
        "username": "willian.lima@legalbot.com.br",
        "password": "Trymore1@3$5"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/sec/auth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token = json.loads(data.decode("utf-8"))["bearer"]
    return token

def request_platform_check(item, search_type="subject"):
    # Gerar o token de autenticação
    token = generate_token()
    conn = http.client.HTTPSConnection("api.legalbot.com.br")

    # Construir o payload com base no tipo de pesquisa
    if search_type == "subject":
        payload = json.dumps({
            "sort": [],
            "should": {},
            "must": {
                "subject": item  # Usar o item atual como o assunto
            },
            "must_not": {},
            "filter": {
                "term_filters": {
                    "origin": ["anbima"]
                }
            },
            "aggs": {
                "term_aggs": [
                    "origin",
                    "norm_type"
                ]
            },
            "themes": ""
        })
    elif search_type == "title":
        payload = json.dumps({
            "sort": [],
            "should": {},
            "must": {
                "title": item  # Usar o item atual como o título
            },
            "must_not": {},
            "filter": {
                "term_filters": {
                    "origin": ["anbima"]
                }
            },
            "aggs": {
                "term_aggs": [
                    "origin",
                    "norm_type"
                ]
            },
            "themes": ""
        })
    else:  # Último caso, buscar por palavra-chave em "q_short"
        payload = json.dumps({
            "sort": [],
            "should": {},
            "must": {
                "q_short": item  # Usar o item atual como palavra-chave
            },
            "must_not": {},
            "filter": {
                "term_filters": {
                    "origin": ["anbima"]
                }
            },
            "aggs": {
                "term_aggs": [
                    "origin",
                    "norm_type"
                ]
            },
            "themes": ""
        })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    # Fazer a requisição e processar a resposta
    conn.request("POST", "/norms/norms/search_count", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response_data = json.loads(data.decode("utf-8"))
    
    # Verificar se 'total' é maior que 0 e retornar 1 se presente, 0 caso contrário
    return 1 if response_data.get("total", 0) > 0 else 0

def requisitar_dados_anbima():
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

    # Fechar o navegador
    driver.quit()

    return dados

def limpar_texto(texto):
    # Remover conteúdo entre parênteses e conteúdo após hífen
    texto_sem_parenteses = re.sub(r"\s*\(.*?\)", "", texto).strip()  # Remove conteúdo entre parênteses
    texto_limpo = re.split(r"\s*-\s*", texto_sem_parenteses)[0]  # Remove conteúdo após hífen
    return texto_limpo

def verificar_itens_na_plataforma():
    # Obter dados da ANBIMA e limpar os textos
    dados_anbima = requisitar_dados_anbima()
    itens_nao_presentes = 0
    itens_ausentes = []  # Lista para armazenar os itens não encontrados

    # Verificar cada item na plataforma
    for item in dados_anbima:
        item_limpo = limpar_texto(item)  # Limpar o item removendo conteúdo entre parênteses e após hífen
        
        # Primeiro, tentar encontrar pelo "subject"
        resultado = request_platform_check(item_limpo, search_type="subject")
        
        # Se não encontrado pelo "subject", tentar pelo "title"
        if resultado == 0:
            resultado = request_platform_check(item_limpo, search_type="title")
        
        # Se ainda não foi encontrado, tentar pela palavra-chave "q_short"
        if resultado == 0:
            resultado = request_platform_check(item_limpo, search_type="q_short")
        
        # Se ainda não foi encontrado, considerar como ausente
        if resultado == 0:
            itens_nao_presentes += 1
            itens_ausentes.append(item)  # Adicionar o item à lista de ausentes

    # Retornar o número total e a lista de itens ausentes
    return itens_nao_presentes, itens_ausentes

if __name__ == "__main__":
    # Executar verificação e obter o número de itens ausentes e a lista dos itens
    itens_faltantes, lista_itens_ausentes = verificar_itens_na_plataforma()
    print(f"Número de itens da ANBIMA que não constam na plataforma: {itens_faltantes}")
    print("Itens ausentes:")
    for item in lista_itens_ausentes:
        print(f"- {item}")
