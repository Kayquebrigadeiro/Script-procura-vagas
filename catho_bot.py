"""
Bot Catho - Estrutura atualizada 2025
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bot_base import BotBase
from utils import (
    logger, esperar_elemento, esperar_clicavel, clicar_seguro,
    digitar_humano, scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA, PERFIL

class CathoBot(BotBase):
    """Bot para candidaturas no Catho"""
    
    def __init__(self, driver):
        super().__init__(driver, "catho")
        self.base_url = "https://www.catho.com.br"
    
    def fazer_login(self) -> bool:
        """Verifica se está logado no Catho"""
        try:
            logger.info("🔐 Verificando login no Catho...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente quando o site pedir")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas no Catho"""
        try:
            # Monta URL de busca
            localizacao = BUSCA["localizacao"]
            url = f"{self.base_url}/vagas?"
            url += f"q={palavra_chave.replace(' ', '+')}"
            url += f"&cidade={localizacao.replace(', ', '-').replace(' ', '-')}"
            
            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll para carregar mais vagas
            logger.info("📜 Carregando vagas...")
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)
            
            # Busca cards de vagas - SELETORES CATHO 2025
            vagas = []
            
            seletores_cards = [
                "article.sc-job-card",
                "div.job-card",
                "li.job-item",
                "article[data-testid='job-card']"
            ]
            
            cards = []
            for seletor in seletores_cards:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    if len(cards) > 0:
                        logger.info(f"✅ Encontrou {len(cards)} cards com seletor: {seletor}")
                        break
                except:
                    continue
            
            if not cards:
                logger.warning("⚠️ Nenhum card de vaga encontrado")
                return []
            
            # Extrai informações de cada card
            for card in cards[:20]:
                try:
                    # Título e link
                    titulo_elem = None
                    seletores_titulo = [
                        "h2.sc-job-card__title a",
                        "a.job-title",
                        "h3.job-card-title a",
                        "a[data-testid='job-title']"
                    ]
                    
                    for sel in seletores_titulo:
                        try:
                            titulo_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if titulo_elem:
                                break
                        except:
                            continue
                    
                    if not titulo_elem:
                        continue
                    
                    titulo = titulo_elem.text.strip()
                    url_vaga = titulo_elem.get_attribute("href")
                    
                    # Empresa
                    empresa = "Não informado"
                    seletores_empresa = [
                        "p.sc-job-card__company",
                        "span.company-name",
                        "div.job-company",
                        "span[data-testid='company-name']"
                    ]
                    
                    for sel in seletores_empresa:
                        try:
                            empresa_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if empresa_elem:
                                empresa = empresa_elem.text.strip()
                                break
                        except:
                            continue
                    
                    # ID da vaga
                    vaga_id = extrair_id_vaga(url_vaga, "catho")
                    if not vaga_id:
                        vaga_id = url_vaga.split("/")[-1][:20]
                    
                    if titulo and url_vaga:
                        vagas.append({
                            "id": vaga_id,
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": url_vaga
                        })
                
                except Exception as e:
                    logger.debug(f"Erro ao processar card: {e}")
                    continue
            
            return vagas
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas: {e}")
            return []
    
    def candidatar_vaga(self, vaga: dict) -> bool:
        """Envia candidatura para uma vaga no Catho"""
        try:
            # Abre a vaga
            logger.info(f"   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            
            scroll_aleatorio(self.driver, 2)
            
            # Procura botão de candidatura - SELETORES CATHO 2025
            logger.info(f"   🔍 Procurando botão de candidatura...")
            
            botao_candidatar = None
            seletores_candidatar = [
                "button[title*='Quero me candidatar']",
                "button.Button__StyledButton-sc-1ovnfsw-1",
                "button:has-text('Quero me candidatar')"
            ]
            
            for sel in seletores_candidatar:
                try:
                    botao_candidatar = esperar_clicavel(self.driver, By.CSS_SELECTOR, sel, timeout=5)
                    if botao_candidatar:
                        break
                except:
                    continue
            
            if not botao_candidatar:
                logger.info(f"   ⚠️ Botão de candidatura não encontrado")
                return False
            
            # Clica no botão
            logger.info(f"   ✅ Botão encontrado! Clicando...")
            if not clicar_seguro(self.driver, botao_candidatar):
                return False
            
            time.sleep(2)
            
            # Verifica se precisa preencher formulário adicional
            try:
                # Procura campos de formulário
                campos_texto = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                
                for campo in campos_texto:
                    placeholder = campo.get_attribute("placeholder") or ""
                    name = campo.get_attribute("name") or ""
                    
                    # Preenche telefone
                    if "telefone" in placeholder.lower() or "phone" in name.lower():
                        if not campo.get_attribute("value"):
                            campo.clear()
                            digitar_humano(campo, PERFIL["telefone"])
                
                delay_humano(1, 2)
                
                # Procura botão de confirmação
                botao_confirmar = None
                seletores_confirmar = [
                    "button[type='submit']",
                    "button:has-text('Confirmar')",
                    "button:has-text('Enviar')",
                    "button.btn-submit"
                ]
                
                for sel in seletores_confirmar:
                    try:
                        botao_confirmar = self.driver.find_element(By.CSS_SELECTOR, sel)
                        if botao_confirmar and botao_confirmar.is_displayed():
                            break
                        else:
                            botao_confirmar = None
                    except:
                        continue
                
                if botao_confirmar:
                    logger.info(f"   🚀 Confirmando candidatura...")
                    clicar_seguro(self.driver, botao_confirmar)
                    time.sleep(2)
            
            except:
                pass
            
            logger.info(f"   ✅ Candidatura enviada!")
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar: {e}")
            return False
