from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

def run(start_date_str, end_date_str):
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        total_count = 0
        current_date = datetime.strptime(start_date_str, "%d/%m/%Y")

        # Mapeamento dos meses em português para inglês
        month_translation = {
            'janeiro': 'January', 'fevereiro': 'February', 'março': 'March',
            'abril': 'April', 'maio': 'May', 'junho': 'June',
            'julho': 'July', 'agosto': 'August', 'setembro': 'September',
            'outubro': 'October', 'novembro': 'November', 'dezembro': 'December'
        }

        while current_date <= datetime.strptime(end_date_str, "%d/%m/%Y"):
            date_str = current_date.strftime("%d/%m/%Y")

            # Acessar a URL com a data específica
            page.goto(f"https://www.bcb.gov.br/estabilidadefinanceira/str?data={date_str}")

            # Obter o ano de referência
            year_locator = page.locator('//*[contains(concat(" ", @class, " "), concat(" ", "mb-sm-0", " "))]')
            year_value = year_locator.inner_text().split('\n')[0]  # Certifique-se de obter apenas o primeiro ano listado

            # Selecionar todos os títulos dos meses
            month_titles = page.locator('//div[contains(@id, "heading-")]/h2/button/span[1]')
            month_count = month_titles.count()

            for i in range(month_count):
                # Obter o título do mês
                month_title = month_titles.nth(i).inner_text()

                # Expandir o mês para ver os detalhes
                month_titles.nth(i).click()
                page.wait_for_timeout(1000)  # Esperar 1 segundo para garantir que o conteúdo seja carregado

                # Selecionar os detalhes dentro do mês
                detail_xpath = f'//*[@id="collapse-{i}"]//h3'
                details = page.locator(detail_xpath)
                detail_count = details.count()

                for j in range(detail_count):
                    # Obter os detalhes do mês
                    detail_value = details.nth(j).inner_text()

                    # Verificar se o detalhe é uma data
                    if "Informe" not in detail_value:
                        try:
                            # Extrair a data e formatar
                            date_str = detail_value.strip().split(', ')[1]
                            month_pt = month_title.split()[0]
                            month_en = month_translation[month_pt.lower()]
                            formatted_date = f'{int(date_str.split()[0]):02d} de {month_pt} de {year_value}'
                            standard_date = f'{date_str.split()[0]}/{int(datetime.strptime(month_en, "%B").strftime("%m"))}/{year_value}'

                            # Imprimir os dados encontrados
                            print(f"Data: {formatted_date} - Página: STR")

                            # Contar ocorrências dentro do intervalo
                            total_count += 1

                        except Exception as e:
                            print(f"Erro ao processar detalhe: {e}")

            current_date += timedelta(days=1)

        # Fechar o navegador
        browser.close()

        # Retornar o total de ocorrências encontradas
        return total_count

    except Exception as ex:
        print(f"Erro ao executar script: {ex}")
        return 0

if __name__ == "__main__":
    start_date = "25/06/2024"
    end_date = "01/07/2024"

    total_count = run(start_date, end_date)
    print(f"Total de ocorrências encontradas no intervalo de {start_date} a {end_date}: {total_count}")
