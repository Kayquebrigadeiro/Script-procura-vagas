"""
Bot Indeed - Corrigido 2026
Fixes: removido button:has-text(), false positive return True, confirmação real
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot_base import BotBase
from utils import (
    logger, clicar_seguro, digitar_humano,
    scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA, PERFIL

class IndeedBot(BotBase):
    """Bot para candidaturas no Indeed"""

    def __init__(self, driver):
        super().__init__(driver, "indeed")
        self.base_url = "https://br.indeed.com"

    def fazer_login(self) -> bool:
        try:
            logger.info("🔐 Verificando login no Indeed...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente")
            return True
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False

    def buscar_vagas(self, palavra_chave: str) -> list:
        try:
            localizacao = BUSCA["localizacao"]
            url = (
                f"{self.base_url}/jobs?"
                f"q={palavra_chave.replace(' ', '+')}"
                f"&l={localizacao.replace(' ', '+')}"
                f"&fromage=7"
            )

            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)

            seletores_cards = [
                "div.job_seen_beacon",
                "div[data-jk]",
                "li.css-5lfssm",
            ]

            cards = []
            for seletor in seletores_cards:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    if cards:
                        logger.info(f"✅ {len(cards)} cards com: {seletor}")
                        break
                except:
                    continue

            if not cards:
                logger.warning("⚠️ Nenhum card encontrado no Indeed")
                return []

            vagas = []
            for card in cards[:20]:
                try:
                    # Título
                    titulo = None
                    seletores_titulo = [
                        "h2.jobTitle a span",
                        "h2.jobTitle span[title]",
                        "a.jcs-JobTitle span",
                        "h2 span[id]",
                    ]
                    for sel in seletores_titulo:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, sel)
                            if el and el.text.strip():
                                titulo = el.text.strip()
                                break
                        except:
                            continue

                    if not titulo:
                        try:
                            titulo = card.find_element(By.CSS_SELECTOR, "h2").text.strip()
                        except:
                            continue

                    # URL
                    url_vaga = None
                    try:
                        link = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a, a.jcs-JobTitle")
                        url_vaga = link.get_attribute("href")
                    except:
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
                        "span[data-testid='company-name']",
                        "span.companyName",
                        "div.company_location span",
                    ]
                    for sel in seletores_empresa:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, sel)
                            if el and el.text.strip():
                                empresa = el.text.strip()
                                break
                        except:
                            continue

                    vaga_id = extrair_id_vaga(url_vaga, "indeed")
                    if not vaga_id:
                        try:
                            vaga_id = card.get_attribute("data-jk")
                        except:
                            vaga_id = url_vaga[-20:]

                    vagas.append({
                        "id": vaga_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_vaga,
                    })

                except Exception as e:
                    logger.debug(f"Erro ao processar card Indeed: {e}")
                    continue

            return vagas

        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas Indeed: {e}")
            return []

    def candidatar_vaga(self, vaga: dict) -> bool:
        try:
            logger.info("   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            scroll_aleatorio(self.driver, 2)

            # Procura botão Indeed Apply — seletores CSS apenas (sem has-text)
            logger.info("   🔍 Procurando botão de candidatura...")
            botao = None

            seletores_css = [
                "button#indeedApplyButton",
                "button[data-testid='indeedApplyButton-test']",
                "button.indeed-apply-button",
                "button[class*='indeed-apply']",
            ]
            for sel in seletores_css:
                try:
                    botao = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                    )
                    if botao:
                        break
                except:
                    continue

            # Fallback XPath por texto
            if not botao:
                xpaths = [
                    "//button[contains(., 'Candidatar-se')]",
                    "//button[contains(., 'Apply now')]",
                    "//button[contains(@aria-label, 'Candidatar')]",
                ]
                for xp in xpaths:
                    try:
                        botao = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, xp))
                        )
                        if botao:
                            break
                    except:
                        continue

            if not botao:
                logger.info("   ⚠️ Botão não encontrado — vaga pode redirecionar para site externo")
                return False

            logger.info("   ✅ Botão encontrado! Clicando...")
            clicar_seguro(self.driver, botao)
            time.sleep(3)

            # Preenche campos básicos
            self._preencher_campos()

            # Navega pelas etapas
            for etapa in range(6):
                time.sleep(1.5)

                # Verifica confirmação real
                try:
                    corpo = self.driver.find_element(By.TAG_NAME, "body").text
                    if any(t in corpo for t in [
                        "Candidatura enviada",
                        "Application submitted",
                        "Sua candidatura foi enviada",
                        "candidatura foi enviada com sucesso",
                    ]):
                        logger.info(f"   🎉 Candidatura CONFIRMADA!")
                        return True
                except:
                    pass

                # Botão Enviar
                botao_enviar = self._encontrar_botao_xpath([
                    "//button[@type='submit' and contains(., 'Enviar')]",
                    "//button[contains(., 'Enviar candidatura')]",
                    "//button[contains(., 'Submit application')]",
                    "//button[contains(@class, 'ia-continueButton') and contains(., 'Enviar')]",
                ])

                if botao_enviar:
                    logger.info(f"   🚀 Enviando (etapa {etapa + 1})...")
                    clicar_seguro(self.driver, botao_enviar)
                    time.sleep(3)

                    # Verifica confirmação após envio
                    try:
                        corpo = self.driver.find_element(By.TAG_NAME, "body").text
                        if any(t in corpo for t in [
                            "Candidatura enviada",
                            "Application submitted",
                        ]):
                            logger.info("   🎉 Candidatura CONFIRMADA!")
                            return True
                    except:
                        pass

                    logger.warning("   ⚠️ Enviou mas não confirmou — verifique manualmente")
                    return False

                # Botão Continuar/Próximo
                botao_continuar = self._encontrar_botao_xpath([
                    "//button[contains(., 'Continuar')]",
                    "//button[contains(., 'Continue')]",
                    "//button[contains(., 'Próximo')]",
                    "//button[contains(., 'Next')]",
                    "//button[@class and contains(@class, 'ia-continueButton')]",
                ])

                if botao_continuar:
                    logger.info(f"   ➡️  Avançando etapa {etapa + 1}...")
                    clicar_seguro(self.driver, botao_continuar)
                    self._preencher_campos()
                    delay_humano(1, 2)
                    continue

                logger.warning(f"   ⚠️ Nenhum botão encontrado na etapa {etapa + 1}")
                break

            return False

        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar Indeed: {e}")
            return False

    def _preencher_campos(self):
        """Preenche campos de formulário quando aparecerem"""
        try:
            # Telefone
            for sel in ["input[name*='phoneNumber']", "input[id*='phone']", "input[name*='phone']"]:
                try:
                    campos = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    for campo in campos:
                        if not campo.get_attribute("value") and campo.is_displayed():
                            campo.clear()
                            digitar_humano(campo, PERFIL["telefone"])
                except:
                    continue

            # Email
            for sel in ["input[type='email']", "input[name*='email']"]:
                try:
                    campos = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    for campo in campos:
                        if not campo.get_attribute("value") and campo.is_displayed():
                            campo.clear()
                            digitar_humano(campo, PERFIL["email"])
                except:
                    continue
        except:
            pass

    def _encontrar_botao_xpath(self, xpaths: list):
        """Tenta encontrar botão por lista de XPaths"""
        for xp in xpaths:
            try:
                el = self.driver.find_element(By.XPATH, xp)
                if el and el.is_displayed() and el.is_enabled():
                    return el
            except:
                continue
        return None
