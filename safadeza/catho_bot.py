"""
Bot Catho - Corrigido 2026
Fixes: removido has-text, false positive return True, confirmação real
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

class CathoBot(BotBase):
    """Bot para candidaturas no Catho"""

    def __init__(self, driver):
        super().__init__(driver, "catho")
        self.base_url = "https://www.catho.com.br"

    def fazer_login(self) -> bool:
        try:
            logger.info("🔐 Verificando login no Catho...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente")
            return True
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False

    def buscar_vagas(self, palavra_chave: str) -> list:
        try:
            from urllib.parse import urlencode
            params = urlencode({"q": palavra_chave})
            url = f"{self.base_url}/vagas/?{params}"

            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)

            seletores_cards = [
                "article[class*='JobCard']",
                "article[data-testid='job-card']",
                "div[class*='JobCard']",
                "article",
            ]

            cards = []
            for seletor in seletores_cards:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    if len(cards) >= 2:
                        logger.info(f"✅ {len(cards)} cards com: {seletor}")
                        break
                except:
                    continue

            if not cards:
                logger.warning("⚠️ Nenhum card encontrado no Catho")
                return []

            vagas = []
            for card in cards[:20]:
                try:
                    # Título
                    titulo = None
                    seletores_titulo = [
                        "h2 a", "h3 a",
                        "a[data-testid='job-title']",
                        "[class*='title'] a",
                        "a[href*='/vagas/']",
                    ]
                    titulo_elem = None
                    for sel in seletores_titulo:
                        try:
                            titulo_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if titulo_elem and titulo_elem.text.strip():
                                titulo = titulo_elem.text.strip()
                                break
                        except:
                            continue

                    if not titulo or not titulo_elem:
                        continue

                    url_vaga = titulo_elem.get_attribute("href") or ""
                    if not url_vaga.startswith("http"):
                        url_vaga = self.base_url + url_vaga

                    # Empresa
                    empresa = "Não informado"
                    seletores_empresa = [
                        "[class*='company']", "[class*='Company']",
                        "[class*='employer']", "span[class*='name']",
                    ]
                    for sel in seletores_empresa:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, sel)
                            if el and el.text.strip():
                                empresa = el.text.strip()
                                break
                        except:
                            continue

                    vaga_id = extrair_id_vaga(url_vaga, "catho") or url_vaga.split("/")[-2][:20]

                    vagas.append({
                        "id": vaga_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_vaga,
                    })

                except Exception as e:
                    logger.debug(f"Erro ao processar card Catho: {e}")
                    continue

            return vagas

        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas Catho: {e}")
            return []

    def candidatar_vaga(self, vaga: dict) -> bool:
        try:
            logger.info("   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            scroll_aleatorio(self.driver, 2)

            logger.info("   🔍 Procurando botão de candidatura...")
            botao = None

            # CSS — sem has-text
            seletores_css = [
                "button[title*='Quero me candidatar']",
                "button[class*='StyledButton'][class*='apply']",
                "button[data-testid*='apply']",
                "button[class*='apply-button']",
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
                    "//button[contains(., 'Quero me candidatar')]",
                    "//button[contains(., 'Candidatar')]",
                    "//button[contains(., 'Aplicar')]",
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
                logger.info("   ⚠️ Botão não encontrado no Catho")
                return False

            logger.info("   ✅ Botão encontrado! Clicando...")
            clicar_seguro(self.driver, botao)
            time.sleep(2)

            # Preenche formulário
            try:
                campos_texto = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                for campo in campos_texto:
                    if not campo.is_displayed():
                        continue
                    placeholder = (campo.get_attribute("placeholder") or "").lower()
                    name = (campo.get_attribute("name") or "").lower()
                    if "telefone" in placeholder or "phone" in name or "tel" in name:
                        if not campo.get_attribute("value"):
                            campo.clear()
                            digitar_humano(campo, PERFIL["telefone"])
            except:
                pass

            delay_humano(1, 2)

            # Botão de confirmação — XPath por texto (sem has-text CSS)
            botao_confirmar = None
            xpaths_confirmar = [
                "//button[@type='submit']",
                "//button[contains(., 'Confirmar')]",
                "//button[contains(., 'Enviar')]",
                "//button[contains(., 'Concluir')]",
            ]
            for xp in xpaths_confirmar:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el and el.is_displayed() and el.is_enabled():
                        botao_confirmar = el
                        break
                except:
                    continue

            if botao_confirmar:
                logger.info("   🚀 Confirmando candidatura...")
                clicar_seguro(self.driver, botao_confirmar)
                time.sleep(2)

                # Verifica confirmação real
                try:
                    corpo = self.driver.find_element(By.TAG_NAME, "body").text
                    if any(t in corpo for t in [
                        "Candidatura enviada",
                        "candidatou",
                        "sucesso",
                        "Obrigado",
                    ]):
                        logger.info("   🎉 Candidatura CONFIRMADA!")
                        return True
                except:
                    pass

                logger.warning("   ⚠️ Clicou em confirmar mas não encontrou mensagem de sucesso")
                return False

            # Se não achou botão confirmar mas clicou em candidatar
            # verifica se já foi confirmado automaticamente
            try:
                corpo = self.driver.find_element(By.TAG_NAME, "body").text
                if any(t in corpo for t in ["candidatou", "Obrigado", "sucesso"]):
                    logger.info("   🎉 Candidatura CONFIRMADA automaticamente!")
                    return True
            except:
                pass

            logger.warning("   ⚠️ Não foi possível confirmar a candidatura no Catho")
            return False

        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar Catho: {e}")
            return False
