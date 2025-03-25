from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# MongoDB connection settings
mongo_uri = "mongodb+srv://lbprod-pri.cuho0.mongodb.net/?authMechanism=MONGODB-X509&authSource=%24external&tls=true&tlsCertificateKeyFile=C%3A%5CUsers%5Cwilli%5COneDrive%5CDocumentos%5CAcessos%5CAcesso+ao+MongoDB%5CX509-cert-4384389572589510418.pem"
database_name = "normas"
collection_name = "rawDou"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

# Function to generate a range of dates
def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y")
    delta = timedelta(days=1)
    current = start
    while current <= end:
        yield current.strftime("%d/%m/%Y")
        current += delta

# Function to process date fields
def processa_data_campo(campo):
    if isinstance(campo, dict) and "$date" in campo:
        return datetime.strptime(campo.get("$date")[:-5], "%Y-%m-%dT%H:%M:%S")
    elif isinstance(campo, datetime):
        return campo
    else:
        return None

# Set date range for the query
start_date = "01/08/2024"
end_date = "30/10/2024"

# Prepare NDJSON output data
ndjson_data = {}

# Iterate through each date in the range
for query_date in generate_date_range(start_date, end_date):
    # Query for retrieving documents
    query = {
        "sirius_status": 4,
        "data_publicacao_dou": query_date,
        "secao": "1"
    }

    # Retrieve documents based on the query
    documents = collection.find(query)

    # Prepare data for Excel and NDJSON
    data = []
    for doc in documents:
        # Processa os campos de data
        done_at_utc = processa_data_campo(doc.get("done_at"))
        created_at_utc = processa_data_campo(doc.get("created_at"))
        doing_at_utc = processa_data_campo(doc.get("doing_at"))

        if done_at_utc and created_at_utc and doing_at_utc:
            # Convert times to local (UTC-3) time
            local_done_at = done_at_utc - timedelta(hours=3)
            local_created_at = created_at_utc - timedelta(hours=3)
            local_doing_at = doing_at_utc - timedelta(hours=3)

            # Format times
            original_done_at_str = done_at_utc.strftime("%d/%m/%Y - %H:%M:%S")
            local_done_at_str = local_done_at.strftime("%d/%m/%Y - %H:%M:%S")

            original_created_at_str = created_at_utc.strftime("%d/%m/%Y - %H:%M:%S")
            local_created_at_str = local_created_at.strftime("%d/%m/%Y - %H:%M:%S")

            original_doing_at_str = doing_at_utc.strftime("%d/%m/%Y - %H:%M:%S")
            local_doing_at_str = local_doing_at.strftime("%d/%m/%Y - %H:%M:%S")

            # Calculate execution time
            tempo_execucao = done_at_utc - created_at_utc
            tempo_execucao_str = "{:02d}:{:02d}:{:02d}".format(
                tempo_execucao.seconds // 3600,
                (tempo_execucao.seconds // 60) % 60,
                tempo_execucao.seconds % 60
            )

            # Add to data list for Excel and NDJSON
            record = {
                "_id": str(doc.get("_id")),
                "Secao": doc.get("secao"),
                "Titulo": doc.get("titulo"),
                "Tipo": doc.get("tipo"),
                "Origem": doc.get("origem"),
                "Link": doc.get("link"),
                "Original Created At (UTC)": original_created_at_str,
                "Local Created At (UTC-3)": local_created_at_str,
                "Original Doing At (UTC)": original_doing_at_str,
                "Local Doing At (UTC-3)": local_doing_at_str,
                "Original Done At (UTC)": original_done_at_str,
                "Local Done At (UTC-3)": local_done_at_str,
                "Tempo de Execução": tempo_execucao_str
            }
            data.append(record)

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Save the data to an Excel file with a sheet name based on the query date, replacing invalid characters
    safe_query_date = query_date.replace("/", "-")
    output_file = "normativos_secao_1.xlsx"

    # Check if the sheet already exists and handle accordingly
    if os.path.exists(output_file):
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            if safe_query_date in writer.book.sheetnames:
                print(f"Sheet for date {query_date} already exists. Skipping...")
            else:
                df.to_excel(writer, sheet_name=safe_query_date, index=False)
    else:
        with pd.ExcelWriter(output_file, mode='w', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=safe_query_date, index=False)

    print(f"Data for {query_date} has been successfully processed.")

    # Add data to NDJSON output structure under the current date
    if data:
        ndjson_data[safe_query_date] = data

# Save all data to NDJSON file in a structured manner
ndjson_output_file = "normativos_secao_1.ndjson"
with open(ndjson_output_file, 'w') as ndjson_file:
    ndjson_file.write(json.dumps(ndjson_data, indent=4))

print(f"NDJSON data has been successfully saved to {ndjson_output_file}")