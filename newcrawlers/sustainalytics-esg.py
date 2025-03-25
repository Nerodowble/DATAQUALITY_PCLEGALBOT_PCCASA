import requests
from bs4 import BeautifulSoup
import datetime

def extract_data_from_page(soup, page_number):
    global total_items, data_list, error_list
    # Selecionando todos os itens
    items = soup.select("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div")

    # Extraindo os dados de cada item
    for item in items:
        try:
            titulo = item.select_one("div > div > div.card-body > p").get_text(strip=True)
            subtitulo = item.select_one("div > div > div.card-body > div").get_text(strip=True)
            tipo = item.select_one("div > div > div.card-footer > small").get_text(strip=True)
            url_artigo = item.select_one("div > div > div.card-footer > a")['href']
            
            # Aplicando a filtragem
            if tipo == 'Article':
                # Acessando a URL do artigo
                article_data = extract_data_from_article(url_artigo, page_number, titulo)

                # Agregando os dados
                item_data = {
                    'Titulo': titulo,
                    'Subtitulo': subtitulo,
                    'Tipo': tipo,
                    'URL': url_artigo,
                    'Data': article_data.get('Data', ''),
                    'Texto': article_data.get('Texto', '')
                }
                data_list.append(item_data)
                
                # Exibindo os dados
                print(f"Titulo: {titulo}")
                print(f"Subtitulo: {subtitulo}")
                print(f"Tipo: {tipo}")
                print(f"URL: {url_artigo}")
                print(f"Data: {item_data['Data']}")
                print(f"Texto: {item_data['Texto'][:100]}...")  # Exibindo apenas os primeiros 100 caracteres do texto
                print("-" * 50)
                
                total_items += 1
        except Exception as e:
            error_list.append({'page': page_number, 'title': titulo, 'url': url_artigo, 'error': str(e)})

def extract_data_from_article(url, page_number, titulo):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        error_list.append({'page': page_number, 'title': titulo, 'url': url, 'error': f"HTTP Status {response.status_code}"})
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    data_element = soup.select_one("#Contentplaceholder1_C013_Col01 > div.blog-post-detail-page-title.light > p")
    texto_element = soup.select_one("#Contentplaceholder1_C014_Col01 > div.sust-blog-post-detail-page")
    
    data = data_element.get_text(strip=True) if data_element else ''
    texto = texto_element.get_text(strip=True) if texto_element else ''

    # Tentar segundo seletor se o primeiro texto não for encontrado
    if not texto:
        texto_element_alternate = soup.select_one("#Contentplaceholder1_C265_Col00")
        texto = texto_element_alternate.get_text(strip=True) if texto_element_alternate else 'Texto not found'

    if not texto:
        error_list.append({'page': page_number, 'title': titulo, 'url': url, 'error': 'Missing text in article'})

    # Processar a data
    if data.startswith("Posted on"):
        data = data.replace("Posted on", "").strip()
        try:
            date_obj = datetime.datetime.strptime(data, "%B %d, %Y")
            data = date_obj.strftime("%d/%m/%Y")
        except ValueError as e:
            error_list.append({'page': page_number, 'title': titulo, 'url': url, 'error': f"Date format error: {str(e)}"})
            data = ''

    return {'Data': data, 'Texto': texto}

# Cabeçalhos para a requisição HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Número inicial da página
page_number = 1
total_items = 0
data_list = []
error_list = []

while True:
    # URL de destino para a página atual
    url = f"https://www.sustainalytics.com/esg-research/search/{page_number}?indexCatalogue=resource-center-blog-posts&searchQuery=ESG&orderBy=Relevance"
    
    # Fazendo a requisição
    response = requests.get(url, headers=headers)
    
    # Verifica se a requisição foi bem sucedida
    if response.status_code != 200:
        print(f"Falha ao recuperar a página {page_number}. Status code: {response.status_code}")
        break
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Verifica se existem itens na página
    items = soup.select("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div")
    if not items:
        print(f"Não há mais itens na página {page_number}. Encerrando a paginação.")
        break
    
    # Extrai os dados da página atual
    extract_data_from_page(soup, page_number)
    
    # Incrementa o número da página
    page_number += 1

print(f"Total de itens requisitados: {total_items}")
print(f"Total de erros: {len(error_list)}")

# Exibindo detalhes dos erros
if error_list:
    print("Detalhes dos erros:")
    for error in error_list:
        print(error)
