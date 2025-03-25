import requests
from lxml import etree
from datetime import datetime, timedelta
import sys
import re

# URL do site que disponibiliza o XML
url = 'https://www.federalreserve.gov/feeds/press_enforcement.xml'

# Função para extrair e formatar as datas
def extract_dates_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.content
        tree = etree.fromstring(xml_content)
        pubdates = tree.xpath('//pubDate/text()')
        formatted_dates = []
        for pubdate in pubdates:
            # Remover <![CDATA[ e ]]>
            pubdate = pubdate.replace('<![CDATA[', '').replace(']]>', '').strip()
            # Parsear a string de data para um objeto datetime
            date_obj = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %Z')
            # Extrair apenas a data no formato desejado
            formatted_date = date_obj.strftime('%d %b %Y')
            formatted_dates.append(formatted_date)
        return formatted_dates
    else:
        print(f'Falha na requisição para {url}')
        return []

# Função para contar ocorrências de datas dentro do intervalo especificado
def count_date_occurrences(dates, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

    count = 0
    current_date = start_date

    while current_date <= end_date:
        target_date = current_date.strftime('%d %b %Y')
        count += dates.count(target_date)
        current_date += timedelta(days=1)
    
    return count

def main(start_date_str, end_date_str):
    # Processar a URL e extrair as datas
    dates = extract_dates_from_url(url)
    if dates:
        # Contar as ocorrências de datas no intervalo especificado
        count = count_date_occurrences(dates, start_date_str, end_date_str)
        print("ORIGIN:frb")
        print(f"TOTAL_COUNT:{count}")
    else:
        print("ORIGIN:frb")
        print("TOTAL_COUNT:0")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python script_base.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:frb")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]

    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:frb")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    main(data_inicio, data_fim)
