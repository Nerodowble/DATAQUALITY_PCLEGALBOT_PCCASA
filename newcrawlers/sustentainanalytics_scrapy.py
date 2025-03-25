import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse

# URL de destino
url = "https://www.sustainalytics.com/esg-research/search?indexCatalogue=resource-center-blog-posts&searchQuery=ESG"

# Cabeçalhos para a requisição HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fazendo a requisição
response = requests.get(url, headers=headers)

# Verifica se a requisição foi bem sucedida
if response.status_code == 200:
    # Utiliza Scrapy para processar a resposta HTML
    class SustSpider(scrapy.Spider):
        name = "sust_spider"
        start_urls = [url]

        def parse(self, response):
            titulo = response.css("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div:nth-child(1) > div > div > div.card-body > p::text").get().strip()
            subtitulo = response.css("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div:nth-child(1) > div > div > div.card-body > div::text").get().strip()
            tipo = response.css("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div:nth-child(1) > div > div > div.card-footer > small::text").get().strip()
            url_artigo = response.css("#Contentplaceholder1_C007_Col00 > div > div.row.sust-blog-items > div:nth-child(1) > div > div > div.card-footer > a::attr(href)").get()

            yield {
                'Titulo': titulo,
                'Subtitulo': subtitulo,
                'Tipo': tipo,
                'URL': url_artigo
            }

    # Cria uma instância do processador Scrapy
    process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    })

    # Cria uma resposta HTML a partir do conteúdo da requisição
    response_html = HtmlResponse(url=url, body=response.content, encoding='utf-8')

    # Inicia o spider Scrapy com a resposta HTML
    process.crawl(SustSpider, response=response_html)
    process.start()
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
