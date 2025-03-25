import requests
from lxml import html

# URL alvo
url = "https://pcaobus.org/oversight/standards/auditing-standards/amendments_to_standards#_AS2315"

# Realizar a requisição GET para a URL
response = requests.get(url)
response.raise_for_status()  # Checar se a requisição foi bem-sucedida

# Parsear o conteúdo HTML da resposta
tree = html.fromstring(response.content)

# Extrair os dados usando XPath
items = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "k-table", " " ))]//a')

# Contabilizar quantos itens foram encontrados
num_items = len(items)

# Imprimir os itens encontrados e a contagem
for item in items:
    print(item.text_content(), item.get('href'))

print(f"\nTotal de itens encontrados: {num_items}")
