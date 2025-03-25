import asyncio
import pandas as pd
import os
import re
import time
from dou import fetch_all_data
from request_platform import request_counts_by_origin

# Limite de execução paralela
MAX_CONCURRENT_SCRIPTS = 4

# Função para buscar dados do DOU e plataforma
async def fetch_data_for_date(start_date, end_date):
    dou_task = asyncio.create_task(fetch_all_data(start_date, end_date))
    request_platform_task = asyncio.to_thread(request_counts_by_origin, start_date, end_date)

    results_dou, results_request_platform = await asyncio.gather(dou_task, request_platform_task)

    # Processando os dados do DOU
    if isinstance(results_dou, list) and all(isinstance(item, str) for item in results_dou):
        data_dou = [item.split(": ") for item in results_dou if ": " in item]
        df_dou = pd.DataFrame(data_dou, columns=[f'DOU Origem {start_date}', f'DOU Resultado {start_date}'])
    else:
        df_dou = pd.DataFrame(results_dou)

    # Processando os dados da Platform
    df_platform = pd.DataFrame.from_dict(results_request_platform, orient='index', columns=[f'Platform Resultado {start_date}'])
    df_platform.reset_index(inplace=True)
    df_platform.rename(columns={'index': f'Platform Origem {start_date}'}, inplace=True)

    return df_dou, df_platform

# Função para executar um script específico
async def run_script(script_name, folder, start_date, end_date, semaphore):
    async with semaphore:  # Limita o número de execuções paralelas
        start_time = time.time()
        try:
            print(f"Iniciando script: {script_name}")
            process = await asyncio.create_subprocess_exec(
                'python', f'{folder}/{script_name}.py', start_date, end_date,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            stdout_decoded = stdout.decode(errors='ignore')  # Ignora caracteres inválidos
            stderr_decoded = stderr.decode(errors='ignore')  # Ignora caracteres inválidos
            print(stdout_decoded)
            print(stderr_decoded)
            
            # Capturando a origem e o total_count da saída do script
            origin_match = re.search(r"ORIGIN:(.+)", stdout_decoded)
            total_count_match = re.search(r"TOTAL_COUNT:(\d+)", stdout_decoded)
            origin = origin_match.group(1).strip() if origin_match else script_name
            total_count = int(total_count_match.group(1)) if total_count_match else 0
            
            end_time = time.time()
            print(f"Finalizado script: {script_name} | Origem: {origin} | Total: {total_count} | Tempo: {end_time - start_time:.2f}s")
            return origin, total_count
        except Exception as e:
            end_time = time.time()
            print(f"Erro ao executar o script {script_name}.py na pasta {folder}: {e} | Tempo: {end_time - start_time:.2f}s")
            return script_name, 0

# Função principal
async def main():
    start_main_time = time.time()
    date_ranges = [
        ("18/03/2025", "24/03/2025"),
        ("25/03/2025", "25/03/2025")
    ]

    # Scripts que você quer rodar junto com suas pastas
    scripts = [
        ("bndes", "bndes"),
        ("cvm", "spiders"),
        ("anp", "spiders"),
        ("anvisa", "spiders"),
        ("b3", "spiders"),
        ("planalto", "spiders"),
        ("receita_federal", "spiders"),#
        ("aneel", "spiders"),#
        ("cfatf", "spiders"),#
        ("cnbv", "spiders"),#
        ("ecfr", "spiders"),
        ("fatf", "spiders"), #
        ("fincen", "spiders"),
        ("finra", "spiders"),
        ("frb", "spiders"),
        ("mxdof", "spiders")
        
    ]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SCRIPTS)
    all_dfs = []

    for start_date, end_date in date_ranges:
        df_dou, df_platform = await fetch_data_for_date(start_date, end_date)
        
        tasks = [run_script(script, folder, start_date, end_date, semaphore) for script, folder in scripts]
        results = await asyncio.gather(*tasks)

        for origin, total_count in results:
            new_row = pd.DataFrame({f'DOU Origem {start_date}': [origin], f'DOU Resultado {start_date}': [total_count]})
            df_dou = pd.concat([df_dou, new_row], ignore_index=True)

        all_dfs.extend([df_dou, df_platform])

    df_combined = pd.concat(all_dfs, axis=1)

    excel_path = 'data.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_combined.to_excel(writer, sheet_name='Combined Data', index=False)

    # Abrindo o arquivo Excel automaticamente após salvá-lo
    if os.name == 'nt':  # para Windows
        os.startfile(excel_path)

    end_main_time = time.time()
    print(f"Tempo total de execução do script principal: {(end_main_time - start_main_time) / 60:.2f} minutos")

if __name__ == "__main__":
    asyncio.run(main())
