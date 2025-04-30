#!/usr/bin/env python3
# whatsapp_local_setup.py
# Abre o WhatsApp Web em modo visível para autenticar e enviar mensagem de teste.

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# — Ajuste aqui —
PROFILE_DIR = Path.home() / ".whatsapp_playwright"  # onde a sessão será salva
GROUP_NAME  = "Meu Grupo DQ"                        # nome exato do grupo WhatsApp
TEST_MESSAGE = "✅ Teste de notificação DQ Monitor funcionando!"  

def send_whatsapp_test(message: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,                # EXPLICITAMENTE não-headless
            args=["--start-maximized"]     # opcional: maximiza a janela
        )
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        print("→ Escaneie o QR code no WhatsApp Web para autenticar...")
        # aguarda até o grupo aparecer na lista (até 2 minutos)
        page.wait_for_selector(f"text={GROUP_NAME}", timeout=120_000)
        print(f"→ Grupo '{GROUP_NAME}' encontrado, abrindo chat...")
        page.click(f"text={GROUP_NAME}")
        # aguarda a caixa de mensagem
        page.wait_for_selector("div[contenteditable='true'][data-tab='10']")
        inp = page.locator("div[contenteditable='true'][data-tab='10']")
        inp.click()
        inp.type(message)
        inp.press("Enter")
        print("→ Mensagem enviada. Aguarde alguns segundos e feche a janela.")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    # Cria a pasta de perfil, se não existir
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    send_whatsapp_test(TEST_MESSAGE)
