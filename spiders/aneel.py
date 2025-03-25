import asyncio
import sys
import re
from datetime import datetime
from playwright.async_api import async_playwright

# URL da busca avançada na ANEEL
URL = "https://biblioteca.aneel.gov.br/Busca/Avancada"

# Seletores CSS corrigidos
BTN_LEGISLACAO = "body > main > div > div > div.row.ficha > div > div > button:nth-child(2)"
DATA_INICIAL = "#LegislacaoDataPublicacao1"
DATA_FINAL = "#LegislacaoDataPublicacao2"
BTN_BUSCAR = "body > main > div > div > div.row.ficha > form > div.botoes-busca > div.div-botao-confirmar > button"
RESULTADO_SELECTOR = "body > main > div > div > div.row.cabecalho-resultado-busca.lista > div:nth-child(1) > p > strong:nth-child(1)"

async def fetch_results(start_date, end_date):
    """ Acessa a página da ANEEL, faz a busca e retorna o número de resultados. """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Agora rodando em headless!
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        print("Acessando a página...")
        await page.goto(URL)
        await asyncio.sleep(2)  # Pequeno delay inicial para garantir carregamento

        print("Aguardando botão 'Legislação' aparecer...")
        await page.wait_for_selector(BTN_LEGISLACAO, timeout=15000)

        print("Simulando movimento do mouse para desbloquear elementos...")
        await page.hover(BTN_LEGISLACAO)  # Simula que o usuário está passando o mouse
        await asyncio.sleep(1)  # Pequena pausa para evitar bloqueios

        print("Clicando no botão 'Legislação'...")
        await page.click(BTN_LEGISLACAO, force=True)  # Usa force=True para garantir o clique

        print(f"Inserindo datas: {start_date} a {end_date}...")
        await page.wait_for_selector(DATA_INICIAL, timeout=10000)
        await page.fill(DATA_INICIAL, start_date)
        await page.fill(DATA_FINAL, end_date)

        print("Clicando no botão 'Buscar'...")
        await page.wait_for_selector(BTN_BUSCAR, timeout=10000)
        await page.click(BTN_BUSCAR, force=True)  # Garante que o clique seja realizado

        print("Aguardando carregamento dos resultados...")
        await page.wait_for_selector(RESULTADO_SELECTOR, timeout=60000)

        print("Extraindo quantidade de resultados...")
        resultado_texto = await page.locator(RESULTADO_SELECTOR).text_content()

        print("Concluído! Fechando navegador...")
        await browser.close()

        return int(resultado_texto.strip())

async def main(start_date_str, end_date_str):
    try:
        # Valida o formato das datas
        datetime.strptime(start_date_str, "%d/%m/%Y")
        datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:  # Captura exceções durante a conversão de datas
        print(f"Erro ao converter a data: {e}", file=sys.stderr)
        print("ORIGIN:aneel")
        print("TOTAL_COUNT:0")
        return

    total_resultados = await fetch_results(start_date_str, end_date_str)

    print(f"ORIGIN:aneel")
    print(f"TOTAL_COUNT:{total_resultados}")

if __name__ == "__main__":
    if len(sys.argv) != 3:  # Verifica se o número de argumentos é correto
        print("Uso: python script_aneel.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:aneel")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    data_inicio = sys.argv[1]  # Obtém a data de início dos argumentos
    data_fim = sys.argv[2]  # Obtém a data de fim dos argumentos
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):  # Verifica o formato das datas
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:aneel")
        print("TOTAL_COUNT:0")
        sys.exit(1)  # Encerra o script com código de erro

    asyncio.run(main(data_inicio, data_fim))  # Chama a função principal com as datas fornecidas
