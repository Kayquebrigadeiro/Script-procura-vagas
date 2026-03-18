"""
Bot LinkedIn - Estrutura atualizada 2025
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bot_base import BotBase
from utils import (
    logger, esperar_elemento, esperar_clicavel, clicar_seguro,
    digitar_humano, scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA, PERFIL, LIMITES

class LinkedInBot(BotBase):
    """Bot para candidaturas no LinkedIn"""
    
    def __init__(self, driver):
        super().__init__(driver, "linkedin")
        self.base_url = "https://www.linkedin.com"
    
    def fazer_login(self) -> bool:
        """Verifica se está logado no LinkedIn"""
        try:
            logger.info("🔐 Verificando login no LinkedIn...")
            self.driver.get(f"{self.base_url}/feed/")
            time.sleep(3)
            
            # Verifica se está na página de feed (logado)
            if "/feed" in self.driver.current_url or "/mynetwork" in self.driver.current_url:
                logger.info("✅ Já está logado no LinkedIn")
                return True
            
            # Se não está logado, pede para fazer login manual
            logger.warning("❌ Não está logado no LinkedIn")
            logger.warning("\n" + "="*60)
            logger.warning("⚠️  AÇÃO NECESSÁRIA: FAÇA LOGIN MANUALMENTE")
            logger.warning("="*60)
            logger.warning("1. O Chrome está aberto na página de login")
            logger.warning("2. Faça login com seu email e senha")
            logger.warning("3. Aguarde carregar o feed")
            logger.warning("4. Volte aqui e pressione ENTER")
            logger.warning("="*60)
            
            self.driver.get(f"{self.base_url}/login")
            input("\n>>> Pressione ENTER após fazer login no LinkedIn... ")
            
            time.sleep(2)
            if "/feed" in self.driver.current_url or "/mynetwork" in self.driver.current_url:
                logger.info("✅ Login confirmado!")
                return True
            else:
                logger.error("❌ Login não detectado")
                return False
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas no LinkedIn"""
        try:
            # Monta URL de busca
            localizacao = BUSCA["localizacao"]
            url = f"{self.base_url}/jobs/search/?"
            url += f"keywords={palavra_chave.replace(' ', '%20')}"
            url += f"&location={localizacao.replace(' ', '%20')}"
            
            # Adiciona filtro Easy Apply se configurado
            if BUSCA["linkedin"]["easy_apply_only"]:
                url += "&f_AL=true"
            
            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            # Scroll para carregar mais vagas
            logger.info("📜 Carregando vagas...")
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)
            
            # Busca cards de vagas - SELETORES ATUALIZADOS 2025
            vagas = []
            
            # Tenta diferentes seletores (LinkedIn muda frequentemente)
            seletores_cards = [
                "ul.scaffold-layout__list-container > li",
                "div.jobs-search-results__list > ul > li",
                "li.jobs-search-results__list-item",
                "div.job-card-container",
                "li[data-occludable-job-id]"
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
            for card in cards[:20]:  # Limita a 20 primeiras vagas
                try:
                    # Tenta extrair título
                    titulo_elem = None
                    seletores_titulo = [
                        "a.job-card-list__title",
                        "a.job-card-container__link",
                        "span.job-card-list__title--link",
                        "a[data-control-name='job_card_title']"
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
                    
                    # Tenta extrair empresa
                    empresa = "Não informado"
                    seletores_empresa = [
                        "span.job-card-container__primary-description",
                        "div.artdeco-entity-lockup__subtitle",
                        "span.job-card-container__company-name"
                    ]
                    
                    for sel in seletores_empresa:
                        try:
                            empresa_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if empresa_elem:
                                empresa = empresa_elem.text.strip()
                                break
                        except:
                            continue
                    
                    # Extrai ID da vaga
                    vaga_id = extrair_id_vaga(url_vaga, "linkedin")
                    if not vaga_id:
                        # Tenta pegar do atributo data
                        try:
                            vaga_id = card.get_attribute("data-occludable-job-id")
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
        """Envia candidatura para uma vaga no LinkedIn"""
        try:
            # Abre a vaga
            logger.info(f"   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            
            scroll_aleatorio(self.driver, 2)
            
            # DETECTA VAGAS EXTERNAS (gerenciadas fora do LinkedIn)
            try:
                vaga_externa = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'Respostas gerenciadas fora do LinkedIn')] | "
                    "//*[contains(text(), 'site de empregos')]"
                )
                
                if vaga_externa:
                    logger.info(f"   ⚠️ Vaga externa detectada (gerenciada fora do LinkedIn)")
                    logger.info(f"   💾 Salvando para candidatura manual...")
                    
                    # Salva em arquivo para candidatura manual
                    with open("c:\\safadeza\\vagas_externas_linkedin.txt", "a", encoding="utf-8") as f:
                        f.write(f"{vaga['titulo']} | {vaga['empresa']} | {vaga['url']}\n")
                    
                    logger.info(f"   ✅ Vaga salva em: vagas_externas_linkedin.txt")
                    return False  # Não conta como candidatura automática
            except Exception as e:
                logger.debug(f"Erro ao verificar vaga externa: {e}")
            
            # Procura botão de candidatura - SELETORES ATUALIZADOS 2025
            logger.info(f"   🔍 Procurando botão de candidatura...")
            
            botao_apply = None
            seletores_apply = [
                "button.jobs-apply-button[data-live-test-job-apply-button]",
                "button.jobs-apply-button",
                "button[aria-label*='Easy Apply']",
                "button[aria-label*='Candidatura simplificada']"
            ]
            
            for sel in seletores_apply:
                try:
                    botao_apply = esperar_clicavel(self.driver, By.CSS_SELECTOR, sel, timeout=5)
                    if botao_apply:
                        break
                except:
                    continue
            
            if not botao_apply:
                logger.info(f"   ⚠️ Botão de candidatura não encontrado")
                return False
            
            # Clica no botão
            logger.info(f"   ✅ Botão encontrado! Clicando...")
            if not clicar_seguro(self.driver, botao_apply):
                return False
            
            time.sleep(2)
            
            # Preenche formulário Easy Apply
            logger.info(f"   📝 Preenchendo formulário...")
            
            max_etapas = 10
            for etapa in range(max_etapas):
                delay_humano(1, 2)
                
                # Preenche telefone se necessário
                try:
                    campos_telefone = self.driver.find_elements(By.CSS_SELECTOR, 
                        "input[id*='phoneNumber'], input[name*='phone']")
                    for campo in campos_telefone:
                        if not campo.get_attribute("value"):
                            campo.clear()
                            digitar_humano(campo, PERFIL["telefone"])
                except:
                    pass
                
                # Preenche selects (escolhe primeira opção válida)
                try:
                    selects = self.driver.find_elements(By.TAG_NAME, "select")
                    for select in selects:
                        if select.get_attribute("value") == "":
                            options = select.find_elements(By.TAG_NAME, "option")
                            if len(options) > 1:
                                options[1].click()
                except:
                    pass
                
                # Marca radio buttons "Sim"
                try:
                    radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    for radio in radios:
                        label = radio.get_attribute("aria-label") or ""
                        if "sim" in label.lower() or "yes" in label.lower():
                            if not radio.is_selected():
                                clicar_seguro(self.driver, radio)
                except:
                    pass
                
                delay_humano(0.5, 1)
                
                # Procura botões de ação
                botao_enviar = None
                botao_proximo = None
                botao_revisar = None
                
                # Botão Enviar/Submit
                seletores_enviar = [
                    "button[aria-label*='Submit']",
                    "button[aria-label*='Enviar']",
                    "button:has-text('Submit application')",
                    "button:has-text('Enviar candidatura')"
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
                
                # Botão Próximo/Next
                if not botao_enviar:
                    seletores_proximo = [
                        "button[aria-label*='Continue']",
                        "button[aria-label*='Continuar']",
                        "button[aria-label*='Next']",
                        "button[aria-label*='Próximo']"
                    ]
                    
                    for sel in seletores_proximo:
                        try:
                            botao_proximo = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if botao_proximo and botao_proximo.is_displayed():
                                break
                            else:
                                botao_proximo = None
                        except:
                            continue
                
                # Botão Revisar/Review
                if not botao_enviar and not botao_proximo:
                    seletores_revisar = [
                        "button[aria-label*='Review']",
                        "button[aria-label*='Revisar']"
                    ]
                    
                    for sel in seletores_revisar:
                        try:
                            botao_revisar = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if botao_revisar and botao_revisar.is_displayed():
                                break
                            else:
                                botao_revisar = None
                        except:
                            continue
                
                # Executa ação
                if botao_enviar:
                    logger.info(f"   🚀 Enviando candidatura...")
                    clicar_seguro(self.driver, botao_enviar)
                    time.sleep(3)
                    
                    # Fecha modal de confirmação se aparecer
                    try:
                        botao_fechar = self.driver.find_element(By.CSS_SELECTOR, 
                            "button[aria-label*='Dismiss'], button[data-test-modal-close-btn]")
                        clicar_seguro(self.driver, botao_fechar)
                    except:
                        pass
                    
                    return True
                
                elif botao_revisar:
                    logger.info(f"   ➡️  Indo para revisão...")
                    clicar_seguro(self.driver, botao_revisar)
                
                elif botao_proximo:
                    logger.info(f"   ➡️  Próxima etapa...")
                    clicar_seguro(self.driver, botao_proximo)
                
                else:
                    logger.warning(f"   ⚠️ Nenhum botão encontrado na etapa {etapa + 1}")
                    break
            
            logger.warning(f"   ❌ Não foi possível completar o formulário")
            return False
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar: {e}")
            return False
