import aiohttp
import asyncio
from lxml import html
from datetime import datetime, timedelta
import sys
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except Exception as e:
            print(f"Erro ao buscar URL {url}: {e}")
            return None

async def get_data(url):
    page_content = await fetch(url)
    if page_content:
        tree = html.fromstring(page_content)
        items = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "text-green", " " ))]')
        for item in items:
            try:
                text_content = item.text_content().strip()
                match = re.search(r"(\d+) atos encontrados", text_content)
                if match:
                    return int(match.group(1))
            except IndexError as e:
                print(f"Erro ao processar item: {e}")
                continue
    return 0

def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:anp")
        print("TOTAL_COUNT:0")
        return

    total_count = 0
    date_format = "%d-%m-%Y"
    start_date_str = start_date.strftime(date_format)
    end_date_str = end_date.strftime(date_format)
    url = f"https://atosoficiais.com.br/anp/?q=&date_start={start_date_str}&date_end={end_date_str}"

    count = asyncio.run(get_data(url))
    total_count += count

    print("ORIGIN:anp")
    print(f"TOTAL_COUNT:{total_count}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script_anp.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:anp")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:base")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    main(data_inicio, data_fim)
