#!/usr/bin/env python3
# dq_monitor_analyze.py
# Autentica, busca os contadores DQ no /dq-api/counter/list e lista as origens com divergência,
# convertendo last_dq_fetch de UTC para hora de Brasília (America/Sao_Paulo).

import requests
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

API_HOST = "https://api.legalbot.com.br"
USERNAME = "willian.lima@legalbot.com.br"   # ajuste se necessário
PASSWORD = "Trymore1@3$5"                  # ajuste se necessário

def generate_token(username: str, password: str) -> str:
    url = f"{API_HOST}/sec/auth/token"
    resp = requests.post(
        url,
        json={"username": username, "password": password},
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    return resp.json()["bearer"]

def fetch_counters_page(token: str, from_dt: str, to_dt: str, page: int, per_page: int = 100) -> dict:
    url = f"{API_HOST}/dq-api/counter/list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "page": {
            "order_by": [{}],
            "page_number": page,
            "per_page": per_page
        },
        "filter": {
            "include": [],
            "exclude": [],
            "from_dt": from_dt,
            "to_dt": to_dt
        }
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def fetch_all_counters(token: str, from_dt: str, to_dt: str) -> list:
    all_items = []
    page = 1
    per_page = 100

    while True:
        data = fetch_counters_page(token, from_dt, to_dt, page, per_page)
        items = data.get("result", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < per_page:
            break
        page += 1

    return all_items

def analyze_divergences(counters: list):
    print("Origens com divergência:\n")
    found = False
    utc_tz = ZoneInfo("UTC")
    br_tz  = ZoneInfo("America/Sao_Paulo")

    for item in counters:
        scrap = item.get("scrap_count", 0)
        dq    = item.get("dq_count", 0)
        if scrap != dq:
            found = True
            diff = scrap - dq
            iso_ts = item.get("scheduler", {}).get("last_dq_fetch")
            if iso_ts:
                try:
                    # assumir ISO como UTC e converter para Brasília
                    dt_utc = datetime.fromisoformat(iso_ts).replace(tzinfo=utc_tz)
                    dt_br  = dt_utc.astimezone(br_tz)
                    ts = dt_br.strftime("%d/%m/%Y às %H:%M:%S")
                except Exception:
                    ts = iso_ts
            else:
                ts = "N/A"

            print(
                f"{item.get('origin','N/A'):<30}"
                f"scrap={scrap:>3}  "
                f"dq={dq:>3}  "
                f"diff={diff:>3}  "
                f"last_dq_fetch={ts}"
            )

    if not found:
        print("Nenhuma divergência encontrada.")

def main(from_date: str, to_date: str):
    # converte DD/MM/YYYY → YYYY-MM-DD
    try:
        f = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        t = datetime.strptime(to_date,   "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("Use o formato DD/MM/YYYY para as datas.", file=sys.stderr)
        sys.exit(1)

    token = generate_token(USERNAME, PASSWORD)
    counters = fetch_all_counters(token, f, t)
    analyze_divergences(counters)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python dq_monitor_analyze.py <from_date> <to_date>", file=sys.stderr)
        print("Exemplo: python dq_monitor_analyze.py 28/04/2025 28/04/2025", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
