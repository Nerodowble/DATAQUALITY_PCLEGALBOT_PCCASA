import asyncio
from aiohttp import ClientSession
from lxml import html
import urllib.parse

async def fetch_data(session, name, urls):
    if not isinstance(urls, list):  # Garante que urls sempre seja uma lista
        urls = [urls]
    results_sum = 0
    for url in urls:
        async with session.get(url) as response:
            content = await response.text()
            tree = html.fromstring(content)
            result = tree.xpath('//*[@id="_br_com_seatecnologia_in_buscadou_BuscaDouPortlet_userDataForm"]/p/text()')
            result_number = int(result[0].split()[0]) if result else 0
            results_sum += result_number
    return f"{name}: {results_sum}"

async def fetch_all_data(start_date, end_date):
    encoded_start_date = urllib.parse.quote(start_date)
    encoded_end_date = urllib.parse.quote(end_date)
    links = {
        "AGU/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Presid%C3%AAncia+da+Rep%C3%BAblica&orgSub=Advocacia-Geral+da+Uni%C3%A3o",
        "ANATEL/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+das+Comunica%C3%A7%C3%B5es&orgSub=Ag%C3%AAncia+Nacional+de+Telecomunica%C3%A7%C3%B5es",
        "ANCINE/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Cultura&orgSub=Ag%C3%AAncia+Nacional+do+Cinema",
        "ANPD/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Justi%C3%A7a+e+Seguran%C3%A7a+P%C3%BAblica&orgSub=Autoridade+Nacional+de+Prote%C3%A7%C3%A3o+de+Dados",
        "BACEN/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Banco+Central+do+Brasil",
        "BNDES/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+do+Desenvolvimento%2C+Ind%C3%BAstria%2C+Com%C3%A9rcio+e+Servi%C3%A7os&orgSub=Banco+Nacional+de+Desenvolvimento+Econ%C3%B4mico+e+Social",
        "CADE/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Justi%C3%A7a+e+Seguran%C3%A7a+P%C3%BAblica&orgSub=Conselho+Administrativo+de+Defesa+Econ%C3%B4mica",
        "CAMEX/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Presid%C3%AAncia+da+Rep%C3%BAblica&orgSub=C%C3%A2mara+de+Com%C3%A9rcio+Exterior",
        "Casa Civil-Presidencia da Republica/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Presid%C3%AAncia+da+Rep%C3%BAblica&orgSub=Casa+Civil",
        "Casa Civil-Governo do Estado/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Governo+do+Estado&orgSub=Governo+do+Estado+do+Cear%C3%A1",
        "CCFGTS/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+do+Trabalho+e+Emprego&orgSub=Conselho+Curador+do+Fundo+de+Garantia+do+Tempo+de+Servi%C3%A7o",
        "CEF/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Caixa+Econ%C3%B4mica+Federal",
        "CMN/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Conselho+Monet%C3%A1rio+Nacional",
        "CNPS/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Previd%C3%AAncia+Social&orgSub=Conselho+Nacional+de+Previd%C3%AAncia+Social",
        "COAF/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Banco+Central+do+Brasil&orgSub=Conselho+de+Controle+de+Atividades+Financeiras",
        "CODEFAT/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+do+Trabalho+e+Emprego&orgSub=Conselho+Deliberativo+do+Fundo+de+Amparo+ao+Trabalhador",
        "CONFAZ/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Conselho+Nacional+de+Pol%C3%ADtica+Fazend%C3%A1ria",
        "Congresso Nacional/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=do1&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Atos+do+Congresso+Nacional",
        "CONTRAN/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+dos+Transportes&orgSub=Conselho+Nacional+de+Tr%C3%A2nsito",
        "Gabinete-MCOM/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+das+Comunica%C3%A7%C3%B5es&orgSub=Gabinete+do+Ministro",
        "Gabinete-MCTI/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Ci%C3%AAncia%2C+Tecnologia+e+Inova%C3%A7%C3%A3o&orgSub=Gabinete+da+Ministra",
        "Gabinete-MDR/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Integra%C3%A7%C3%A3o+e+do+Desenvolvimento+Regional&orgSub=Gabinete+do+Ministro",
        "Gabinete-ME/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Economia&orgSub=Gabinete+do+Ministro",
        "Gabinete-MF/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Gabinete+do+Ministro",
        "Gabinete-Minfra/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Ministerio+da+Infraestrutura&orgSub=Gabinete+do+Ministro",
        "Gabinete-MJSP/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Justi%C3%A7a+e+Seguran%C3%A7a+P%C3%BAblica&orgSub=Gabinete+do+Ministro",
        "Gabinete-MPS/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Previd%C3%AAncia+Social&orgSub=Gabinete+do+Ministro",
        "Gabinete-MTE/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+do+Trabalho+e+Emprego&orgSub=Gabinete+do+Ministro",
        "Gabinete-MTP/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+do+Trabalho+e+Previd%C3%AAncia&orgSub=Gabinete+do+Ministro",
        "INSS/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Previd%C3%AAncia+Social&orgSub=Instituto+Nacional+do+Seguro+Social",
        "PGFN/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Procuradoria-Geral+da+Fazenda+Nacional",
        "Poder Executivo/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Atos+do+Poder+Executivo",
        "Poder Legislativo/DOU": [
            f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Poder+Legislativo",
            f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Atos+do+Poder+Legislativo"
        ],
        "Receita Federal/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Secretaria+Especial+da+Receita+Federal+do+Brasil",
        "SE-Casa Cívil/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Presid%C3%AAncia+da+Rep%C3%BAblica&orgSub=Casa+Civil",
        "SEDDM/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Economia&orgSub=Secretaria+Especial+de+Desestatiza%C3%A7%C3%A3o%2C+Desinvestimento+e+Mercados",
        "SEDGG/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Ministerio+da+Economia&orgSub=Secretaria+Especial+de+Desburocratiza%C3%A7%C3%A3o,+Gest%C3%A3o+e+Governo+Digital",
        "SFPP/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Infraestrutura&orgSub=Secretaria+de+Fomento%2C+Planejamento+e+Parcerias",
        "STN/DOU": f"https://www.in.gov.br/consulta/-/buscar/dou?q=*&s=todos&exactDate=personalizado&sortType=0&delta=20&publishFrom={encoded_start_date}&publishTo={encoded_end_date}&orgPrin=Minist%C3%A9rio+da+Fazenda&orgSub=Secretaria+do+Tesouro+Nacional",
        # Outras origens conforme necessário
    }
    async with ClientSession() as session:
        tasks = [asyncio.create_task(fetch_data(session, name, url)) for name, url in links.items()]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    start_date = "15/05/2024"
    end_date = "21/05/2024"
    results = await fetch_all_data(start_date, end_date)
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
