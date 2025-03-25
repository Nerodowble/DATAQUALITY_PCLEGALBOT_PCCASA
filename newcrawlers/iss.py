import requests
from bs4 import BeautifulSoup

# URL da página
url = "https://www.issgovernance.com/policy-gateway/voting-policies/"
base_url = "https://www.issgovernance.com"

# Fazer a requisição HTTP para obter o conteúdo da página
response = requests.get(url)
response.raise_for_status()  # Levanta um erro se a requisição falhar

# Parsear o conteúdo HTML da página
soup = BeautifulSoup(response.content, "html.parser")

# Extrair todos os itens do primeiro seletor
elements1 = soup.select("#list-32 > ul > li > a")

# Extrair o item específico do segundo seletor
element2 = soup.select_one("#list-77 > ul > li:nth-child(2) > a")

# Salvar os dados em listas e variáveis
titles1, urls1 = [], []

for element in elements1:
    titles1.append(element.text.strip())
    urls1.append(base_url + element['href'])

if element2:
    title2 = element2.text.strip()
    url2 = base_url + element2['href']
else:
    title2 = url2 = None

# Imprimir os dados extraídos
print("Dados do primeiro grupo de elementos:")
for title, url in zip(titles1, urls1):
    print(f"Título: {title}, URL: {url}")

print("\nDados do segundo elemento:")
if title2 and url2:
    print(f"Título: {title2}, URL: {url2}")
else:
    print("Segundo elemento não encontrado")
