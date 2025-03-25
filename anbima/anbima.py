import re
import sys
from datetime import datetime
import inspect

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

# Função principal para executar os scripts filhos
def anbima(start_date, end_date):
    try:
        # Converte a data final para o formato esperado pelos scripts filhos
        data_desejada_formatada = datetime.strptime(end_date, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError as e:
        print(f"Erro ao converter a data: {e}")
        print("ORIGIN:anbima")
        print("TOTAL_COUNT:0")
        return

    total_diferencas = 0  # Contador para armazenar o total de diferenças

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
        try:
            num_args = len(inspect.signature(funcao).parameters)
            if num_args == 0:
                resultado = funcao()  # Chama a função do script filho sem argumentos
            elif num_args == 1:
                resultado = funcao(data_desejada_formatada)  # Chama a função do script filho com um argumento
            else:
                print(f"Função {nome_script} espera {num_args} argumentos. Ajuste necessário.", file=sys.stderr)
                continue
            
            if isinstance(resultado, int):
                total_diferencas += resultado
            else:
                print(f"Resultado inválido do script {nome_script}. Esperado um inteiro, obtido {type(resultado)}", file=sys.stderr)
        
        except Exception as e:
            print(f"Erro ao executar o script {nome_script}: {e}", file=sys.stderr)
    
    # Imprimindo a origem e o total_count para serem capturados pelo script main.py
    print("ORIGIN:anbima")
    print(f"TOTAL_COUNT:{total_diferencas}")

    return total_diferencas

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python anbima.py <data_inicio> <data_fim>", file=sys.stderr)
        print("ORIGIN:anbima")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    if not re.match(r"\d{2}/\d{2}/\d{4}", start_date) or not re.match(r"\d{2}/\d{2}/\d{4}", end_date):
        print("Formato de data inválido. Use DD/MM/YYYY.", file=sys.stderr)
        print("ORIGIN:anbima")
        print("TOTAL_COUNT:0")
        sys.exit(1)

    resultados = anbima(start_date, end_date)
    print(f"\nTotal de diferenças encontradas: {resultados}")
