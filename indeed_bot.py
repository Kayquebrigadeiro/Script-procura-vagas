"""
Bot Indeed - Estrutura atualizada 2025
"""

import time
from selenium.webdriver.common.by import By
from bot_base import BotBase
from utils import (
    logger, esperar_elemento, esperar_clicavel, clicar_seguro,
    digitar_humano, scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA, PERFIL

class IndeedBot(BotBase):
    """Bot para candidaturas no Indeed"""
    
    def __init__(self, driver):
        super().__init__(driver, "indeed")
        self.base_url = "https://br.indeed.com"
    
    def fazer_login(self) -> bool:
        """Verifica se está logado no Indeed"""
        try:
            logger.info("🔐 Verificando login no Indeed...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente quando o site pedir")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas no Indeed"""
        try:
            # Monta URL de busca
            localizacao = BUSCA["localizacao"]
            url = f"{self.base_url}/jobs?"
            url += f"q={palavra_chave.replace(' ', '+')}"
            url += f"&l={localizacao.replace(' ', '+')}"
            
            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll para carregar mais vagas
            logger.info("📜 Carregando vagas...")
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)
            
            # Busca cards de vagas - SELETORES INDEED 2025
            vagas = []
            
            seletores_cards = [
                "div.job_seen_beacon",
                "div.jobsearch-SerpJobCard",
                "div[data-jk]",
                "li.css-5lfssm",
                "div.slider_item"
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
                        "h2.jobTitle a",
                        "a.jcs-JobTitle",
                        "h2 span[title]",
                        "a[data-jk]"
                    ]
                    
                    for sel in seletores_titulo:
                        try:
                            titulo_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if titulo_elem:
                                break
                        except:
                            continue
                    
                    if not titulo_elem:
                        # Tenta pegar título de outra forma
                        try:
                            titulo_elem = card.find_element(By.CSS_SELECTOR, "h2")
                        except:
                            continue
                    
                    titulo = titulo_elem.text.strip()
                    
                    # URL da vaga
                    url_vaga = None
                    try:
                        link = card.find_element(By.CSS_SELECTOR, "a")
                        url_vaga = link.get_attribute("href")
                    except:
                        # Tenta construir URL a partir do data-jk
                        try:
                            jk = card.get_attribute("data-jk")
                            if jk:
                                url_vaga = f"{self.base_url}/viewjob?jk={jk}"
                        except:
                            continue
                    
                    if not url_vaga:
                        continue
                    
                    # Empresa
                    empresa = "Não informado"
                    seletores_empresa = [
                        "span.companyName",
                        "span[data-testid='company-name']",
                        "div.company_location span"
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
                    vaga_id = extrair_id_vaga(url_vaga, "indeed")
                    if not vaga_id:
                        try:
                            vaga_id = card.get_attribute("data-jk")
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
        """Envia candidatura para uma vaga no Indeed"""
        try:
            # Abre a vaga
            logger.info(f"   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            
            scroll_aleatorio(self.driver, 2)
            
            # Procura botão de candidatura - SELETORES INDEED 2025
            logger.info(f"   🔍 Procurando botão de candidatura...")
            
            botao_candidatar = None
            seletores_candidatar = [
                "button#indeedApplyButton",
                "button[data-testid='indeedApplyButton-test']",
                "button.indeed-apply-button",
                "button:has-text('Candidatar-se')"
            ]
            
            for sel in seletores_candidatar:
                try:
                    botao_candidatar = esperar_clicavel(self.driver, By.CSS_SELECTOR, sel, timeout=5)
                    if botao_candidatar:
                        break
                except:
                    continue
            
            if not botao_candidatar:
                logger.info(f"   ⚠️ Botão de candidatura não encontrado (pode ser redirecionamento externo)")
                return False
            
            # Clica no botão
            logger.info(f"   ✅ Botão encontrado! Clicando...")
            if not clicar_seguro(self.driver, botao_candidatar):
                return False
            
            time.sleep(3)
            
            # Indeed Apply - Preenche formulário
            try:
                # Telefone
                campos_telefone = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[name*='phoneNumber'], input[id*='phone']")
                for campo in campos_telefone:
                    if not campo.get_attribute("value"):
                        campo.clear()
                        digitar_humano(campo, PERFIL["telefone"])
                
                # Email (caso peça)
                campos_email = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[type='email'], input[name*='email']")
                for campo in campos_email:
                    if not campo.get_attribute("value"):
                        campo.clear()
                        digitar_humano(campo, PERFIL["email"])
                
                delay_humano(1, 2)
                
                # Procura botões de continuar/enviar
                max_etapas = 5
                for etapa in range(max_etapas):
                    botao_continuar = None
                    botao_enviar = None
                    
                    # Botão Enviar
                    seletores_enviar = [
                        "button[type='submit']",
                        "button:has-text('Enviar candidatura')",
                        "button:has-text('Submit application')",
                        "button.ia-continueButton"
                    ]
                    
                    for sel in seletores_enviar:
                        try:
                            botao_enviar = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if botao_enviar and botao_enviar.is_displayed():
                                break
                            else:
                                botao_enviar = None
                        except:
                            continue
                    
                    # Botão Continuar
                    if not botao_enviar:
                        seletores_continuar = [
                            "button:has-text('Continuar')",
                            "button:has-text('Continue')",
                            "button:has-text('Próximo')",
                            "button:has-text('Next')"
                        ]
                        
                        for sel in seletores_continuar:
                            try:
                                botao_continuar = self.driver.find_element(By.CSS_SELECTOR, sel)
                                if botao_continuar and botao_continuar.is_displayed():
                                    break
                                else:
                                    botao_continuar = None
                            except:
                                continue
                    
                    if botao_enviar:
                        logger.info(f"   🚀 Enviando candidatura...")
                        clicar_seguro(self.driver, botao_enviar)
                        time.sleep(2)
                        return True
                    
                    elif botao_continuar:
                        logger.info(f"   ➡️  Continuando...")
                        clicar_seguro(self.driver, botao_continuar)
                        delay_humano(1, 2)
                    
                    else:
                        break
            
            except:
                pass
            
            logger.info(f"   ✅ Candidatura enviada!")
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar: {e}")
            return False
