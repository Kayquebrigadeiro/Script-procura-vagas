# -*- coding: utf-8 -*-
"""
Teste específico do LinkedIn - Debug detalhado
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import config

print("="*60)
print("TESTE LINKEDIN - DEBUG DETALHADO")
print("="*60)

# Conecta ao Chrome
print("\n1. Conectando ao Chrome...")
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", f"localhost:{config.CHROME['debug_port']}")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
print("   ✅ Conectado!")

# Vai para uma vaga de teste
print("\n2. Abrindo vaga de teste...")
print("   Cole a URL de uma vaga do LinkedIn que você quer testar:")
url_vaga = input("   URL: ").strip()

driver.get(url_vaga)
time.sleep(3)

# Procura botão de candidatura
print("\n3. Procurando botão 'Candidatar-se'...")

seletores = [
    ("CSS", "button.jobs-apply-button"),
    ("CSS", "button[class*='jobs-apply-button']"),
    ("XPATH", "//button[contains(@class, 'jobs-apply-button')]"),
    ("XPATH", "//button[contains(., 'Candidatar-se')]"),
    ("XPATH", "//button[contains(., 'Easy Apply')]"),
]

botao_encontrado = None
for tipo, seletor in seletores:
    try:
        if tipo == "CSS":
            botao = driver.find_element(By.CSS_SELECTOR, seletor)
        else:
            botao = driver.find_element(By.XPATH, seletor)
        
        if botao and botao.is_displayed():
            print(f"   ✅ BOTÃO ENCONTRADO com {tipo}: {seletor}")
            print(f"      Texto: {botao.text}")
            print(f"      Visível: {botao.is_displayed()}")
            print(f"      Habilitado: {botao.is_enabled()}")
            botao_encontrado = botao
            break
    except Exception as e:
        print(f"   ❌ {tipo} '{seletor}' não funcionou")

if not botao_encontrado:
    print("\n   ⚠️ NENHUM BOTÃO ENCONTRADO!")
    print("\n   Vou listar todos os botões da página:")
    botoes = driver.find_elements(By.TAG_NAME, "button")
    for i, btn in enumerate(botoes[:20], 1):
        try:
            texto = btn.text[:50] if btn.text else "(sem texto)"
            classes = btn.get_attribute("class")[:50] if btn.get_attribute("class") else "(sem classe)"
            print(f"   {i}. Texto: {texto} | Classes: {classes}")
        except:
            pass
    
    driver.quit()
    exit()

# Tenta clicar
print("\n4. Tentando clicar no botão...")
try:
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_encontrado)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", botao_encontrado)
    print("   ✅ CLIQUE EXECUTADO!")
    time.sleep(3)
except Exception as e:
    print(f"   ❌ Erro ao clicar: {e}")
    driver.quit()
    exit()

# Verifica se abriu o modal
print("\n5. Verificando se abriu o formulário...")
try:
    # Procura elementos do formulário Easy Apply
    modal = driver.find_element(By.CSS_SELECTOR, "div[role='dialog'], div.jobs-easy-apply-modal")
    print("   ✅ MODAL ABERTO!")
    
    # Procura botões de ação
    print("\n6. Procurando botões de ação no formulário...")
    
    botoes_acao = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Submit') or contains(@aria-label, 'Enviar') or contains(@aria-label, 'Next') or contains(@aria-label, 'Próximo')]")
    
    if botoes_acao:
        print(f"   ✅ Encontrou {len(botoes_acao)} botões:")
        for i, btn in enumerate(botoes_acao, 1):
            aria = btn.get_attribute("aria-label")
            texto = btn.text
            print(f"   {i}. aria-label: {aria} | texto: {texto}")
    else:
        print("   ⚠️ Nenhum botão de ação encontrado")
        print("\n   Listando todos os botões do modal:")
        todos_botoes = modal.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(todos_botoes, 1):
            try:
                aria = btn.get_attribute("aria-label") or "(sem aria-label)"
                texto = btn.text or "(sem texto)"
                print(f"   {i}. aria: {aria[:50]} | texto: {texto[:50]}")
            except:
                pass

except Exception as e:
    print(f"   ❌ Modal não encontrado: {e}")
    print("\n   Vou tirar um screenshot...")
    driver.save_screenshot("c:\\safadeza\\debug_erro.png")
    print("   📸 Screenshot salvo: debug_erro.png")

print("\n" + "="*60)
print("TESTE CONCLUÍDO!")
print("="*60)
print("\nO Chrome vai ficar aberto para você inspecionar.")
print("Pressione ENTER para fechar...")
input()

driver.quit()
