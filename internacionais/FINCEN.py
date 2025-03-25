import aiohttp
import asyncio
from lxml import html
from datetime import datetime
from dateutil import parser

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def extract_data(url, xpath):
    content = await fetch(url)
    tree = html.fromstring(content)
    elements = tree.xpath(xpath)
    return [element.text_content().strip() for element in elements]

async def main():
    # Data fornecida
    provided_date_str = '13/02/2024'
    provided_date = datetime.strptime(provided_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    provided_date_display = datetime.strptime(provided_date_str, '%d/%m/%Y').strftime('%d %b %Y')

    # URL com as datas preenchidas
    url = f'https://www.fincen.gov/news-room/news?field_date_release_value={provided_date}&field_date_release_value_1={provided_date}&field_tags_financial_institution_target_id=All'
    xpath = '/html/body/div/div/div/section/div[2]/div/div/div[3]/div/div/div/span[1]/span/time'
    
    data = await extract_data(url, xpath)
    
    count = 0
    print(f'Itens da URL:')
    for item in data:
        try:
            # Parse o texto do item para uma data
            date = parser.parse(item).strftime('%d %b %Y')
            print(date)  # Para verificação, remova isso se não for necessário
            if provided_date_display == date:
                count += 1
        except ValueError:
            continue
    print(f'Total encontrado: {count}')
    print()

if __name__ == '__main__':
    asyncio.run(main())
