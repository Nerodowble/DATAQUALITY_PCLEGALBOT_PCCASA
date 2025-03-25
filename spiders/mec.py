import asyncio
import aiohttp
from aiohttp import ClientSession
from lxml import html
import urllib.parse
import ssl

async def fetch_data(session, name, urls):
    if not isinstance(urls, list):  # Garante que urls sempre seja uma lista
        urls = [urls]
    results_sum = 0
    for url in urls:
        try:
            async with session.get(url) as response:
                content = await response.text()
                tree = html.fromstring(content)
                result = tree.xpath('//*[@id="_br_com_seatecnologia_in_buscadou_BuscaDouPortlet_userDataForm"]/p/text()')
                result_number = int(result[0].split()[0]) if result else 0
                results_sum += result_number
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
    return name, results_sum

async def fetch_all_data(start_date, end_date, subcategories):
    encoded_start_date = urllib.parse.quote(start_date)
    encoded_end_date = urllib.parse.quote(end_date)
    base_url = (
        f"https://www.in.gov.br/consulta/-/buscar/dou?"
        f"q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&"
        f"publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Ministério+da+Educação"
    )
    
    links = {
        subcat: f"{base_url}&orgSub={urllib.parse.quote(subcat)}"
        for subcat in subcategories
    }

    sslcontext = ssl.create_default_context()
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE

    conn = aiohttp.TCPConnector(ssl=sslcontext)

    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [asyncio.create_task(fetch_data(session, name, url)) for name, url in links.items()]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    start_date = "13/01/2025"
    end_date = "13/01/2025"
    subcategories = [
            "Universidade Tecnológica Federal do Paraná",
            "Câmpus Pato Branco",
            "Câmpus Ponta Grossa",
            "Universidade Federal dos Vales do Jequitinhonha e Mucuri",
            "Universidade Federal do Triângulo Mineiro",
            "Pró-Reitoria de Administração",
            "Pró-Reitoria de Recursos Humanos",
            "Departamento de Administração de Pessoal",
            "Universidade Federal do Sul e Sudeste do Pará",
            "Universidade Federal do Rio de Janeiro",
            "Pró-Reitoria de Gestão e Governança",
            "Universidade Federal do Rio Grande do Sul",
            "Pró-Reitoria de Gestão de Pessoas",
            "Universidade Federal do Rio Grande do Norte",
            "Universidade Federal do Recôncavo da Bahia",
            "Universidade Federal do Pará",
            "Universidade Federal do Paraná",
            "Departamento de Administração Pessoal",
            "Universidade Federal do Oeste do Pará",
            "Universidade Federal do Oeste da Bahia",
            "Universidade Federal do Norte do Tocantins",
            "Universidade Federal do Espírito Santo",
            "Diretoria de Projetos Institucionais",
            "Universidade Federal do Ceará",
            "Pró-Reitoria de Planejamento e Administração",
            "Universidade Federal de Uberlândia",
            "Universidade Federal de São Paulo",
            "Universidade Federal de Santa Maria",
            "Campus da Universidade Federal de Santa Maria em Cachoeira do Sul",
            "Universidade Federal de Santa Catarina",
            "Pró-Reitoria de Desenvolvimento e Gestão de Pessoas",
            "Universidade Federal de Rondonópolis",
            "Universidade Federal de Pernambuco",
            "Pró-Reitoria de Gestão de Pessoas e Qualidade de Vida",
            "Universidade Federal de Minas Gerais",
            "Escola de Arquitetura",
            "Pró-Reitoria de Planejamento",
            "Biblioteca Universitária",
            "Divisão de Coleções Especiais",
            "Faculdade de Medicina",
            "Universidade Federal de Lavras",
            "Universidade Federal de Juiz de Fora",
            "Universidade Federal de Jataí",
            "Universidade Federal de Itajubá",
            "Diretoria de Desenvolvimento de Pessoal",
            "Universidade Federal de Goiás",
            "Pró-Reitoria de Administração e Finanças",
            "Universidade Federal de Campina Grande",
            "Centro de Saúde e Tecnologia Rural",
            "Universidade Federal de Alfenas",
            "Universidade Federal de Alagoas",
            "Pró-Reitoria de Gestão de Pessoas e do Trabalho",
            "Universidade Federal da Paraíba",
            "Superintendência de Orçamento e Finanças",
            "Universidade Federal da Integração Latino-Americana",
            "Gabinete da Reitoria",
            "Universidade Federal da Fronteira Sul",
            "Universidade Federal da Bahia",
            "Coordenação de Gestão de Pessoas",
            "Universidade Federal Rural do Semi-Árido",
            "Universidade Federal Rural do Rio de Janeiro",
            "Pró-Reitoria de Assuntos Financeiros",
            "Departamento de Materiais e Serviços Auxiliares",
            "Universidade Federal Rural de Pernambuco",
            "Universidade Federal Fluminense",
            "Coordenação de Planejamento e Desenvolvimento",
            "Empresa Brasileira de Serviços Hospitalares",
            "Instituto Federal de Educação, Ciência e Tecnologia da Bahia",
            "REI",
            "Fundação Universidade Federal do Maranhão",
            "Fundação Universidade Federal de Viçosa",
            "Pró-Reitoria de Planejamento e Orçamento",
            "Diretoria de Governança Institucional",
            "Fundação Universidade Federal de São João Del Rei",
            "Pró-Reitoria de Gestão e Desenvolvimento de Pessoas",
            "Colégio Pedro II",
            "Instituto Federal de Educação, Ciência e Tecnologia do Paraná",
            "Instituto Federal de Educação, Ciência e Tecnologia Catarinense",
            "Pró-Reitoria de Desenvolvimento, Inclusão, Diversidade e Assistência à Pessoa",
            "Instituto Federal de Educação, Ciência e Tecnologia Sul-Rio-Grandense",
            "Pró-Reitoria de Administração e de Planejamento",
            "Fundação Universidade Federal do Mato Grosso do Sul",
            "Pró-Reitoria de Administração e Infraestrutura",
            "Fundação Universidade Federal do Acre",
            "Instituto Federal de Educação, Ciência e Tecnologia do Sudeste de Minas Gerais",
            "Fundação Universidade Federal do Piauí",
            "Instituto Federal de Educação, Ciência e Tecnologia do Norte de Minas Gerais",
            "Instituto Federal de Educação, Ciência e Tecnologia do Ceará",
            "Campus Maracanaú",
            "Instituto Federal de Educação, Ciência e Tecnologia de Santa Catarina",
            "Instituto Federal de Educação, Ciência e Tecnologia de Alagoas",
            "Instituto Federal de Educação, Ciência e Tecnologia da Paraíba",
            "Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Norte",
            "Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul",
            "Instituto Federal de Educação, Ciência e Tecnologia de Brasília",
            "Instituto Federal de Educação, Ciência e Tecnologia do Maranhão",
            "Campus Barreirinhas",
            "Instituto Federal de Educação, Ciência e Tecnologia do Espírito Santo",
            "Fundação Universidade Federal do Rio Grande",
            "Instituto Federal de Educação, Ciência e Tecnologia de São Paulo",
            "Fundação Universidade Federal do Vale do São Francisco",
            "Hospital Universitário",
            "Campus Apodi",
            "Centro Federal de Educação Tecnológica Celso Suckow da Fonseca",
            "Campus Nova Cruz",
            "Instituto Federal de Educação, Ciência e Tecnologia de Roraima",
            "Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Sul",
            "Instituto Federal de Educação, Ciência e Tecnologia do Pará",
            "Instituto Federal de Educação, Ciência e Tecnologia do Rio de Janeiro",
            "Campus Pinheiral",
            "Filial Hospital Universitário da UFS",
            "Instituto Federal de Educação, Ciência e Tecnologia de Rondônia",
            "Campus Jaru",
            "Diretoria de Planejamento e Administração",
            "Coordenação de Compras e Licitação",
            "Instituto Federal de Educação, Ciência e Tecnologia Baiano",
            "Campus Guanambi",
            "Campus Pontes e Lacerda",
            "Instituto Federal de Educação, Ciência e Tecnologia do Sertão Pernambucano",
            "Campus Vitória",
            "Instituto Federal de Educação, Ciência e Tecnologia de Pernambuco",
            "Campus Belo Jardim",
            "Filial Hospital Universitário Prof. Alberto Antunes",
            "Filial Hospital das Clínicas da UFG",
            "Instituto Federal de Educação, Ciência e Tecnologia Fluminense",
            "Fundação Universidade de Brasília",
            "Fundação Universidade Federal de Mato Grosso",
            "Instituto Federal de Educação, Ciência e Tecnologia de Goiás",
            "Campus Salvador",
            "Filial Hospital Universitário Professor Dr. Horácio Carlos Penepucci",
            "Instituto Federal de Educação, Ciência e Tecnologia do Amazonas",
            "Campus Tabatinga",
            "Instituto Federal de Educação, Ciência e Tecnologia do Piauí",
            "Instituto Federal de Educação, Ciência e Tecnologia Farroupilha",
            "Instituto Federal de Educação, Ciência e Tecnologia de Minas Gerais",
            "Campus Cachoeiro do Itapemirim",
            "Fundação Universidade do Amazonas",
            "Fundação Universidade Federal de Rondônia",
            "Fundação Universidade Federal do Pampa",
            "Instituto Federal de Educação, Ciência e Tecnologia do Sul de Minas Gerais",
            "Campus Crateús",
            "Decanato de Gestão de Pessoas",
            "Campus Tauá",
            "EBSERH - Filial Complexo Hospitalar da UFRJ (HUCFF, IPPMG, ME)",
            "Campus Tijuca I",
            "Filial Hospital das Clínicas da UFPE",
            "Instituto Federal de Educação, Ciência e Tecnologia de Sergipe",
            "Hospital de Clínicas de Porto Alegre",
            "Fundação Universidade Federal do Tocantins",
            "Filial Hospital das Clínicas da UFMG",
            "Campus Marabá Industrial",
            "Campus Arraial do Cabo",
            "Fundação Universidade Federal de Sergipe",
            "Instituto Federal de Educação, Ciência e Tecnologia Goiano",
            "Fundação Universidade Federal de Ouro Preto",
            "Campus Osório",
            "Diretoria de Administração e Planejamento",
            "Fundação Universidade Federal de Pelotas",
            "Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso",
            "Campus Belém",
            "Campus João Câmara",
            "Universidade da Integração Internacional da Lusofonia Afro-Brasileira",
            "Centro de Ciências da Saúde",
            "Pró-Reitoria de Desenvolvimento e Gestão de Pessoal",
            "Universidade Federal do Estado do Rio de Janeiro",
            "Universidade Federal do Cariri",
            "Pró-Reitoria de Ensino",
            "Departamento de Seleção",
            "Ministério da Educação"


    ]
    results = await fetch_all_data(start_date, end_date, subcategories)
    
    total_count = 0
    for name, count in results:
        print(f"{name}: {count}")
        total_count += count
    
    print("\n=== TOTAL COUNT ===")
    print(f"Total: {total_count}")

if __name__ == "__main__":
    asyncio.run(main())
