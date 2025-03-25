import aiohttp
import asyncio
from lxml import html
from datetime import datetime

async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def extract_data(url, xpath):
    page_content = await fetch_page(url)
    tree = html.fromstring(page_content)
    elements = tree.xpath(xpath)
    dates = []
    for element in elements:
        date_text = element.text_content().strip()
        # Remove the day of the week
        date_parts = date_text.split(', ', 1)
        if len(date_parts) == 2:
            dates.append(date_parts[1])
    return dates

def convert_date(input_date):
    date_obj = datetime.strptime(input_date, "%d/%m/%Y")
    formatted_date = date_obj.strftime("%B %d, %Y")
    return formatted_date

async def compare_dates(url, xpath, input_date):
    target_date = convert_date(input_date)
    data = await extract_data(url, xpath)
    count = data.count(target_date)
    return count

url = "https://www.finra.org/rules-guidance/notices"
xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "datetime", " " ))]'
input_date = "26/02/2024"  # Exemplo de data a ser comparada

async def main():
    count = await compare_dates(url, xpath, input_date)
    if count > 0:
        print(count)
    else:
        print(0)

asyncio.run(main())
