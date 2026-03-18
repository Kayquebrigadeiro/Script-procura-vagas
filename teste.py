# -*- coding: utf-8 -*-
"""
Script de Teste - Verifica se tudo esta configurado corretamente
"""

import sys
from pathlib import Path

print("="*60)
print("TESTE DE CONFIGURACAO")
print("="*60)

# Testa imports
print("\n1. Testando imports...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("   OK Selenium OK")
except Exception as e:
    print(f"   ERRO Erro no Selenium: {e}")
    sys.exit(1)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("   OK WebDriver Manager OK")
except Exception as e:
    print(f"   ERRO Erro no WebDriver Manager: {e}")
    sys.exit(1)

try:
    import config
    print("   OK Config OK")
except Exception as e:
    print(f"   ERRO Erro no Config: {e}")
    sys.exit(1)

try:
    import utils
    print("   OK Utils OK")
except Exception as e:
    print(f"   ERRO Erro no Utils: {e}")
    sys.exit(1)

try:
    from linkedin_bot import LinkedInBot
    from catho_bot import CathoBot
    from infojobs_bot import InfoJobsBot
    from indeed_bot import IndeedBot
    print("   OK Todos os bots OK")
except Exception as e:
    print(f"   ERRO Erro nos bots: {e}")
    sys.exit(1)

# Verifica curriculo
print("\n2. Verificando curriculo...")
curriculo = Path(config.PERFIL["curriculo_path"])
if curriculo.exists():
    print(f"   OK Curriculo encontrado: {curriculo}")
else:
    print(f"   AVISO Curriculo nao encontrado: {curriculo}")
    print(f"   Ajuste o caminho em config.py")

# Verifica configuracoes
print("\n3. Verificando configuracoes...")
print(f"   Email: {config.PERFIL['email']}")
print(f"   Telefone: {config.PERFIL['telefone']}")
print(f"   Localizacao: {config.BUSCA['localizacao']}")
print(f"   Palavras-chave: {len(config.BUSCA['palavras_chave'])}")
print(f"   Meta por site: {config.LIMITES['max_candidaturas_por_site']}")
print(f"   Meta total: {config.LIMITES['max_candidaturas_total']}")

# Testa conexao Chrome (se estiver aberto)
print("\n4. Testando conexao com Chrome...")
try:
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"localhost:{config.CHROME['debug_port']}")
    
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print(f"   OK Conectado ao Chrome!")
    print(f"   URL atual: {driver.current_url}")
    
    driver.quit()

except Exception as e:
    print(f"   AVISO Chrome nao esta aberto com debug port")
    print(f"   Execute 'abrir_chrome.bat' primeiro")

print("\n" + "="*60)
print("TESTE CONCLUIDO!")
print("="*60)
print("\nPROXIMOS PASSOS:")
print("1. Execute: abrir_chrome.bat")
print("2. Faca login nos 4 sites (LinkedIn, Catho, InfoJobs, Indeed)")
print("3. Execute: python main.py")
print("\nBoa sorte!")
print("="*60)
