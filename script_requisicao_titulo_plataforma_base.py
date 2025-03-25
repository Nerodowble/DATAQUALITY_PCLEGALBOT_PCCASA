import http.client
import json
from datetime import datetime

def generate_token():
    conn = http.client.HTTPSConnection("api.legalbot.com.br")
    payload = json.dumps({
        "username": "willian.lima@legalbot.com.br",
        "password": "Trymore1@3$5"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/sec/auth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token = json.loads(data.decode("utf-8"))["bearer"]
    return token

def request_counts_by_origin(start_date, end_date, origens=None):
    if origens is None:
        origens = [
                "AGU/DOU",
]
    start_date_fmt = datetime.strptime(start_date, '%d/%m/%Y').strftime('%Y-%m-%d')
    end_date_fmt = datetime.strptime(end_date, '%d/%m/%Y').strftime('%Y-%m-%d')

    token = generate_token()
    conn = http.client.HTTPSConnection("api.legalbot.com.br")
    results = {}

    for origem in origens:
        payload = json.dumps({
            "sort": [],
            "should": {},
            "must":{
                "title":"AUTORIZAÇÃO SDL-ANP Nº 5, DE 2 DE JANEIRO DE 2023 - DOU DE 03-01-2023." #AQUI VAI O TITULO REQUISITADO
            },
            "must_not": {},
            "filter": {
                "term_filters": {
                    "origin": [origem]
                },
                "range_filters": {
                    "issuance_date": {
                        "gte": start_date_fmt,
                        "lte": end_date_fmt
                    }
                }
            },
            "aggs": {
                "term_aggs": [
                    "origin",
                    "norm_type"
                ]
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        conn.request("POST", "/norms/norms/search_count", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))
        total = response_data.get("total", 0)
        results[origem] = total

    return results

if __name__ == "__main__":
    start_date = "14/03/2025"
    end_date = "14/03/2025"
    results = request_counts_by_origin(start_date, end_date)
    print(results)