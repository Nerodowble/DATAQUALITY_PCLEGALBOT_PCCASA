import requests
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
    if not page_content:
        return []
    tree = html.fromstring(page_content)
    data = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "recent-changes-results", " " ))]//text()')
    cleaned_data = [item.strip() for item in data if item.strip()]

    structured_data = []
    current_date = None

    for i in range(len(cleaned_data)):
        item = cleaned_data[i]
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', item):
            if current_date:
                structured_data.append(current_date)
            current_date = {"data": item, "sections_changed": 0, "items": []}
        elif re.search(r'\((\d+) sections changed\)', item):
            if current_date:
                match = re.search(r'\((\d+) sections changed\)', item)
                if match:
                    current_date["sections_changed"] = int(match.group(1))
        else:
            if current_date:
                if '§' in item:
                    current_date["items"].append(f"dado encontrado(§): {item}")
                else:
                    current_date["items"].append(item)

    if current_date:
        structured_data.append(current_date)

    for entry in structured_data:
        actual_sections_count = sum(1 for item in entry["items"] if '§' in item)
        entry["sections_changed"] = actual_sections_count

    return structured_data

def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:ecfr")
        print("TOTAL_COUNT:0")
        return

    url = "https://www.ecfr.gov/recent-changes?search%5Bdate%5D=current&search%5Bhierarchy%5D%5Btitle%5D=12"
    structured_data = asyncio.run(get_data(url))

    total_sections_count = 0

    for entry in structured_data:
        entry_date = datetime.strptime(entry["data"], "%m/%d/%Y")
        if start_date <= entry_date <= end_date:
            total_sections_count += entry["sections_changed"]

    print("ORIGIN:ecfr")
    print(f"TOTAL_COUNT:{total_sections_count}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script_ecfr.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:ecfr")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:ecfr")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    main(data_inicio, data_fim)
