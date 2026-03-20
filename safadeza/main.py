"""
Bot de Candidaturas Automáticas
LinkedIn | Catho | InfoJobs | Indeed
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import LIMITES, CHROME
from utils import logger, tracker, delay_humano

# Importa os bots
from linkedin_bot import LinkedInBot
from catho_bot import CathoBot
from infojobs_bot import InfoJobsBot
from indeed_bot import IndeedBot

def conectar_chrome():
    """Conecta ao Chrome já aberto com debug port"""
    try:
        logger.info("🔌 Conectando ao Chrome...")
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{CHROME['debug_port']}")
        
        # Usa webdriver-manager para gerenciar o ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Conectado ao Chrome com sucesso!")
        return driver
    
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao Chrome: {e}")
        logger.error("\n⚠️  CERTIFIQUE-SE DE:")
        logger.error("1. Executar 'abrir_chrome.bat' ANTES de rodar este script")
        logger.error("2. O Chrome deve estar aberto com a porta de debug 9222")
        return None

def main():
    """Função principal"""
    logger.info("\n" + "="*60)
    logger.info("🤖 BOT DE CANDIDATURAS AUTOMÁTICAS")
    logger.info("="*60)
    logger.info("📋 Sites: LinkedIn, Catho, InfoJobs, Indeed")
    logger.info(f"🎯 Meta: {LIMITES['max_candidaturas_total']} candidaturas totais")
    logger.info(f"📊 Limite por site: {LIMITES['max_candidaturas_por_site']}")
    logger.info("="*60 + "\n")
    
    # Conecta ao Chrome
    driver = conectar_chrome()
    if not driver:
        logger.error("❌ Não foi possível conectar ao Chrome. Encerrando.")
        return
    
    try:
        total_candidaturas = 0
        
        # Lista de bots para executar
        bots = [
            LinkedInBot(driver),
            CathoBot(driver),
            InfoJobsBot(driver),
            IndeedBot(driver)
        ]
        
        # Executa cada bot
        for bot in bots:
            if total_candidaturas >= LIMITES["max_candidaturas_total"]:
                logger.info(f"\n🎯 META TOTAL ATINGIDA: {total_candidaturas} candidaturas!")
                break
            
            try:
                candidaturas = bot.executar()
                total_candidaturas += candidaturas
                
                logger.info(f"\n📊 PROGRESSO GERAL: {total_candidaturas}/{LIMITES['max_candidaturas_total']}")
                
                # Delay entre sites
                if total_candidaturas < LIMITES["max_candidaturas_total"]:
                    delay = LIMITES["delay_entre_sites"]
                    logger.info(f"⏳ Aguardando {delay}s antes do próximo site...\n")
                    delay_humano(delay, delay + 3)
            
            except Exception as e:
                logger.error(f"❌ Erro ao executar bot {bot.nome_site}: {e}")
                continue
        
        # Relatório final
        logger.info("\n" + "="*60)
        logger.info("🎉 BOT FINALIZADO!")
        logger.info("="*60)
        logger.info(f"✅ Total de candidaturas enviadas: {total_candidaturas}")
        logger.info(f"📊 LinkedIn: {tracker.candidaturas_por_site('linkedin')}")
        logger.info(f"📊 Catho: {tracker.candidaturas_por_site('catho')}")
        logger.info(f"📊 InfoJobs: {tracker.candidaturas_por_site('infojobs')}")
        logger.info(f"📊 Indeed: {tracker.candidaturas_por_site('indeed')}")
        logger.info("="*60)
        logger.info(f"📁 Histórico salvo em: candidaturas.json")
        logger.info(f"📁 Logs salvos em: bot.log")
        logger.info("="*60 + "\n")
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Bot interrompido pelo usuário")
    
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {e}")
    
    finally:
        logger.info("\n👋 Encerrando...")
        # NÃO fecha o driver para manter o Chrome aberto
        # driver.quit()

if __name__ == "__main__":
    main()
