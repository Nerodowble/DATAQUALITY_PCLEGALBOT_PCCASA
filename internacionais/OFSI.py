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
    # Data fornecida e formatada
    provided_date_str = '20/04/2018'
    provided_date = datetime.strptime(provided_date_str, '%d/%m/%Y').strftime('%d %b %Y')

    urls_xpaths = [
        ('https://www.gov.uk/search/policy-papers-and-consultations?organisations%5b%5d=office-of-financial-sanctions-implementation&parent=office-of-financial-sanctions-implementation', '//time'),
        ('https://www.gov.uk/search/news-and-communications?organisations%5b%5d=office-of-financial-sanctions-implementation&parent=office-of-financial-sanctions-implementation', '//time'),
        ('https://www.gov.uk/search/transparency-and-freedom-of-information-releases?organisations%5b%5d=office-of-financial-sanctions-implementation&parent=office-of-financial-sanctions-implementation', '//time')
    ]

    tasks = [extract_data(url, xpath) for url, xpath in urls_xpaths]
    results = await asyncio.gather(*tasks)

    total_count = 0

    for idx, (url, xpath) in enumerate(urls_xpaths):
        print(f'Itens da URL {idx + 1}:')
        count = 0
        for item in results[idx]:
            try:
                # Parse o texto do item para uma data
                date = parser.parse(item).strftime('%d %b %Y')
                print(date)  # Para verificação, remova isso se não for necessário
                if provided_date == date:
                    count += 1
            except ValueError:
                continue
        print(f'Total encontrado na URL {idx + 1}: {count}')
        total_count += count
        print()

    print(f'Total geral encontrado: {total_count}')

if __name__ == '__main__':
    asyncio.run(main())
