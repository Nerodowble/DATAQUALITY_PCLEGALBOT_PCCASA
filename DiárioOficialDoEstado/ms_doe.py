import requests
from lxml import html
import os

# URL do site
url = 'https://www.spdo.ms.gov.br/diariodoe'

# Realizando a requisição HTTP para obter o conteúdo da página
response = requests.get(url)
response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

# Parseando o conteúdo HTML da página
tree = html.fromstring(response.content)

# Encontrando os elementos com os XPaths fornecidos
titulos = tree.xpath('//td[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "abrirDiario", " " ))]')
datas = tree.xpath('//td/following-sibling::td//*[contains(concat( " ", @class, " " ), concat( " ", "abrirDiario", " " ))]')

# Data que você está procurando
data_procurada = '05/06/2024'

# Contador para acompanhar o número de itens encontrados
contador = 0

# Verificando se a quantidade de títulos e datas corresponde
if isinstance(titulos, list) and isinstance(datas, list):
    if len(titulos) != len(datas):
        print("A quantidade de títulos não corresponde à quantidade de datas. Verifique os XPaths fornecidos.")
    else:
        # Extraindo e exibindo os dados dos elementos encontrados
        for titulo, data in zip(titulos, datas):
            data_texto = data.text_content().strip()
            
            # Verificando se a data corresponde à data que você está procurando
            if data_texto == data_procurada:
                titulo_texto = titulo.text_content().strip()
                print(f"Título: {titulo_texto}")
                print(f"Data: {data_texto}")
                
                # Obtendo o ID do diário a partir do atributo 'id' do elemento do título
                diario_id = titulo.get('id')
                
                # Construindo a URL do PDF
                pdf_url = f'https://www.spdo.ms.gov.br/diariodoe/Index/Download/{diario_id}'
                
                # Realizando a requisição HTTP para obter o cabeçalho da resposta
                pdf_response = requests.head(pdf_url)
                pdf_response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
                
                # Obtendo o tamanho do conteúdo a partir do cabeçalho da resposta
                content_length = pdf_response.headers.get('Content-Length')

                if content_length:
                    print(f"Tamanho do PDF: {int(content_length) / 1024 / 1024} MB")
                else:
                    print("Não foi possível obter o tamanho do PDF.")
                
                print("="*50)
                
                # Incrementando o contador
                contador += 1

        print(f"Foram encontrados {contador} itens da data {data_procurada} procurada.")
else:
    print("Erro ao obter títulos e datas. Verifique os XPaths fornecidos.")
