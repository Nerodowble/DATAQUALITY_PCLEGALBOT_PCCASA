import aiohttp
import asyncio
import json
import os
from lxml import html

async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def extract_data(url, xpath):
    page_content = await fetch_page(url)
    tree = html.fromstring(page_content)
    items = tree.xpath(xpath)
    return [item.text_content().strip() for item in items]

async def main():
    base_url = 'https://www.cfatf-gafic.org/home/cfatf-news?start='
    xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "clearfix", " " ))]//h3'
    json_file = 'cfatf_data.json'

    all_data = []
    for i in range(0, 25, 5):  # Paginar 5 vezes (0, 5, 10, 15, 20)
        url = f'{base_url}{i}'
        data = await extract_data(url, xpath)
        all_data.extend(data)

    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            saved_data = json.load(file)
        
        new_items = set(all_data) - set(saved_data)
        if new_items:
            print(f'Itens diferentes encontrados: {new_items}')
            print(f'Quantidade de itens diferentes: {len(new_items)}')
            with open(json_file, 'w') as file:
                json.dump(all_data, file, indent=4)
        else:
            print('0')
    else:
        with open(json_file, 'w') as file:
            json.dump(all_data, file, indent=4)
        print('Novo arquivo JSON criado.')

if __name__ == '__main__':
    asyncio.run(main())
