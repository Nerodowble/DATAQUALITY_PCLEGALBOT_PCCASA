import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL alvo
url = 'https://www.glasslewis.com/voting-policies-current/'

# Cabeçalhos para imitar uma requisição de navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fazer a requisição para a URL com os cabeçalhos
response = requests.get(url, headers=headers)

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    # Conteúdo HTML da página
    html_content = response.text
    
    # Parser do HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Procurar pelo elemento <h3> que contém "Brazil"
    brazil_section = soup.find('h3', string='Brazil')
    
    if brazil_section:
        # Procurar pela URL associada
        parent_div = brazil_section.find_parent('div', class_='fusion-column-wrapper')
        link_tag = parent_div.find('a', href=True) if parent_div else None
        if link_tag:
            # Obter a data atual
            current_date = datetime.now().strftime("%Y-%m-%d")
            # Formatar o título
            title = f"Glass Lewis - {current_date} - Brazil"
            url = link_tag['href']
            
            # Exibir a informação no terminal
            print(f"Título: {title}")
            print(f"URL: {url}")
        else:
            print("URL associada ao 'Brazil' não encontrada.")
    else:
        print("Seção 'Brazil' não encontrada.")
else:
    print(f"Falha na requisição. Status code: {response.status_code}")
