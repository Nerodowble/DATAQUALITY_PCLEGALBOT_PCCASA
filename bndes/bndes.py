import re
from datetime import datetime, date
from pymongo import MongoClient
from playwright.sync_api import sync_playwright

# URI de conexão com o MongoDB
uri = (
    "mongodb+srv://lbprod-pri.cuho0.mongodb.net/"
    "?authMechanism=MONGODB-X509&authSource=%24external&tls=true"
    "&tlsCertificateKeyFile=C:\\Users\\willi\\OneDrive\\Documentos\\Acessos\\Acesso ao MongoDB\\X509-cert-4384389572589510418.pem"
)

# Conecta ao MongoDB, seleciona o banco 'legalbot_platform' e a collection 'norm'
client = MongoClient(uri)
db = client['legalbot_platform']
collection = db['norm']

def generate_date_variants(title):
    """
    A partir de um título, que tem o padrão:
      "Circular nº 23/2025, de 12.03.2025"
    ou
      "Circular nº 16/2025, de 25 de fevereiro de 2025"
    gera duas variantes do título (com data numérica e com data textual).
    """
    if ", de " not in title:
        return [title]
    prefix, date_str = title.split(", de ", 1)
    date_str = date_str.strip().rstrip(".")
    variants = []
    # Caso formato numérico: dd.mm.yyyy
    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{4}$", date_str):
        parts = date_str.split(".")
        day = parts[0]
        month_num = parts[1]
        year = parts[2]
        month_map = {
            "01": "janeiro", "1": "janeiro",
            "02": "fevereiro", "2": "fevereiro",
            "03": "março", "3": "março",
            "04": "abril", "4": "abril",
            "05": "maio", "5": "maio",
            "06": "junho", "6": "junho",
            "07": "julho", "7": "julho",
            "08": "agosto", "8": "agosto",
            "09": "setembro", "9": "setembro",
            "10": "outubro",
            "11": "novembro",
            "12": "dezembro"
        }
        month_name = month_map.get(month_num, month_num)
        numeric_variant = f"{prefix}, de {day}.{month_num}.{year}"
        text_variant = f"{prefix}, de {day} de {month_name} de {year}"
        variants.extend([numeric_variant, text_variant])
    # Caso formato textual: "dd de mês de yyyy"
    elif re.match(r"^\d{1,2}\s+de\s+\w+\s+de\s+\d{4}$", date_str):
        parts = date_str.split()
        if len(parts) >= 5:
            day = parts[0]
            month_word = parts[2]
            year = parts[4]
            month_map = {
                "janeiro": "01",
                "fevereiro": "02",
                "março": "03",
                "abril": "04",
                "maio": "05",
                "junho": "06",
                "julho": "07",
                "agosto": "08",
                "setembro": "09",
                "outubro": "10",
                "novembro": "11",
                "dezembro": "12"
            }
            month_num = month_map.get(month_word.lower(), month_word)
            numeric_variant = f"{prefix}, de {day}.{month_num}.{year}"
            text_variant = f"{prefix}, de {day} de {month_word} de {year}"
            variants.extend([numeric_variant, text_variant])
    else:
        variants.append(title)
    return list(set(variants))

def parse_date_from_title(title):
    """
    Extrai a data do título e retorna um objeto datetime.date.
    Exemplo de título:
      "Circular nº 23/2025, de 12.03.2025"
      "Circular nº 16/2025, de 25 de fevereiro de 2025"
    """
    if ", de " not in title:
        return None
    parts = title.split(", de ", 1)
    date_str = parts[1].strip().rstrip(".")
    # Tenta o formato numérico: dd.mm.yyyy
    try:
        d = datetime.strptime(date_str, "%d.%m.%Y").date()
        return d
    except ValueError:
        pass
    # Tenta o formato textual: "dd de mês de yyyy"
    m = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", date_str)
    if m:
        day = int(m.group(1))
        month_word = m.group(2).lower()
        year = int(m.group(3))
        month_map = {
            "janeiro": 1,
            "fevereiro": 2,
            "março": 3,
            "abril": 4,
            "maio": 5,
            "junho": 6,
            "julho": 7,
            "agosto": 8,
            "setembro": 9,
            "outubro": 10,
            "novembro": 11,
            "dezembro": 12
        }
        month = month_map.get(month_word)
        if month:
            return date(year, month, day)
    return None

def main():
    # Parâmetros de range de data (formato "dd/mm/yyyy")
    range_start_str = "12/03/2025"
    range_end_str = "12/03/2025"
    range_start = datetime.strptime(range_start_str, "%d/%m/%Y").date()
    range_end = datetime.strptime(range_end_str, "%d/%m/%Y").date()
    
    url = "https://www.bndes.gov.br/wps/portal/site/home/instituicoes-financeiras-credenciadas/normas/normas-operacoes-indiretas"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        page.wait_for_selector("#normas_info")
        
        # Extração do valor total (apenas o número)
        normas_info_element = page.query_selector("#normas_info")
        total_texto = normas_info_element.inner_text().strip() if normas_info_element else ""
        # Exemplo: "Exibindo de 1 a 50 de 1,285 resultados"
        match = re.search(r"de\s+([\d,\.]+)\s+resultados", total_texto)
        total_numero = match.group(1).replace(",", "").replace(".", "") if match else "Número não encontrado"
        print("Valor Total:", total_numero)
        
        # Extrai as linhas da tabela e coleta título e data extraída
        linhas = page.query_selector_all("#normas > tbody > tr")
        scraped_items = []
        if linhas:
            for idx, linha in enumerate(linhas, start=1):
                title_element = linha.query_selector("td a")
                if title_element:
                    titulo = title_element.inner_text().strip()
                    item_date = parse_date_from_title(titulo)
                    scraped_items.append({
                        "title": titulo,
                        "date": item_date
                    })
                    print(f"{idx:02d} - Título: {titulo} - Data extraída: {item_date}")
                else:
                    print(f"{idx:02d} - Título não encontrado nesta linha.")
        else:
            print("Nenhuma linha encontrada na tabela '#normas'.")
        
        browser.close()
    
    # Filtra os itens cujo campo "date" esteja dentro do range informado
    items_in_range = [item for item in scraped_items if item["date"] and range_start <= item["date"] <= range_end]
    print("\nResumo da pesquisa:")
    print(f"Para o range {range_start_str} a {range_end_str} no SITE foram encontrados {len(items_in_range)} documentos.")
    
    # Consulta no MongoDB para cada item do range, considerando variantes de formatação da data
    found_in_db = []
    missing = []
    for item in items_in_range:
        variants = generate_date_variants(item["title"])
        query = { "origin": "BNDES", "title": { "$in": variants } }
        doc = collection.find_one(query)
        if doc:
            found_in_db.append(item["title"])
        else:
            missing.append(item["title"])
    
    print(f"No banco foram encontrados {len(found_in_db)} documentos.")
    if missing:
        print("Documento(s) faltante(s):")
        for title in missing:
            print(title)
    else:
        print("Nenhum documento faltante.")

if __name__ == "__main__":
    main()
