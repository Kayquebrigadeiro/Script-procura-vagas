"""
Bot InfoJobs - Corrigido 2026
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

class InfoJobsBot(BotBase):
    """Bot para candidaturas no InfoJobs"""

    def __init__(self, driver):
        super().__init__(driver, "infojobs")
        self.base_url = "https://www.infojobs.com.br"

    def fazer_login(self) -> bool:
        try:
            logger.info("🔐 Verificando login no InfoJobs...")
            logger.info("⚠️  Se não estiver logado, faça login manualmente")
            return True
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False

    def buscar_vagas(self, palavra_chave: str) -> list:
        try:
            localizacao = BUSCA["localizacao"]
            q = palavra_chave.lower().replace(" ", "-")
            cidade = localizacao.split(",")[0].strip().lower().replace(" ", "-")
            url = f"{self.base_url}/empregos-em-{cidade}/para-{q}.aspx"

            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)

            seletores_cards = [
                "li[class*='vacancy']",
                "div[class*='vacancy']",
                "div[class*='offer']",
                "li[data-id]",
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
                logger.warning("⚠️ Nenhum card encontrado no InfoJobs")
                return []

            vagas = []
            for card in cards[:20]:
                try:
                    titulo_elem = None
                    seletores_titulo = [
                        "h2 a", "h3 a",
                        "a[class*='title']",
                        "a[class*='js-o-link']",
                        "a[href*='vaga-de']",
                    ]
                    for sel in seletores_titulo:
                        try:
                            titulo_elem = card.find_element(By.CSS_SELECTOR, sel)
                            if titulo_elem and titulo_elem.text.strip():
                                break
                        except:
                            continue

                    if not titulo_elem:
                        continue

                    titulo = titulo_elem.text.strip()
                    url_vaga = titulo_elem.get_attribute("href") or ""
                    if not url_vaga.startswith("http"):
                        url_vaga = self.base_url + url_vaga

                    empresa = "Não informado"
                    seletores_empresa = [
                        "span[class*='company']", "a[class*='company']",
                        "span[class*='employer']", "div[class*='company']",
                    ]
                    for sel in seletores_empresa:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, sel)
                            if el and el.text.strip():
                                empresa = el.text.strip()
                                break
                        except:
                            continue

                    vaga_id = (
                        extrair_id_vaga(url_vaga, "infojobs")
                        or card.get_attribute("data-id")
                        or url_vaga[-20:]
                    )

                    vagas.append({
                        "id": vaga_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_vaga,
                    })

                except Exception as e:
                    logger.debug(f"Erro ao processar card InfoJobs: {e}")
                    continue

            return vagas

        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas InfoJobs: {e}")
            return []

    def candidatar_vaga(self, vaga: dict) -> bool:
        try:
            logger.info("   🌐 Abrindo vaga...")
            self.driver.get(vaga["url"])
            time.sleep(3)
            scroll_aleatorio(self.driver, 2)

            logger.info("   🔍 Procurando botão de candidatura...")
            botao = None

            # CSS sem has-text — InfoJobs usa <a> não <button>
            seletores_css = [
                "a.js_btApplyVacancy",
                "a.btn-primary.js_btApplyVacancy",
                "a[class*='ApplyVacancy']",
                "a[class*='apply']",
                "a[id*='apply']",
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
                    "//a[contains(., 'CANDIDATAR-ME')]",
                    "//a[contains(., 'Candidatar')]",
                    "//a[contains(., 'Me candidatar')]",
                    "//button[contains(., 'Candidatar')]",
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
                logger.info("   ⚠️ Botão não encontrado no InfoJobs")
                return False

            logger.info("   ✅ Botão encontrado! Clicando...")
            clicar_seguro(self.driver, botao)
            time.sleep(2)

            # Preenche campos
            try:
                for sel in ["input[name*='telefone']", "input[name*='phone']", "input[id*='phone']"]:
                    try:
                        campos = self.driver.find_elements(By.CSS_SELECTOR, sel)
                        for campo in campos:
                            if campo.is_displayed() and not campo.get_attribute("value"):
                                campo.clear()
                                digitar_humano(campo, PERFIL["telefone"])
                    except:
                        continue
            except:
                pass

            delay_humano(1, 2)

            # Botão de confirmação via XPath
            botao_confirmar = None
            xpaths_confirmar = [
                "//button[@type='submit']",
                "//button[contains(., 'Confirmar')]",
                "//button[contains(., 'Enviar candidatura')]",
                "//button[contains(., 'Concluir')]",
                "//input[@type='submit']",
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
                        "candidatura enviada",
                        "candidatou",
                        "sucesso",
                        "Obrigado",
                        "enviada com sucesso",
                    ]):
                        logger.info("   🎉 Candidatura CONFIRMADA!")
                        return True
                except:
                    pass

                logger.warning("   ⚠️ Clicou mas não confirmou — verifique manualmente")
                return False

            # Sem botão confirmar — verifica se foi direto
            try:
                corpo = self.driver.find_element(By.TAG_NAME, "body").text
                if any(t in corpo for t in ["candidatou", "Obrigado", "sucesso"]):
                    logger.info("   🎉 Candidatura CONFIRMADA!")
                    return True
            except:
                pass

            logger.warning("   ⚠️ Não foi possível confirmar a candidatura no InfoJobs")
            return False

        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar InfoJobs: {e}")
            return False
