import asyncio
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from lxml import html
from datetime import datetime, timedelta
import sys
import re
import locale

# Definir localidade para português do Brasil
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# Mapeamento de meses com a primeira letra maiúscula
meses = {
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março',
    '04': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}

# Função assíncrona para buscar e processar os dados na primeira URL
async def fetch_data(url, log_data):
    log_data['logs'].append(f"Iniciando fetch_data para URL: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        await page.goto(url)
        
        try:
            await page.wait_for_selector('.small', timeout=60000)  # Aumentar o timeout para 60 segundos
        except Exception as e:
            await browser.close()
            log_data['errors'].append(f"Erro ao carregar a página {url}: {e}")
            return 0

        content = await page.content()
        tree = html.fromstring(content)
        elements = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "small", " " ))]')
        
        for element in elements:
            text_content = element.text_content()
            if "Foram encontrados" in text_content:
                value = text_content.split()[2]
                await browser.close()
                log_data['logs'].append(f"Data {url}: Encontrado valor: {value}")
                return int(value)
        
        await browser.close()
        log_data['logs'].append(f"Data {url}: Nenhum valor encontrado")
        return 0

# Função assíncrona para buscar e processar os dados na segunda URL
async def fetch_data_new_url(url, target_date, log_data):
    log_data['logs'].append(f"Iniciando fetch_data_new_url para URL: {url} com data alvo: {target_date}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        await page.goto(url)
        
        try:
            await page.wait_for_selector('ul', timeout=60000)  # Aumentar o timeout para 60 segundos
        except Exception as e:
            await browser.close()
            log_data['errors'].append(f"Erro ao carregar a página {url}: {e}")
            return 0

        content = await page.content()
        tree = html.fromstring(content)
        elements = tree.xpath('/html/body/div[6]/ul/li')
        
        count = 0
        
        for element in elements:
            link = element.xpath('./a/@href')
            if link:
                link_url = urljoin(url, link[0])
                await page.goto(link_url)
                new_content = await page.content()
                new_tree = html.fromstring(new_content)
                start_date = new_tree.xpath('//*[@id="dataInicio"]/text()')
                if start_date:
                    start_date_text = start_date[0].strip()
                    if start_date_text == target_date:
                        count += 1
                        log_data['logs'].append(f"Data {link_url}: Encontrado na data {target_date}")
        
        await browser.close()
        log_data['logs'].append(f"Data {url}: Total encontrado na data {target_date}: {count}")
        return count

# Função assíncrona para buscar e processar os dados na terceira URL (integrada do script fornecido)
async def fetch_data_third_url(target_date, log_data):
    log_data['logs'].append(f"Iniciando fetch_data_third_url para data alvo: {target_date}")
    data_especificada = datetime.strptime(target_date, "%d/%m/%Y").strftime("%d de %B de %Y").replace(' 0', ' ')
    meses_en = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho",
        "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    data_especificada = ' '.join(meses_en.get(word, word) for word in data_especificada.split())

    contador_de_datas = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        await page.goto('https://www.bcb.gov.br/estabilidadefinanceira/sicornoticias')
        
        try:
            await page.wait_for_selector('ul', timeout=60000)
        except Exception as e:
            await browser.close()
            log_data['errors'].append(f"Erro ao carregar a página https://www.bcb.gov.br/estabilidadefinanceira/sicornoticias: {e}")
            return 0

        elements = await page.query_selector_all('//*[contains(concat( " ", @class, " " ), concat( " ", "col-md-8", " " ))]//ul')

        for i, element in enumerate(elements):
            element_text = await element.inner_text()
            element_text = element_text.replace('\u00a0', ' ')  # Substitui espaços não separáveis por espaços normais
            date_pattern = r'\d{2} de [a-zA-Z]+ de \d{4}'
            dates = re.findall(date_pattern, element_text)

            for date in dates:
                if date == data_especificada:
                    contador_de_datas += 1

        await browser.close()
    
    log_data['logs'].append(f"Total encontrado na URL Sicor para a data {target_date}: {contador_de_datas}")
    return contador_de_datas

# Script adicional inserido na lógica principal
def format_manual_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        month_number = date_obj.strftime('%m')
        month_name = meses[month_number]
        formatted_date = f'{date_obj.strftime("%d")} de {month_name} de {date_obj.strftime("%Y")}'
        return formatted_date
    except Exception as e:
        return None

def convert_to_standard_date(date_str, month_name, year):
    try:
        date_obj = datetime.strptime(date_str, f'%d de {month_name} de %Y')
        standard_date = date_obj.strftime('%d/%m/%Y')
        return standard_date
    except Exception as e:
        return None

def run(playwright, manual_date, log_data):
    log_data['logs'].append(f"Iniciando run com data manual: {manual_date}")
    formatted_manual_date = format_manual_date(manual_date)
    standard_manual_date = manual_date  # Mantendo o formato padrão 'dd/MM/yyyy'

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    # Acessar a URL
    page.goto("https://www.bcb.gov.br/estabilidadefinanceira/str", timeout=60000)  # Aumentar para 60 segundos (60000 milissegundos)

    # Obter o ano de referência
    year_locator = page.locator('//*[contains(concat(" ", @class, " "), concat(" ", "mb-sm-0", " "))]')
    year_value = year_locator.inner_text().split('\n')[0]  # Certifique-se de obter apenas o primeiro ano listado

    # Selecionar todos os títulos dos meses
    month_titles = page.locator('//div[contains(@id, "heading-")]/h2/button/span[1]')
    month_count = month_titles.count()

    manual_date_count = 0

    for i in range(month_count):
        # Obter e imprimir o título do mês
        month_title = month_titles.nth(i).inner_text()

        # Extrair o mês de referência
        month_name = month_title.split()[0].capitalize()

        # Expandir o mês para ver os detalhes
        month_titles.nth(i).click()
        page.wait_for_timeout(1000)  # Esperar 1 segundo para garantir que o conteúdo seja carregado

        # Selecionar os detalhes dentro do mês
        detail_xpath = f'//*[@id="collapse-{i}"]//h3'
        details = page.locator(detail_xpath)
        detail_count = details.count()

        for j in range(detail_count):
            # Obter e imprimir os detalhes do mês
            detail_value = details.nth(j).inner_text()

            # Verificar se o detalhe é uma data
            if "Informe" not in detail_value:
                try:
                    # Extrair a data e formatar
                    date_str = detail_value.strip().split(', ')[1]
                    formatted_date = f'{int(date_str.split()[0]):02d} de {month_name} de {year_value}'
                    standard_date = convert_to_standard_date(formatted_date, month_name, year_value)

                    # Verificar se a data formatada coincide com a data manual
                    if formatted_date == formatted_manual_date or standard_date == standard_manual_date:
                        manual_date_count += 1

                except Exception as e:
                    pass

    # Adicionando a requisição do novo XPath para elementos adicionais
    additional_elements = page.locator('//*[contains(concat(" ", @class, " "), concat(" ", "pl-3", " "))]')
    additional_count = additional_elements.count()

    for k in range(additional_count):
        additional_text = additional_elements.nth(k).inner_text()

        # Verificar se o elemento adicional contém uma data no formato 'dd/MM/yyyy'
        date_parts = additional_text.split()
        if len(date_parts) >= 3:
            try:
                date_str = date_parts[-1]  # A data deve ser o último elemento
                date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                formatted_date = f'{date_obj.strftime("%d")} de {meses[date_obj.strftime("%m")]} de {date_obj.strftime("%Y")}'
                standard_date = date_str  # Já está no formato padrão

                # Verificar se a data coincide com a data manual
                if formatted_date == formatted_manual_date or standard_date == standard_manual_date:
                    manual_date_count += 1

            except ValueError:
                pass

    # Fechar o navegador
    browser.close()

    log_data['logs'].append(f"Total encontrado no run para a data manual {manual_date}: {manual_date_count}")

    # Retornar a contagem de ocorrências da data manual
    return manual_date_count

# Função principal que itera sobre o intervalo de datas e acumula o total de itens
async def main(start_date_str, end_date_str):
    log_data = {'logs': [], 'errors': [], 'total_count': 0}

    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError as e:
        log_data['errors'].append(f"Erro ao converter a data: {e}")
        print("ORIGIN:bacen")
        print("TOTAL_COUNT:0")
        return

    current_date = start_date
    total_count = 0

    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%Y")

        url = f"https://www.bcb.gov.br/estabilidadefinanceira/buscanormas?dataInicioBusca={date_str}&dataFimBusca={date_str}&tipoDocumento=Todos"
        count = await fetch_data(url, log_data)
        total_count += count

        new_url = "https://www3.bcb.gov.br/audpub/AudienciasAtivas?1"
        count_new_url = await fetch_data_new_url(new_url, date_str, log_data)
        total_count += count_new_url

        count_third_url = await fetch_data_third_url(date_str, log_data)
        total_count += count_third_url

        current_date += timedelta(days=1)

    log_data['total_count'] = total_count

    return total_count, start_date_str, log_data  # Retornar a data e log_data para uso em outras funções

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python bacen.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:bacen")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    data_inicio = sys.argv[1]
    data_fim = sys.argv[2]
    if not re.match(r"\d{2}/\d{2}/\d{4}", data_inicio) or not re.match(r"\d{2}/\d{2}/\d{4}", data_fim):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:bacen")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    total_count, date_used, log_data = asyncio.run(main(data_inicio, data_fim))

    with sync_playwright() as playwright:
        manual_date_count = run(playwright, date_used, log_data)
        final_total_count = total_count + manual_date_count
        log_data['logs'].append(f"Total final incluindo run: {final_total_count}")
        print("ORIGIN:bacen")
        print(f"TOTAL_COUNT:{final_total_count}")
        print("LOGS:")
        for log in log_data['logs']:
            print(log)
        if log_data['errors']:
            print("ERRORS:")
            for error in log_data['errors']:
                print(error)
