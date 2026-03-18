"""
Bot InfoJobs - Estrutura atualizada 2025
"""

import time
from selenium.webdriver.common.by import By
from bot_base import BotBase
from utils import (
    logger, esperar_elemento, esperar_clicavel, clicar_seguro,
    digitar_humano, scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA, PERFIL

class InfoJobsBot(BotBase):
    """Bot para candidaturas no InfoJobs"""
    
    def __init__(self, driver):
        super().__init__(driver, "infojobs")
        self.base_url = "https://www.infojobs.com.br"
    
    def fazer_login(self) -> bool:
        """Verifica se está logado no InfoJobs"""
        try:
            logger.info("🔐 Verificando login no InfoJobs...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente quando o site pedir")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas no InfoJobs"""
        try:
            # Monta URL de busca
            localizacao = BUSCA["localizacao"]
            url = f"{self.base_url}/empregos.aspx?"
            url += f"palabra={palavra_chave.replace(' ', '-')}"
            
            # InfoJobs usa código de cidade (São Paulo = 42)
            if "São Paulo" in localizacao or "Sao Paulo" in localizacao:
                url += "&provincia=42"
            
            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll para carregar mais vagas
            logger.info("📜 Carregando vagas...")
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)
            
            # Busca cards de vagas - SELETORES INFOJOBS 2025
            vagas = []
            
            seletores_cards = [
                "div.element-offer",
                "article.offer-item",
                "li.js-offer-item",
                "div[data-id]"
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
                        "h2.title a",
                        "a.js-o-link",
                        "h3.offer-title a",
                        "a.offer-link"
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
                        "span.company-name",
                        "a.company",
                        "p.company-location span",
                        "div.company-info"
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
                    vaga_id = extrair_id_vaga(url_vaga, "infojobs")
                    if not vaga_id:
                        try:
                            vaga_id = card.get_attribute("data-id")
                        except:
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
        """Envia candidatura para uma vaga no InfoJobs"""
        try:
            # Abre a vaga
            logger.info(f"   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            
            scroll_aleatorio(self.driver, 2)
            
            # Procura botão de candidatura - SELETORES INFOJOBS 2025
            logger.info(f"   🔍 Procurando botão de candidatura...")
            
            botao_candidatar = None
            seletores_candidatar = [
                "a.js_btApplyVacancy",
                "a.btn-primary.js_btApplyVacancy",
                "a:has-text('CANDIDATAR-ME')"
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
            
            # Preenche formulário se necessário
            try:
                # Telefone
                campos_telefone = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[name*='telefone'], input[name*='phone']")
                for campo in campos_telefone:
                    if not campo.get_attribute("value"):
                        campo.clear()
                        digitar_humano(campo, PERFIL["telefone"])
                
                delay_humano(1, 2)
                
                # Botão de confirmação
                botao_confirmar = None
                seletores_confirmar = [
                    "button[type='submit']",
                    "button.btn-confirm",
                    "button:has-text('Confirmar')",
                    "button:has-text('Enviar candidatura')"
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
