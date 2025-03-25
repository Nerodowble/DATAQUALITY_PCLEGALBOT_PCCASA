import aiohttp
import asyncio
import aiofiles
import json
from bs4 import BeautifulSoup

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Verifica se há erros HTTP
            content = await response.content.read()
            return content.decode('utf-8', errors='ignore')
    except aiohttp.ClientConnectorError as e:
        print(f"Erro de conexão ao tentar acessar {url}: {e}")
    except Exception as e:
        print(f"Erro ao tentar acessar {url}: {e}")

async def main():
    base_url = "https://pcaobus.org/oversight/standards/auditing-standards/"
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Fetch the main page
        main_page = await fetch(session, base_url)
        if main_page is None:
            return

        soup = BeautifulSoup(main_page, 'html.parser')
        
        # Find all items generically
        item_urls = []
        divs = soup.select('#Main_T92A60133009_Col01 > div')
        for div in divs:
            items = div.select('ul > li > a')
            for item in items:
                item_urls.append(item['href'])

        # Ensure URLs are complete
        item_urls = [f"https://pcaobus.org{url}" if not url.startswith("http") else url for url in item_urls]

        # Iterate over each item URL
        for index, item_url in enumerate(item_urls):
            item_page = await fetch(session, item_url)
            if item_page is None:
                continue

            item_soup = BeautifulSoup(item_page, 'html.parser')
            
            # Extract the title
            title_elem = item_soup.select_one('#Main_T92A60133009_Col01 > article > header > h1')
            title = title_elem.text.strip() if title_elem else "Título não encontrado"
            
            # Extract the article content
            article_elem = item_soup.select_one('#Main_T92A60133009_Col01 > article > div > div')
            article = article_elem.text.strip() if article_elem else "Artigo não encontrado"
            
            # Store the results
            results.append({
                'title': title,
                'article': article,
                'url': item_url
            })
            
            # Adding delay to prevent overwhelming the server
            await asyncio.sleep(1.5)
    
    # Save results to a JSON file with UTF-8 encoding
    async with aiofiles.open('results.json', 'w', encoding='utf-8') as json_file:
        await json_file.write(json.dumps(results, ensure_ascii=False, indent=4))

asyncio.run(main())
