import asyncio
import random
import aiohttp
from playwright.async_api import async_playwright
from lxml import html
import re
from datetime import datetime
import sys

# Cabeçalho para as requisições HTTP (B3)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# URL base da B3
B3_BASE_URL = "https://www.b3.com.br/pt_br/regulacao/oficios-e-comunicados/oficios-e-comunicados/?dataIni={}&dataFim={}&pagination={}"
B3_XPATH = '//*[contains(concat( " ", @class, " " ), concat( " ", "least-content", " " ))]'

# URL base do Bora Investir
BORAINVESTIR_BASE_URL = "https://borainvestir.b3.com.br/noticias/page/{}"
XPATH_PAGE_1 = ('//*[contains(concat( " ", @class, " " ), concat( " ", "mt-md-0", " " ))]'
                '//*[contains(concat( " ", @class, " " ), concat( " ", "post-meta__date", " " ))] | '
                '//*[contains(concat( " ", @class, " " ), concat( " ", "post-meta--white", " " ))]'
                '//*[contains(concat( " ", @class, " " ), concat( " ", "post-meta__date", " " ))]')
CSS_SELECTOR = "#main-content > div > div > div.col-lg-7 > section > div > ul > li article a div div.col-md-7.mt-3.mt-md-0 div div"

# ========================== #
# FUNÇÃO PARA SCRAPEAR A B3  #
# ========================== #
async def fetch_b3(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Erro ao buscar URL {url}: {e}")
    return None

async def scrape_b3(start_date, end_date):
    """ Pagina na B3 e para quando encontra uma data abaixo do intervalo. """
    total_found = 0
    page_number = 1

    while True:
        url = B3_BASE_URL.format(start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"), page_number)
        page_content = await fetch_b3(url)

        if not page_content:
            break  # Se não encontrar conteúdo, encerra a busca

        tree = html.fromstring(page_content)
        items = tree.xpath(B3_XPATH)

        if not items:
            break  # Se a página não contém itens, terminamos a busca

        dates = []
        for item in items:
            try:
                item_text = item.text_content().strip()
                item_date = datetime.strptime(item_text, "%d/%m/%y")
                dates.append(item_date)
            except ValueError:
                continue

        if not dates:
            break  # Se não encontrou datas válidas, encerramos

        dates.sort()
        oldest_date_in_page = dates[0]  # Data mais antiga na página

        if oldest_date_in_page < start_date:
            valid_dates = [date for date in dates if date >= start_date]
            total_found += len(valid_dates)
            break  # Para a execução se encontrar uma data abaixo do intervalo

        total_found += len([date for date in dates if start_date <= date <= end_date])

        page_number += 1  # Passa para a próxima página

    return total_found

# ================================= #
# FUNÇÃO PARA SCRAPEAR O BORA INVESTIR #
# ================================= #
async def fetch_borainvestir(page_number, retries=3):
    """ Faz scraping de Bora Investir usando Playwright. """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = BORAINVESTIR_BASE_URL.format(page_number)

        for _ in range(retries):
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(random.randint(5, 10))

                selector = XPATH_PAGE_1 if page_number == 1 else CSS_SELECTOR

                if await page.is_visible(selector):
                    date_elements = await page.locator(selector).all_text_contents()
                    await browser.close()

                    return [re.search(r"\d{2}/\d{2}/\d{2}", date).group() for date in date_elements if re.search(r"\d{2}/\d{2}/\d{2}", date)]

            except:
                pass

        await browser.close()
        return []

async def scrape_borainvestir(start_date, end_date):
    """ Pagina no Bora Investir e para quando encontra uma data abaixo do intervalo. """
    total_found = 0
    page_number = 1

    while True:
        dates = await fetch_borainvestir(page_number)

        if not dates:
            break  # Se a página não contém datas, terminamos a busca

        sorted_dates = sorted(datetime.strptime(date, "%d/%m/%y") for date in dates)
        oldest_date_in_page = sorted_dates[0]

        if oldest_date_in_page < start_date:
            valid_dates = [date.strftime('%d/%m/%y') for date in sorted_dates if date >= start_date]
            total_found += len(valid_dates)
            break

        total_found += len([date for date in dates if start_date <= datetime.strptime(date, "%d/%m/%y") <= end_date])

        page_number += 1

    return total_found

# ========================== #
# FUNÇÃO PRINCIPAL (UNIFICADA) #
# ========================== #
async def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:b3")
        print("TOTAL_COUNT:0")
        return

    # Executa scraping da B3 e do Bora Investir em paralelo
    b3_count, borainvestir_count = await asyncio.gather(
        scrape_b3(start_date, end_date),
        scrape_borainvestir(start_date, end_date)
    )

    # Soma os resultados das duas fontes
    total_count = b3_count + borainvestir_count

    # Exibe apenas um resultado consolidado
    print("ORIGIN:b3")
    print(f"TOTAL_COUNT:{total_count}")

# ========================== #
# EXECUÇÃO DO SCRIPT        #
# ========================== #
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script_duplo.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:b3")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]

    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:b3")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    asyncio.run(main(data_inicio, data_fim))
