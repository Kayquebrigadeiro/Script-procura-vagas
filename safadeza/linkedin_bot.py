"""
Bot LinkedIn - Criado do zero com seletores corretos 2026
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot_base import BotBase
from utils import (
    logger, esperar_elemento, esperar_clicavel, clicar_seguro,
    scroll_aleatorio, delay_humano, extrair_id_vaga
)
from config import BUSCA

VAGAS_EXTERNAS_FILE = "c:\\safadeza\\vagas_externas_linkedin.txt"

class LinkedInBot(BotBase):
    """Bot para candidaturas no LinkedIn via Easy Apply"""

    def __init__(self, driver):
        super().__init__(driver, "linkedin")
        self.base_url = "https://www.linkedin.com"
        self.vagas_externas = []

    def fazer_login(self) -> bool:
        """Verifica se está logado no LinkedIn"""
        try:
            logger.info("🔐 Verificando login no LinkedIn...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)

            url_atual = self.driver.current_url
            if "feed" in url_atual or "mynetwork" in url_atual:
                logger.info("✅ Já está logado no LinkedIn")
                return True

            if "login" in url_atual or "checkpoint" in url_atual:
                logger.warning("⚠️  Não está logado — faça login manualmente no Chrome e execute novamente")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False

    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas no LinkedIn"""
        try:
            from urllib.parse import quote
            localizacao = BUSCA["localizacao"]
            q = quote(palavra_chave)
            loc = quote(localizacao)

            # f_AL=true filtra só Easy Apply
            url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={q}&location={loc}"
                f"&f_E=2&sortBy=DD"
            )

            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)

            scroll_aleatorio(self.driver, 4)
            time.sleep(2)

            # Seletores de cards 2026
            seletores_cards = [
                "li.jobs-search-results__list-item",
                "div.job-card-container",
                "li[class*='jobs-search-results']",
                "div[data-job-id]",
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
                logger.warning("⚠️  Nenhum card encontrado no LinkedIn")
                return []

            vagas = []
            for card in cards[:20]:
                try:
                    # Clica no card para carregar detalhes no painel lateral
                    try:
                        clicar_seguro(self.driver, card)
                        time.sleep(1.5)
                    except:
                        pass

                    # Título
                    titulo = None
                    seletores_titulo = [
                        "h2.t-24.t-bold.inline",
                        "h1.t-24",
                        "h2[class*='job-title']",
                        "a[class*='job-card-list__title']",
                        "span[aria-hidden='true']",
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
                        continue

                    # Link da vaga
                    url_vaga = None
                    try:
                        link = card.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                        url_vaga = link.get_attribute("href").split("?")[0]
                    except:
                        try:
                            job_id = card.get_attribute("data-job-id") or card.get_attribute("data-occludable-job-id")
                            if job_id:
                                url_vaga = f"https://www.linkedin.com/jobs/view/{job_id}/"
                        except:
                            continue

                    if not url_vaga:
                        continue

                    # Empresa
                    empresa = "Não informado"
                    seletores_empresa = [
                        "span.job-card-container__primary-description",
                        "a[class*='job-card-container__company']",
                        "span[class*='company']",
                        "div.job-card-container__company-name",
                    ]
                    for sel in seletores_empresa:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, sel)
                            if el and el.text.strip():
                                empresa = el.text.strip()
                                break
                        except:
                            continue

                    vaga_id = extrair_id_vaga(url_vaga, "linkedin") or url_vaga.split("/")[-2]

                    vagas.append({
                        "id": vaga_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_vaga,
                    })

                except Exception as e:
                    logger.debug(f"Erro ao processar card LinkedIn: {e}")
                    continue

            logger.info(f"LinkedIn: {len(vagas)} vagas encontradas")
            return vagas

        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas LinkedIn: {e}")
            return []

    def candidatar_vaga(self, vaga: dict) -> bool:
        """Envia candidatura via Easy Apply no LinkedIn"""
        try:
            logger.info(f"   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)

            # Verifica se é vaga externa (sem Easy Apply)
            try:
                texto_pagina = self.driver.find_element(By.TAG_NAME, "body").text
                if "Respostas gerenciadas fora do LinkedIn" in texto_pagina:
                    logger.info("   ↪️  Vaga externa — salvando para candidatura manual")
                    self._salvar_vaga_externa(vaga)
                    return False
            except:
                pass

            # Procura botão Easy Apply — seletores 2026
            logger.info("   🔍 Procurando botão Easy Apply...")
            botao = None

            # Tenta CSS primeiro
            seletores_css = [
                "button.jobs-apply-button[data-live-test-job-apply-button]",
                "button.jobs-apply-button",
                "button[class*='jobs-apply-button']",
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

            # Fallback: XPath por texto
            if not botao:
                xpaths = [
                    "//button[contains(., 'Candidatura simplificada')]",
                    "//button[contains(., 'Easy Apply')]",
                    "//button[contains(@aria-label, 'Candidatura simplificada')]",
                    "//button[contains(@aria-label, 'Easy Apply')]",
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
                logger.info("   ⚠️  Botão Easy Apply não encontrado — vaga pode ser externa")
                self._salvar_vaga_externa(vaga)
                return False

            logger.info("   ✅ Botão Easy Apply encontrado! Clicando...")
            clicar_seguro(self.driver, botao)
            time.sleep(2)

            # Verifica se o modal abriu
            modal = None
            try:
                modal = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                        "div[data-test-modal], div.jobs-easy-apply-modal, div[role='dialog']"
                    ))
                )
            except:
                logger.warning("   ⚠️  Modal não abriu após clicar")
                return False

            if not modal:
                return False

            logger.info("   ✅ Modal aberto! Navegando pelas etapas...")

            # Navega pelas etapas do formulário (máx 8)
            for etapa in range(8):
                time.sleep(1.5)

                # Verifica se candidatura foi enviada com sucesso
                try:
                    corpo = self.driver.find_element(By.TAG_NAME, "body").text
                    if any(t in corpo for t in [
                        "Candidatura enviada",
                        "Application submitted",
                        "sua candidatura foi enviada",
                    ]):
                        logger.info(f"   🎉 Candidatura CONFIRMADA na etapa {etapa + 1}!")
                        return True
                except:
                    pass

                # Botão Enviar candidatura — tenta CSS e XPath
                botao_enviar = self._encontrar_botao([
                    (By.CSS_SELECTOR, "button[aria-label='Enviar candidatura']"),
                    (By.CSS_SELECTOR, "button[aria-label='Submit application']"),
                    (By.XPATH, "//button[contains(., 'Enviar candidatura')]"),
                    (By.XPATH, "//button[contains(., 'Submit application')]"),
                ])

                if botao_enviar:
                    logger.info(f"   🚀 Enviando candidatura (etapa {etapa + 1})...")
                    clicar_seguro(self.driver, botao_enviar)
                    time.sleep(3)

                    # Confirma envio
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

                    return True  # Assumiu enviado após clicar enviar

                # Botão Próximo/Continuar
                botao_proximo = self._encontrar_botao([
                    (By.CSS_SELECTOR, "button[aria-label='Continuar para a próxima etapa']"),
                    (By.CSS_SELECTOR, "button[aria-label='Continue to next step']"),
                    (By.XPATH, "//button[contains(., 'Próximo')]"),
                    (By.XPATH, "//button[contains(., 'Continuar')]"),
                    (By.XPATH, "//button[contains(., 'Next')]"),
                    (By.XPATH, "//button[contains(., 'Continue')]"),
                ])

                if botao_proximo:
                    logger.info(f"   ➡️  Avançando etapa {etapa + 1}...")
                    clicar_seguro(self.driver, botao_proximo)
                    delay_humano(1, 2)
                    continue

                # Nenhum botão encontrado — para o loop
                logger.warning(f"   ⚠️  Nenhum botão encontrado na etapa {etapa + 1}")
                break

            # Fecha modal se ainda aberto
            try:
                botao_fechar = self.driver.find_element(By.CSS_SELECTOR,
                    "button[aria-label='Fechar'], button[aria-label='Dismiss']"
                )
                clicar_seguro(self.driver, botao_fechar)
            except:
                pass

            logger.warning("   ❌ Não foi possível confirmar o envio da candidatura")
            return False

        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar no LinkedIn: {e}")
            return False

    def _encontrar_botao(self, seletores: list):
        """Tenta encontrar um botão por lista de seletores (CSS ou XPath)"""
        for by, sel in seletores:
            try:
                el = self.driver.find_element(by, sel)
                if el and el.is_displayed() and el.is_enabled():
                    return el
            except:
                continue
        return None

    def _salvar_vaga_externa(self, vaga: dict):
        """Salva vaga externa para candidatura manual"""
        try:
            with open(VAGAS_EXTERNAS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{vaga['titulo']} | {vaga['empresa']} | {vaga['url']}\n")
        except Exception as e:
            logger.debug(f"Erro ao salvar vaga externa: {e}")
