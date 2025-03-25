from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import sys
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

MESES_PT = {
    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
}

MESES_TRADUCAO = {v.lower(): k for k, v in MESES_PT.items()}

async def fetch(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.set_extra_http_headers(headers)
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await page.wait_for_selector('table.visaoQuadrosTabela', timeout=45000)
            content = await page.content()
            return content
        except Exception as e:
            print(f"Erro durante o scraping: {e}", file=sys.stderr)
            return None
        finally:
            await browser.close()

def parse_content(content, start_date, end_date):
    soup = BeautifulSoup(content, 'html.parser')
    tabela = soup.find('table', {'class': 'visaoQuadrosTabela'})
    
    total = 0
    if tabela:
        for linha in tabela.find_all('tr')[1:]:
            cols = linha.find_all('td')
            if len(cols) >= 2:
                data_str = cols[0].get_text(strip=True)
                
                # Regex para capturar "1º de janeiro de 2023" ou "1 de janeiro de 2023 - Edição especial"
                match = re.search(
                    r'(\d{1,2})(?:º)?\s+de\s+([^\d\W]+)\s+de\s+(\d{4})', 
                    data_str.split('-')[0].strip()  # Remove texto após hífen
                )
                
                if match:
                    try:
                        dia = int(match.group(1).replace('º', ''))  # Remove "º"
                        mes_nome = match.group(2).lower().strip()
                        mes = MESES_TRADUCAO[mes_nome]
                        ano = int(match.group(3))
                        data_obj = datetime(ano, mes, dia)
                        
                        if start_date <= data_obj <= end_date:
                            itens = cols[1].find_all('a')
                            total += len(itens)
                    except KeyError:
                        print(f"Mês não reconhecido: {mes_nome}", file=sys.stderr)
                    except Exception as e:
                        print(f"Erro ao processar data: {data_str} - {e}", file=sys.stderr)
    return total

def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro de formato de data: {e}", file=sys.stderr)
        print("ORIGIN:planalto")
        print("TOTAL_COUNT:0")
        return

    mes_pt = MESES_PT[start_date.month].lower()
    url = (
        f"https://www4.planalto.gov.br/legislacao/portal-legis/resenha-diaria/"
        f"{start_date.year}-resenha-diaria/{mes_pt}-resenha-diaria"
    )

    try:
        content = asyncio.run(fetch(url))
        if content:
            total = parse_content(content, start_date, end_date)
        else:
            total = 0
    except Exception as e:
        print(f"Erro fatal: {e}", file=sys.stderr)
        total = 0

    print("ORIGIN:planalto")
    print(f"TOTAL_COUNT:{total}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python planalto.py <data_inicio_dd/mm/yyyy> <data_fim_dd/mm/yyyy>", file=sys.stderr)
        print("ORIGIN:planalto")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    if not all(re.match(r"\d{2}/\d{2}/\d{4}", arg) for arg in sys.argv[1:3]):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:planalto")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])