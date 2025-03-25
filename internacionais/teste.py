import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime

class SustainalyticsSpider(scrapy.Spider):
    name = "sustainalytics"
    start_urls = [
        'https://www.sustainalytics.com/esg-research/search/1?indexCatalogue=resource-center-blog-posts&searchQuery=Environmental%20Sustainability&orderBy=Relevance'
    ]

    def parse(self, response):
        articles = response.css('div > div > div.card-footer')

        for article in articles:
            tipo = article.css('small::text').get()
            if tipo == 'Article':
                link = article.css('a::attr(href)').get()
                if link:
                    yield response.follow(link, self.parse_article)
        
        # Lógica de paginação
        current_page = int(response.url.split('/')[-1].split('?')[0])
        next_page = current_page + 1
        next_page_url = f'https://www.sustainalytics.com/esg-research/search/{next_page}?indexCatalogue=resource-center-blog-posts&searchQuery=Environmental%20Sustainability&orderBy=Relevance'
        
        # Checar se a próxima página tem conteúdo
        if response.css('div > div > div.card-footer'):
            yield response.follow(next_page_url, self.parse)

    def parse_article(self, response):
        titulo = response.css('#Contentplaceholder1_C013_Col01 > div.blog-post-detail-page-title.light > h1::text').get()
        data_emissao_raw = response.xpath('//*[@id="Contentplaceholder1_C013_Col01"]/div[2]/p/span/following-sibling::text()').get().strip()
        
        # Convertendo a data para o formato DD/MM/YYYY
        data_emissao = datetime.strptime(data_emissao_raw, '%B %d, %Y').strftime('%d/%m/%Y')
        
        texto = ' '.join(response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "blog-post-content", " " ))]//text()').getall()).strip()
        
        yield {
            'titulo': titulo,
            'data_emissao': data_emissao,
            'tipo': 'Article',
            'texto': texto,
            'link': response.url,
        }

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    })
    process.crawl(SustainalyticsSpider)
    process.start()
