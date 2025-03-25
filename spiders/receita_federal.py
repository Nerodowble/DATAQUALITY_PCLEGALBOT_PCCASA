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
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except Exception as e:
            print(f"Erro ao buscar URL {url}: {e}")
            return None

# Função para contar os itens da Receita Federal
def count_receita_federal_items(date):
    url = f"https://www.gov.br/receitafederal/pt-br/assuntos/noticias?form.submitted=1&texto=&dt_inicio={date}&dt_fim={date}&categoria="
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = html.fromstring(response.content)
        elementos = soup.xpath('//*[contains(concat(" ", @class, " "), concat(" ", "data", " "))]')
        return len(elementos)
    return 0

# Função assíncrona para processar o conteúdo da página e contar os itens
async def get_data(url):
    page_content = await fetch(url)
    if page_content:
        tree = html.fromstring(page_content)
        element = tree.xpath("//strong")
        if element:
            text = element[0].text_content().strip()
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())
            else:
                return 0
        else:
            return 0
    return 0

# Função principal que itera sobre o intervalo de datas e acumula o total de itens
def main(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:Receita Federal")
        print("TOTAL_COUNT:0")
        return

    current_date = start_date
    total_count = 0

    # Itera sobre o intervalo de datas
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%Y")
        
        # Contabiliza os itens da Receita Federal
        receita_count = count_receita_federal_items(date_str)
        
        # Constrói a URL para a data corrente
        url = f"http://normas.receita.fazenda.gov.br/sijut2consulta/consulta.action?dt_inicio={date_str}&dt_fim={date_str}"
        count = asyncio.run(get_data(url))
        
        total_count += count + receita_count  # Acumula a contagem total
        current_date += timedelta(days=1)

    # Imprime a origem e a contagem total, no formato esperado pelo script pai
    print("ORIGIN:Receita Federal")
    print(f"TOTAL_COUNT:{total_count}")

# Ponto de entrada do script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script_Receita Federal.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:Receita Federal")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:Receita Federal")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    main(data_inicio, data_fim)
