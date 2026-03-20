"""
Bot de Candidaturas Automáticas — Catho
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import LIMITES, CHROME
from utils import logger
from catho_bot import CathoBot

def conectar_chrome():
    try:
        logger.info("🔌 Conectando ao Chrome...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{CHROME['debug_port']}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✅ Conectado ao Chrome!")
        return driver
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        logger.error("⚠️  Execute abrir_chrome.bat ANTES de rodar este script")
        return None

def perguntar_quantidade() -> int:
    print("\n" + "="*60)
    print("🤖 BOT DE CANDIDATURAS — CATHO")
    print("="*60)
    while True:
        try:
            valor = input("\nQuantas vagas você quer se candidatar hoje? (1-50): ").strip()
            qtd = int(valor)
            if 1 <= qtd <= 50:
                return qtd
            print("❌ Digite um número entre 1 e 50.")
        except ValueError:
            print("❌ Digite apenas um número.")

def main():
    qtd = perguntar_quantidade()

    # Sobrescreve o limite do config com o que o usuário escolheu
    LIMITES["max_candidaturas_por_site"] = qtd

    logger.info(f"🎯 Meta definida: {qtd} candidatura(s)")
    logger.info("="*60 + "\n")

    driver = conectar_chrome()
    if not driver:
        return

    try:
        bot = CathoBot(driver)
        total = bot.executar()
        logger.info("\n" + "="*60)
        logger.info("🎉 BOT FINALIZADO!")
        logger.info(f"✅ Candidaturas enviadas: {total} de {qtd} solicitadas")
        logger.info(f"📁 Histórico: c:\\safadeza\\candidaturas.json")
        logger.info(f"📁 Logs: c:\\safadeza\\bot.log")
        logger.info("="*60 + "\n")
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {e}")
    finally:
        logger.info("👋 Encerrando...")

if __name__ == "__main__":
    main()
