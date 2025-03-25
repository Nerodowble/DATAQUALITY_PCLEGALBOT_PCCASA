import requests
from lxml import etree
from datetime import datetime

# URLs dos sites que disponibilizam o XML
urls = [
    'https://www.occ.gov/rss/occ_alerts.xml',
    'https://www.occ.gov/rss/occ_bulletins.xml',
    'https://www.occ.gov/rss/occ_news.xml'
]

# Função para extrair e formatar as datas
def extract_dates_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.content
        tree = etree.fromstring(xml_content)
        pubdates = tree.xpath('//pubDate/text()') + tree.xpath('//pubdate/text()')
        formatted_dates = []
        for pubdate in pubdates:
            date_obj = datetime.strptime(pubdate, '%d %b %Y %H:%M:%S %z')
            formatted_date = date_obj.strftime('%d %b %Y')
            formatted_dates.append(formatted_date)
        return formatted_dates
    else:
        print(f'Falha na requisição para {url}')
        return []

# Função para contar ocorrências da data especificada
def count_date_occurrences(dates, target_date):
    return dates.count(target_date)

# Definir a data de interesse
input_date_str = '31/05/2024'
try:
    input_date_obj = datetime.strptime(input_date_str, '%d/%m/%Y')
    target_date = input_date_obj.strftime('%d %b %Y')
except ValueError:
    print('Data no formato incorreto. Utilize dd/mm/yyyy.')
    exit()

# Processar cada URL e exibir os resultados separadamente
total_count = 0
for url in urls:
    dates = extract_dates_from_url(url)
    if dates:
        print(f'Resultados para {url}:')
        count = count_date_occurrences(dates, target_date)
        total_count += count
        print(f'  Data {target_date} encontrada {count} vez(es).')
    else:
        print(f'Nenhuma data encontrada para {url}')

print(f'Total de ocorrências da data {target_date}: {total_count}')
