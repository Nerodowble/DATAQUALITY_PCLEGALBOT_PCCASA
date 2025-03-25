import aiohttp
import asyncio
from lxml import html
from datetime import datetime
import http.client
import json
import sys
import re

# Função para gerar o token
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

# Função para buscar contagem por título
def request_counts_by_title(titles):
    token = generate_token()
    conn = http.client.HTTPSConnection("api.legalbot.com.br")
    results = {}
    origin = "cvm"

    for title in titles:
        payload = json.dumps({
            "sort": [],
            "should": {},
            "must": {
                "title": title
            },
            "must_not": {},
            "filter": {
                "term_filters": {
                    "origin": [origin]
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
        print(f"Requesting count for title: {title}")  # Depuração
        print(f"Payload: {payload}")  # Depuração
        conn.request("POST", "/norms/norms/search_count", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))
        print(f"Response for {title}: {response_data}")  # Depuração
        total = response_data.get("total", 0)
        results[title] = 1 if total > 0 else 0

    return results, origin

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Erro ao acessar {url}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"Erro ao buscar URL {url}: {e}")
            return None

async def get_cvm_article_data(url):
    page_content = await fetch(url)
    item_count = 0
    if page_content:
        tree = html.fromstring(page_content)
        articles = tree.xpath('//article')
        for article in articles:
            try:
                title_element = article.xpath('.//h3/a')[0]
                title = title_element.text.strip()
                link = title_element.get('href')
                full_link = f"https://conteudo.cvm.gov.br{link}" if link.startswith('/') else link
                
                subtitle = article.xpath('.//div[@class="contentDesc"]/text()')[0].strip()
                date = article.xpath('.//div[@class="infoItem"]/p[b/text()="Data:"]/text()')[0].strip()
                tipo = article.xpath('.//div[@class="infoItem"]/p[b/text()="Tipo:"]/text()')[0].strip()
                
                item_count += 1
            except IndexError as e:
                print(f"Erro ao processar artigo: {e}")
                continue

    return item_count

async def get_gov_article_data(url):
    page_content = await fetch(url)
    item_count = 0
    if page_content:
        tree = html.fromstring(page_content)
        titles = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "titulo", " " ))]//a')
        dates = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "data", " " ))]')
        subtitles = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "descricao", " " ))]')
        types = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "subtitulo-noticia", " " ))]')
        
        for i in range(len(titles)):
            try:
                title_element = titles[i]
                title = title_element.text.strip()
                link = title_element.get('href')
                full_link = f"https://www.gov.br{link}" if link.startswith('/') else link
                
                date = dates[i].text.strip() if i < len(dates) else "N/A"
                subtitle = subtitles[i].text.strip() if i < len(subtitles) else "N/A"
                tipo = types[i].text.strip() if i < len(types) else "N/A"
                
                item_count += 1
            except IndexError as e:
                print(f"Erro ao processar artigo: {e}")
                continue

    return item_count

async def get_audiencia_publica_data(url):
    page_content = await fetch(url)
    titles = []
    if page_content:
        tree = html.fromstring(page_content)
        title_elements = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "link", " " ))]')
        subtitles = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "table-bordered", " " ))]//p[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]')
        
        for i in range(len(title_elements)):
            try:
                title = title_elements[i].text.strip()

                # Verificação adicional para garantir que subtitle[i] não seja None
                subtitle_element = subtitles[i] if i < len(subtitles) else None
                subtitle = subtitle_element.text.strip() if subtitle_element is not None and subtitle_element.text is not None else "N/A"
                
                titles.append(title)
                print(f"Title found: {title}")  # Depuração
            except IndexError as e:
                print(f"Erro ao processar artigo: {e}")
                continue

    print(f"Total titles found: {len(titles)}")  # Depuração
    return titles

def create_url(base_url, start_date, end_date):
    start_date_str = start_date.strftime("%d/%m/%Y")
    end_date_str = end_date.strftime("%d/%m/%Y")
    return f"{base_url}&dataInicio={start_date_str}&dataFim={end_date_str}"

def create_gov_url(base_url, start_date, end_date):
    start_date_str = start_date.strftime("%d/%m/%Y")
    end_date_str = end_date.strftime("%d/%m/%Y")
    return f"{base_url}?form.submitted=1&texto=&dt_inicio={start_date_str}&dt_fim={end_date_str}&categoria="

async def main(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    
    cvm_url = create_url("https://conteudo.cvm.gov.br/legislacao/index.html?numero=&lastNameShow=&lastName=&filtro=todos&buscado=false&contCategoriasCheck=7", start_date, end_date)
    gov_url = create_gov_url("https://www.gov.br/cvm/pt-br/assuntos/noticias", start_date, end_date)
    audiencia_url = "https://conteudo.cvm.gov.br/audiencias_publicas/"
    
    cvm_item_count = await get_cvm_article_data(cvm_url)
    gov_item_count = await get_gov_article_data(gov_url)
    audiencia_titles = await get_audiencia_publica_data(audiencia_url)
    
    # Contagem inicial dos itens encontrados
    total_count = cvm_item_count + gov_item_count
    print(f"Total initial count: {total_count}")  # Depuração
    print(f"Audiencia titles: {audiencia_titles}")  # Depuração

    if audiencia_titles:
        # Integrando as funções de token e contagem por títulos
        title_counts, origin = request_counts_by_title(audiencia_titles)
        print(f"Contagem por título: {title_counts}")
        # Incrementar o total_count com base nos valores de title_counts
        total_count += sum(value for value in title_counts.values() if value == 1)
    else:
        print("Nenhuma audiência pública encontrada.")  # Depuração
        title_counts = {}
        origin = "cvm"

    # Imprimindo a origem e o total_count para serem capturados pelo script main.py
    print(f"ORIGIN:{origin}")
    print(f"TOTAL_COUNT:{total_count}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python cvm.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:cvm")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    
    if not re.match(r"\d{2}/\d{2}/\d{4}", start_date_str) or not re.match(r"\d{2}/\d{2}/\d{4}", end_date_str):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:cvm")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    asyncio.run(main(start_date_str, end_date_str))
