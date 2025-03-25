import asyncio  # Biblioteca para programação assíncrona
from playwright.async_api import async_playwright  # Playwright assíncrono
from datetime import datetime
import sys  # Biblioteca para manipulação de argumentos de linha de comando
import re  # Biblioteca para expressões regulares

# Cabeçalho de usuário para as requisições HTTP, simulando um navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Função assíncrona para buscar o conteúdo de uma URL e interagir com a página
async def fetch_and_process_data(url, start_date_str, end_date_str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Inicia o navegador em modo headless
        page = await browser.new_page()

        await page.goto(url)  # Acessa a URL

        # Clica no botão de "pesquisa avançada"
        await page.click('//*[contains(concat( " ", @class, " " ), concat( " ", "linkAvancado", " " ))]')

        # Preenche as datas inicial e final
        await page.fill('//*[(@id = "dta_promulgacao")]', start_date_str)  # Preenche data inicial
        await page.fill('//*[(@id = "dta_promulgacao_final")]', end_date_str)  # Preenche data final

        # Clica no botão de pesquisar
        await page.click('//*[contains(concat( " ", @class, " " ), concat( " ", "btn-primary", " " )) and contains(concat( " ", @class, " " ), concat( " ", "btn-block", " " ))]')

        # Espera até o resultado ser carregado
        await page.wait_for_selector('//*[contains(concat( " ", @class, " " ), concat( " ", "resultado", " " ))]')

        # Extrai o número de resultados
        # Extrai o texto do elemento resultado
        resultado_texto = await page.locator('//*[contains(concat( " ", @class, " " ), concat( " ", "resultado", " " ))]').text_content()

        # Utiliza regex para extrair apenas números
        resultado_numero = re.search(r"(\d+)", resultado_texto)  # Captura o primeiro número encontrado

        # Se encontrou um número válido, atribui o valor, caso contrário, define como zero
        resultado_final = resultado_numero.group(1) if resultado_numero else "0"

        # Fecha o navegador
        await browser.close()

        return resultado_final  # Retorna o resultado encontrado

# Função principal assíncrona
async def main(start_date_str, end_date_str):
    try:
        # Converte as datas de string para objetos datetime
        global start_date, end_date
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:  # Captura exceções durante a conversão de datas
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:ANVISA")
        print("TOTAL_COUNT:0")
        return

    # A URL que será acessada
    url = "https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=consultarAtosInicial&cod_modulo=134&cod_menu=1696"

    # Chama a função para buscar e processar os dados
    resultado = await fetch_and_process_data(url, start_date_str, end_date_str)

    # Exibe a origem e o resultado total
    print("ORIGIN:ANVISA")
    print(f"TOTAL_COUNT:{resultado}")

# Ponto de entrada do script
if __name__ == "__main__":
    if len(sys.argv) != 3:  # Verifica se o número de argumentos é correto
        print("Uso: python anvisa.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:ANVISA")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    data_inicio = sys.argv[1]  # Obtém a data de início dos argumentos
    data_fim = sys.argv[2]  # Obtém a data de fim dos argumentos
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):  # Verifica o formato das datas
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:ANVISA")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    asyncio.run(main(data_inicio, data_fim))  # Chama a função principal com as datas fornecidas
