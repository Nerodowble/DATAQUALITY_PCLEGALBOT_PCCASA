#Modelo de script base para spiders DQ.

import requests  # Biblioteca para fazer requisições HTTP
import aiohttp  # Biblioteca para fazer requisições HTTP assíncronas
import asyncio  # Biblioteca para programação assíncrona
from lxml import html  # Biblioteca para parsear HTML
from datetime import datetime  # Biblioteca para manipulação de datas
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

# Função assíncrona para processar o conteúdo da página e contar os itens
async def get_data(url):
    page_content = await fetch(url)  # Faz a requisição e obtém o conteúdo da página
    item_count = 0  # Inicializa a contagem de itens
    if page_content:
        tree = html.fromstring(page_content)  # Parseia o conteúdo HTML
        # Exemplo de extração de dados, ajuste o XPath conforme necessário
        items = tree.xpath('//exemplo_de_xpath')  # Substitua '//exemplo_de_xpath' pelo XPath real
        for item in items:
            try:
                # Lógica de processamento dos dados extraídos
                item_count += 1  # Incrementa a contagem de itens
            except IndexError as e:  # Captura exceções durante o processamento
                print(f"Erro ao processar item: {e}")
                continue
    return item_count  # Retorna a contagem de itens

# Função principal que itera sobre o intervalo de datas e acumula o total de itens
def main(start_date_str, end_date_str):
    try:
        # Converte as datas de string para objetos datetime
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:  # Captura exceções durante a conversão de datas
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:base")
        print("TOTAL_COUNT:0")
        return

    current_date = start_date  # Inicializa a data corrente
    total_count = 0  # Inicializa a contagem total

    # Itera sobre o intervalo de datas
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%Y")  # Converte a data corrente para string no formato DD/MM/YYYY
        # Substitua 'url_base' com a URL do site que você deseja scrapear
        url = f"url_base&data={date_str}"  # Constrói a URL para a data corrente
        # Chama a função assíncrona para obter os dados
        count = asyncio.run(get_data(url))  # Executa a função assíncrona e obtém a contagem de itens
        total_count += count  # Acumula a contagem total
        current_date += datetime.timedelta(days=1)  # Incrementa a data corrente

    # Imprime a origem e a contagem total, no formato esperado pelo script pai
    print("ORIGIN:base")
    print(f"TOTAL_COUNT:{total_count}")

# Ponto de entrada do script
if __name__ == "__main__":
    if len(sys.argv) != 3:  # Verifica se o número de argumentos é correto
        print("Uso: python script_base.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:base")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    data_inicio = sys.argv[1]  # Obtém a data de início dos argumentos
    data_fim = sys.argv[2]  # Obtém a data de fim dos argumentos
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):  # Verifica o formato das datas
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:base")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    main(data_inicio, data_fim)  # Chama a função principal com as datas fornecidas
