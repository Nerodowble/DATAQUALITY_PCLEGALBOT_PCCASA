# Importa os scripts filhos como módulos
import anbima_administracao_de_recursos_de_terceiros
import anbima_atividades_conveniadas
import anbima_certificacao
import anbima_circulares_supervisao
import anbima_circulares
import anbima_comunicado
import anbima_distribuicao_de_produtos_de_investimento
import anbima_negociacao_de_instrumentos_financeiros
import anbima_noticias
import anbima_oficios
import anbima_servicos_qualificados

from datetime import datetime

# Script Pai
def anbima(data_desejada):
    # Converte a data para o formato esperado pelos scripts filhos
    try:
        data_desejada_formatada = datetime.strptime(data_desejada, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError as e:
        print(f"Erro ao converter a data: {e}")
        return

    resultados = []  # Lista para armazenar os resultados de cada script filho
    scripts_alterados = []  # Lista para armazenar os nomes dos scripts com alterações

    # Dicionário de funções dos scripts filhos
    funcoes_filhas = {
        'anbima_administracao_de_recursos_de_terceiros': anbima_administracao_de_recursos_de_terceiros.anbima_administracao_de_recursos_de_terceiros,
        'anbima_atividades_conveniadas': anbima_atividades_conveniadas.anbima_atividades_conveniadas,
        'anbima_certificacao': anbima_certificacao.anbima_certificacao,
        'anbima_circulares_supervisao': anbima_circulares_supervisao.anbima_circulares_supervisao,
        'anbima_circulares': anbima_circulares.anbima_circulares,
        'anbima_comunicado': anbima_comunicado.anbima_comunicado,
        'anbima_distribuicao_de_produtos_de_investimento': anbima_distribuicao_de_produtos_de_investimento.anbima_distribuicao_de_produtos_de_investimento,
        'anbima_negociacao_de_instrumentos_financeiros': anbima_negociacao_de_instrumentos_financeiros.anbima_negociacao_de_instrumentos_financeiros,
        'anbima_noticias': anbima_noticias.noticias,
        'anbima_oficios': anbima_oficios.oficios,
        'anbima_servicos_qualificados': anbima_servicos_qualificados.anbima_servicos_qualificados,
    }

    for nome_script, funcao in funcoes_filhas.items():
        if nome_script == 'anbima_administracao_de_recursos_de_terceiros':
            resultado = funcao()  # Chama a função do script filho sem argumentos
        else:
            resultado = funcao(data_desejada_formatada)  # Chama a função do script filho com a data desejada formatada
        resultados.append(resultado)  # Adiciona o resultado à lista de resultados

        if resultado != 0:
            scripts_alterados.append(nome_script)  # Adiciona o nome do script alterado à lista

    # Imprime os resultados de cada script filho
    for nome_script, resultado in zip(funcoes_filhas.keys(), resultados):
        print(f'{nome_script}: {resultado}')

    # Verifica se houve scripts com alterações
    if scripts_alterados:
        print("\nScripts com alterações:")
        for script in scripts_alterados:
            print(script)

        print(f'Data desejada: {data_desejada}')  # Imprime a data desejada

    # Retorna a soma total dos resultados
    return sum(resultados)

# Exemplo de uso
data_desejada = "18/06/2024"  # Substitua com a data desejada
resultados = anbima(data_desejada)
print(f"\nTotal de diferenças encontradas: {resultados}")
