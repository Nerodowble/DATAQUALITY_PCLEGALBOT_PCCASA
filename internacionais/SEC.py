from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import aiohttp
import asyncio
from lxml import html
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

# Função para converter a data
def convert_date(input_date):
    date_obj = datetime.strptime(input_date, '%d/%m/%Y')
    formatted_date = date_obj.strftime('%d %B %Y')
    # Remover zeros à esquerda no dia
    if formatted_date[0] == '0':
        formatted_date = formatted_date[1:]
    return formatted_date

# Função Selenium para a primeira URL
def selenium_part_1():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get("https://www.sec.gov/news/pressreleases?aId=&combine=&year=2024&month=All")
        driver.implicitly_wait(10)
        elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "datetime", " " ))]')
        data = [element.text.strip() for element in elements]
    finally:
        driver.quit()

    return data

# Função Selenium para a segunda URL
def selenium_part_2():
    chrome_options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        url = 'https://www.sec.gov/rules/rulemaking-activity?aId=&search=&rulemaking_status=All&division_office=All&year=2024'
        driver.get(url)
        driver.implicitly_wait(10)
        elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "datetime", " " ))]')
        data = [element.text.strip() for element in elements]
    finally:
        driver.quit()

    return data

# Função aiohttp
async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_and_parse(session, url, xpath_query):
    html_content = await fetch_url(session, url)
    tree = html.fromstring(html_content)
    elements = tree.xpath(xpath_query)
    return [element.text_content().strip() for element in elements]

async def aiohttp_part():
    url = "https://www.sec.gov.ph/investors-education-and-information/notices/#gsc.tab=0"
    xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "myDate", " " ))]'

    async with aiohttp.ClientSession() as session:
        results = await fetch_and_parse(session, url, xpath)
        return results

# Função principal para juntar as partes
def main(input_date):
    converted_date = convert_date(input_date)
    print(f"Converted Date: {converted_date}")

    # Executa a parte Selenium para a primeira URL
    selenium_data_1 = selenium_part_1()
    print("Data from Selenium part 1:")
    for data in selenium_data_1:
        print(data)
    selenium_count_1 = selenium_data_1.count(converted_date)
    print(f"Occurrences in Selenium part 1: {selenium_count_1}")

    # Executa a parte Selenium para a segunda URL
    selenium_data_2 = selenium_part_2()
    print("Data from Selenium part 2:")
    for data in selenium_data_2:
        print(data)
    selenium_count_2 = selenium_data_2.count(converted_date)
    print(f"Occurrences in Selenium part 2: {selenium_count_2}")

    # Executa a parte aiohttp
    aiohttp_data = asyncio.run(aiohttp_part())
    print("Data from aiohttp part:")
    for data in aiohttp_data:
        print(data)
    aiohttp_count = aiohttp_data.count(converted_date)
    print(f"Occurrences in aiohttp data: {aiohttp_count}")

    # Total occurrences
    total_count = selenium_count_1 + selenium_count_2 + aiohttp_count
    print(f"Total occurrences of {converted_date}: {total_count}")

if __name__ == '__main__':
    # Informe a data no formato 'dd/mm/yyyy'
    input_date = '22/09/2016'
    main(input_date)
