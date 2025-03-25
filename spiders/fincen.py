import aiohttp
import asyncio
from lxml import html
from datetime import datetime, timedelta
from dateutil import parser
import sys
import re

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def extract_data(url, xpath):
    content = await fetch(url)
    tree = html.fromstring(content)
    elements = tree.xpath(xpath)
    return [element.text_content().strip() for element in elements]

async def process_date_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

    count = 0
    current_date = start_date
    xpath = '/html/body/div/div/div/section/div[2]/div/div/div[3]/div/div/div/span[1]/span/time'
    
    while current_date <= end_date:
        current_date_str = current_date.strftime('%Y-%m-%d')
        current_date_display = current_date.strftime('%d %b %Y')

        url = f'https://www.fincen.gov/news-room/news?field_date_release_value={current_date_str}&field_date_release_value_1={current_date_str}&field_tags_financial_institution_target_id=All'
        
        data = await extract_data(url, xpath)
        
        print(f'Itens da URL para a data {current_date_display}:')
        for item in data:
            try:
                date = parser.parse(item).strftime('%d %b %Y')
                print(date)  # Para verificação, remova isso se não for necessário
                if current_date_display == date:
                    count += 1
            except ValueError:
                continue

        current_date += timedelta(days=1)
    
    print(f'ORIGIN:fincen')
    print(f'TOTAL_COUNT:{count}')
    print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python script_base.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:fincen")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]

    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:fincen")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    asyncio.run(process_date_range(data_inicio, data_fim))
