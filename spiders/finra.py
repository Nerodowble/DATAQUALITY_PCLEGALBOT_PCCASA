import aiohttp
import asyncio
from lxml import html
from datetime import datetime, timedelta
import sys
import re

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

async def compare_dates(url, xpath, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

    count = 0
    current_date = start_date

    while current_date <= end_date:
        target_date = current_date.strftime("%B %d, %Y")
        data = await extract_data(url, xpath)
        count += data.count(target_date)
        current_date += timedelta(days=1)
    
    return count

url = "https://www.finra.org/rules-guidance/notices"
xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "datetime", " " ))]'

async def main(start_date_str, end_date_str):
    count = await compare_dates(url, xpath, start_date_str, end_date_str)
    print("ORIGIN:finra")
    print(f"TOTAL_COUNT:{count}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python script_base.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:finra")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]

    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:finra")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    asyncio.run(main(data_inicio, data_fim))
