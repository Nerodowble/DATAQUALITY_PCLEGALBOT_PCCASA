import requests
from lxml import html
from datetime import datetime

# Função para converter a data
def convert_date(input_date):
    try:
        # Convertendo a data de dd/mm/yyyy para o formato Month d, yyyy
        date_obj = datetime.strptime(input_date, "%d/%m/%Y")
        # Removendo zero inicial do dia, se necessário
        day = date_obj.day
        return f"{date_obj.strftime('%B')} {day}, {date_obj.year}"
    except ValueError as e:
        print(f"Formato de data inválido: {e}")
        return None

# Função para processar uma página específica
def process_page(url, headers):
    # Realizando a requisição HTTP com os cabeçalhos
    response = requests.get(url, headers=headers)
    page_data = []

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Analisando o conteúdo HTML
        tree = html.fromstring(response.content)
        
        # XPath para o título
        title_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "entry-title", " " ))]//a'
        titles = tree.xpath(title_xpath)

        # XPath para o subtítulo
        subtitle_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "fusion-post-content-container", " " ))]//p'
        subtitles = tree.xpath(subtitle_xpath)

        # XPaths genéricos para a data
        date_xpaths = [
            '//*[contains(@id, "blog-1-post-")]/div[4]/div[1]/span[4]',
            '//*[contains(@id, "blog-1-post-")]/div[3]/div[1]/span[4]'
        ]
        dates = []
        for date_xpath in date_xpaths:
            dates.extend(tree.xpath(date_xpath))
        
        # Salvando os dados extraídos em uma lista
        for i in range(max(len(titles), len(subtitles), len(dates))):
            title = titles[i].text_content().strip() if i < len(titles) else "N/A"
            title_url = titles[i].get('href') if i < len(titles) else "N/A"
            subtitle = subtitles[i].text_content().strip() if i < len(subtitles) else "N/A"
            date = dates[i].text_content().strip() if i < len(dates) else "N/A"
            
            page_data.append({
                'title': title,
                'title_url': title_url,
                'subtitle': subtitle,
                'date': date
            })

        # XPath específico para o elemento "Next"
        next_xpath = '//a[contains(@class, "next")]/span[text()="Next"]'
        next_elements = tree.xpath(next_xpath)
        next_found = len(next_elements) > 0
        
        return page_data, next_found
    else:
        print(f"Erro ao acessar a URL: {response.status_code}")
        return page_data, False

# Função para processar a página de detalhes de um item
def process_detail_page(url, headers):
    # Realizando a requisição HTTP com os cabeçalhos
    response = requests.get(url, headers=headers)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Analisando o conteúdo HTML
        tree = html.fromstring(response.content)
        
        # XPath para os detalhes da categoria
        details_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "category-regulatory_matters", " " ))]'
        details = tree.xpath(details_xpath)
        
        # Extraindo e limpando o conteúdo dos detalhes
        detail_texts = [detail.text_content().strip() for detail in details]
        cleaned_texts = [text.replace("\n", " ").replace("\t", " ").strip() for text in detail_texts]
        return cleaned_texts
    else:
        print(f"Erro ao acessar a URL de detalhes: {response.status_code}")
        return []

# Cabeçalhos para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# URL base
base_url = "https://www.glasslewis.com/regulatory-matters/page/"

# Data alvo no formato dd/mm/yyyy
input_date = "04/03/2024"
target_date = convert_date(input_date)

if target_date:
    all_data = []
    page_number = 1
    next_found = True

    # Loop para paginar enquanto o elemento "Next" for encontrado
    while next_found:
        url = f"{base_url}{page_number}/"
        print(f"Processando página {page_number}...")
        page_data, next_found = process_page(url, headers)
        all_data.extend(page_data)
        page_number += 1

    # Pesquisando a data nos dados salvos e acessando os detalhes se encontrados
    found = False
    for data in all_data:
        if target_date == data['date']:
            print(f"Dado encontrado na data {target_date}:")
            print(f"Título: {data['title']}")
            print(f"URL do Título: {data['title_url']}")
            print(f"Subtítulo: {data['subtitle']}")
            print(f"Data: {data['date']}")
            
            # Acessando a URL de detalhes e extraindo informações adicionais
            details = process_detail_page(data['title_url'], headers)
            print(f"Detalhes: {details}")
            print("\n")
            found = True
    
    if not found:
        print(f"Nenhum item encontrado com a data {target_date}.")
else:
    print("Data alvo inválida fornecida.")
