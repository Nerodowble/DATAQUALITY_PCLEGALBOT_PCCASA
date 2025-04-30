#!/usr/bin/env python3
# main.py
# 1) Autentica na API DQ
# 2) Busca os contadores DQ
# 3) Analisa divergências
# 4) Envia UMA única notificação no WhatsApp Web (Playwright)

import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ——— Configurações DQ API ———
API_HOST = "https://api.legalbot.com.br"
USERNAME = "willian.lima@legalbot.com.br"
PASSWORD = "Trymore1@3$5"

# ——— Configurações WhatsApp Web ———
PROFILE_DIR = Path.home() / ".whatsapp_playwright"
GROUP_NAME  = "Meu Grupo DQ"  # nome exato do grupo criado manualmente

def generate_token(user: str, pwd: str) -> str:
    resp = requests.post(
        f"{API_HOST}/sec/auth/token",
        json={"username": user, "password": pwd},
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    return resp.json()["bearer"]

def fetch_all_counters(token: str, from_dt: str, to_dt: str) -> list:
    all_items, page, per_page = [], 1, 100
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    while True:
        payload = {
            "page": {"order_by":[{}], "page_number": page, "per_page": per_page},
            "filter": {"include":[], "exclude":[], "from_dt": from_dt, "to_dt": to_dt}
        }
        resp = requests.post(f"{API_HOST}/dq-api/counter/list", headers=headers, json=payload)
        resp.raise_for_status()
        items = resp.json().get("result", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < per_page:
            break
        page += 1
    return all_items

def extract_divergences(counters: list) -> list:
    utc_tz = ZoneInfo("UTC")
    br_tz  = ZoneInfo("America/Sao_Paulo")
    diverg = []
    for itm in counters:
        s, d = itm.get("scrap_count", 0), itm.get("dq_count", 0)
        if s != d:
            iso_ts = itm.get("scheduler", {}).get("last_dq_fetch") or ""
            try:
                dt_utc = datetime.fromisoformat(iso_ts).replace(tzinfo=utc_tz)
                dt_br  = dt_utc.astimezone(br_tz)
                ts = dt_br.strftime("%d/%m/%Y às %H:%M:%S")
            except Exception:
                ts = iso_ts
            diverg.append({
                "origin": itm.get("origin", "N/A"),
                "scrap":  s,
                "dq":     d,
                "diff":   s - d,
                "ts":     ts
            })
    return diverg

def send_whatsapp(divs: list):
    if not PROFILE_DIR.exists():
        print(f"ERRO: perfil WhatsApp não encontrado em {PROFILE_DIR}.", file=sys.stderr)
        print("  Execute primeiro o whatsapp_local_setup.py para autenticar.", file=sys.stderr)
        return

    # Monta a mensagem
    header = "*⚠️ Alerta DQ Monitor*"
    subtitle = "_Origens com divergência:_"
    lines = [header, subtitle, ""]
    for d in divs:
        lines.append(
            f"• *{d['origin']}* — scrap={d['scrap']}  dq={d['dq']}  diff={d['diff']}  @ {d['ts']}"
        )
    body = "\n".join(lines)

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/114.0.0.0 Safari/537.36"
            )
        )
        page = browser.new_page()

        # Logs para debug
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Erro: {err}"))

        page.goto("https://web.whatsapp.com")
        page.wait_for_load_state("networkidle", timeout=180_000)

        # Bypass automação
        page.evaluate("""
            () => {
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [
                    { name: 'Chrome PDF Plugin' },
                    { name: 'Chrome PDF Viewer' }
                ]});
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            }
        """
        )

        # Autenticação QR code
        if page.locator("canvas[aria-label='Scan this QR code with WhatsApp']").is_visible(timeout=30_000):
            print(
                "ERRO: Sessão inválida. Autentique novamente com whatsapp_local_setup.py.",
                file=sys.stderr
            )
            browser.close()
            return

        # Seleciona grupo
        try:
            page.wait_for_selector(f"text={GROUP_NAME}", timeout=180_000)
            page.click(f"text={GROUP_NAME}")
        except PlaywrightTimeoutError:
            print(
                "ERRO: Não foi possível encontrar o grupo. Verifique o nome do grupo.",
                file=sys.stderr
            )
            browser.close()
            return

        # Envia mensagem
        try:
            inp = page.locator("div[contenteditable='true'][data-tab='10']")
            page.wait_for_selector(
                "div[contenteditable='true'][data-tab='10']",
                timeout=60_000
            )

            # Foco e clique
            for attempt in range(1, 4):
                try:
                    inp.focus()
                    time.sleep(1)
                    inp.click(timeout=10_000)
                    break
                except PlaywrightTimeoutError:
                    print(f"Tentativa {attempt} de clique falhou.", file=sys.stderr)
                    if attempt == 3:
                        print(
                            "ERRO: Não foi possível clicar no campo de texto após 3 tentativas.",
                            file=sys.stderr
                        )
                        browser.close()
                        return

            inp.fill(body)
            inp.press("Enter")

            # Espera que o balão de mensagem com o header apareça
            try:
                page.wait_for_selector(
                    f"div.message-out:has-text('{header}')",
                    timeout=60_000
                )
            except PlaywrightTimeoutError:
                print(
                    "ERRO: tempo esgotado esperando confirmação de envio.",
                    file=sys.stderr
                )

            # Espera extra para garantir envio antes de fechar
            time.sleep(10)
        except PlaywrightTimeoutError:
            print(
                "ERRO: Não foi possível localizar o campo de texto.",
                file=sys.stderr
            )
        finally:
            browser.close()


def main(from_date: str, to_date: str):
    try:
        f = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        t = datetime.strptime(to_date,   "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("Use o formato DD/MM/YYYY para as datas.", file=sys.stderr)
        sys.exit(1)

    token    = generate_token(USERNAME, PASSWORD)
    counters = fetch_all_counters(token, f, t)
    diverg   = extract_divergences(counters)

    if not diverg:
        print("Nenhuma divergência encontrada.")
    else:
        for d in diverg:
            print(f"{d['origin']}: diff={d['diff']} @ {d['ts']}")
        send_whatsapp(diverg)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main.py <from_date> <to_date>", file=sys.stderr)
        print("Exemplo: python main.py 28/04/2025 28/04/2025", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
