import aiohttp
import asyncio
from lxml import html
from datetime import datetime

# URL do site que disponibiliza o HTML
url = 'https://www.rcips.ky/news/department?Dep_Val=21'

# Função assíncrona para fazer a requisição e extrair dados
async def fetch_and_extract_dates(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                tree = html.fromstring(content)
                dates = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "news_date", " " ))]/text()')
                return [date.strip() for date in dates]
            else:
                print(f'Falha na requisição para {url}')
                return []

# Função para converter a data no formato `dd/mm/yyyy` para o formato do site
def convert_date_format(input_date_str):
    try:
        input_date_obj = datetime.strptime(input_date_str, '%d/%m/%Y')
        # Formatar a data no estilo desejado (e.g., `13th May, 2024`)
        day = input_date_obj.day
        if 11 <= day <= 13:
            day_suffix = 'th'
        else:
            day_suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
        formatted_date = input_date_obj.strftime(f'{day}{day_suffix} %B, %Y')
        return formatted_date
    except ValueError:
        print('Data no formato incorreto. Utilize dd/mm/yyyy.')
        return None

# Função principal para rodar o código assíncrono
async def main():
    input_date_str = '13/05/2024'
    target_date = convert_date_format(input_date_str)
    if not target_date:
        return

    dates = await fetch_and_extract_dates(url)
    if dates:
        print(f'Datas encontradas em {url}:')
        count = dates.count(target_date)
        for i, date in enumerate(dates, 1):
            print(f'  Data {i}: {date}')
        print(f'Data {target_date} encontrada {count} vez(es).')
    else:
        print(f'Nenhuma data encontrada para {url}')

# Executar a função principal
asyncio.run(main())
