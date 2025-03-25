import requests  # Biblioteca para fazer requisições HTTP
import aiohttp  # Biblioteca para fazer requisições HTTP assíncronas
import asyncio  # Biblioteca para programação assíncrona
from lxml import html  # Biblioteca para parsear HTML
from datetime import datetime, timedelta  # Biblioteca para manipulação de datas
import sys  # Biblioteca para manipulação de argumentos de linha de comando
import re  # Biblioteca para expressões regulares

# Cabeçalho de usuário para as requisições HTTP, simulando um navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Função assíncrona para buscar o conteúdo de uma URL
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:  # Adiciona cabeçalho à requisição
                if response.status == 200:  # Verifica se a resposta foi bem-sucedida
                    return await response.text()  # Retorna o conteúdo da página como texto
                else:
                    return None
        except Exception as e:  # Captura exceções durante a requisição
            print(f"Erro ao buscar URL {url}: {e}")
            return None

# Função para converter a data para o formato desejado
def convert_date(date_str):
    try:
        date_obj = datetime.strptime(date_str.strip(), "Created: %d %B %Y")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError as e:
        print(f"Erro na conversão da data: {e}")
        return None

# Função assíncrona para processar o conteúdo da página e contar os itens
async def get_data(url, start_date, end_date):
    page_content = await fetch(url)  # Faz a requisição e obtém o conteúdo da página
    item_count = 0  # Inicializa a contagem de itens
    if page_content:
        tree = html.fromstring(page_content)  # Parseia o conteúdo HTML
        # Extração de datas, ajuste o XPath conforme necessário
        dates = tree.xpath('//time/text()')  # Substitua '//time' pelo XPath real
        for date in dates:
            converted_date = convert_date(date)
            if converted_date:
                date_obj = datetime.strptime(converted_date, "%d/%m/%Y")
                if start_date <= date_obj <= end_date:
                    item_count += 1  # Incrementa a contagem de itens
    return item_count  # Retorna a contagem de itens

# Função principal que itera sobre o intervalo de datas e acumula o total de itens
def main(start_date_str, end_date_str):
    try:
        # Converte as datas de string para objetos datetime
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:  # Captura exceções durante a conversão de datas
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:cfatf")
        print("TOTAL_COUNT:0")
        return

    # Obter o número total de páginas
    total_pages = asyncio.run(fetch_total_pages())
    if total_pages == 0:
        print("Unable to determine the total number of pages to process", file=sys.stderr)
        print("ORIGIN:cfatf")
        print("TOTAL_COUNT:0")
        return

    total_count = 0  # Inicializa a contagem total

    # Itera sobre todas as páginas
    for page in range(total_pages):
        url = f"https://www.cfatf-gafic.org/home/cfatf-news?start={page * 5}"
        count = asyncio.run(get_data(url, start_date, end_date))  # Executa a função assíncrona e obtém a contagem de itens
        total_count += count  # Acumula a contagem total

    # Imprime a origem e a contagem total, no formato esperado pelo script pai
    print("ORIGIN:cfatf")
    print(f"TOTAL_COUNT:{total_count}")

# Função assíncrona para buscar o total de páginas
async def fetch_total_pages():
    url = "https://www.cfatf-gafic.org/home/cfatf-news?start=0"
    page_content = await fetch(url)
    if page_content:
        tree = html.fromstring(page_content)
        counter_text = tree.xpath('//*[contains(concat(" ", @class, " "), concat(" ", "counter", " "))]/text()')
        if counter_text:
            match = re.search(r'Page \d+ of (\d+)', counter_text[0])
            if match:
                total_pages = int(match.group(1))
                return total_pages
    return 0

# Ponto de entrada do script
if __name__ == "__main__":
    if len(sys.argv) != 3:  # Verifica se o número de argumentos é correto
        print("Uso: python cfatf.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:cfatf")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    data_inicio = sys.argv[1]  # Obtém a data de início dos argumentos
    data_fim = sys.argv[2]  # Obtém a data de fim dos argumentos
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):  # Verifica o formato das datas
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:cfatf")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    main(data_inicio, data_fim)  # Chama a função principal com as datas fornecidas
