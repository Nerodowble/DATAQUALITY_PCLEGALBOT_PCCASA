import requests
from lxml import html
from datetime import datetime

# URL do site
url = "https://www.fatf-gafi.org/en/the-fatf/news.html"

def fetch_news_dates(url):
    # Realizar a requisição GET
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Parsear o conteúdo HTML da página
        tree = html.fromstring(response.content)
        
        # XPath para selecionar os itens desejados
        xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "date", " " ))]'
        
        # Extrair os elementos usando o XPath
        elements = tree.xpath(xpath)
        
        # Extrair e retornar o texto de cada elemento
        dates = [element.text_content().strip() for element in elements]
        return dates
    else:
        print(f"Erro na requisição: {response.status_code}")
        return []

def count_date_occurrences(dates, target_date):
    # Contar o número de ocorrências da data especificada
    count = dates.count(target_date)
    return count

def main():
    # Data a ser pesquisada no formato brasileiro
    date_to_search = "23/02/2024"
    
    # Converter a data para o formato desejado
    date_object = datetime.strptime(date_to_search, "%d/%m/%Y")
    formatted_date = date_object.strftime("%d %b %Y")  # Exemplo: "31 May 2024"
    
    # Buscar as datas das notícias
    dates = fetch_news_dates(url)
    
    # Contar as ocorrências da data especificada
    occurrences = count_date_occurrences(dates, formatted_date)
    
    print(f"Data pesquisada: {formatted_date}")
    print(f"Número de ocorrências encontradas: {occurrences}")

if __name__ == "__main__":
    main()
