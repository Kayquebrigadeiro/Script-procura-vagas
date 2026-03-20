"""
Bot Catho - Focado em Candidatura Fácil 2026
Fluxo: clica em "Enviar Candidatura Fácil" na listagem → fecha modal upsell → confirma toast
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot_base import BotBase
from utils import (
    logger, clicar_seguro, scroll_aleatorio,
    delay_humano, extrair_id_vaga
)
from config import BUSCA

class CathoBot(BotBase):
    def __init__(self, driver):
        super().__init__(driver, "catho")
        self.base_url = "https://www.catho.com.br"

    def fazer_login(self) -> bool:
        try:
            logger.info("🔐 Verificando login no Catho...")
            self.driver.get("https://www.catho.com.br/area-candidato/")
            time.sleep(3)
            if "login" not in self.driver.current_url:
                logger.info("✅ Logado no Catho")
                return True
            logger.warning("⚠️  Faça login manualmente no Catho e execute novamente")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False

    def buscar_vagas(self, palavra_chave: str) -> list:
        """Busca vagas com Candidatura Fácil disponível"""
        try:
            from urllib.parse import urlencode
            params = urlencode({
                "q": palavra_chave,
                "origem_apply": "caixa-de-busca-home-logada",
                "entrada_apply": "direto",
            })
            url = f"{self.base_url}/vagas/?{params}"

            logger.info(f"🌐 Acessando: {url}")
            self.driver.get(url)
            time.sleep(4)
            scroll_aleatorio(self.driver, 3)
            time.sleep(2)

            # Busca todos os botões de Candidatura Fácil visíveis na listagem
            botoes = []
            xpaths_botao = [
                "//button[contains(., 'Enviar Candidatura Fácil')]",
                "//button[contains(., 'Candidatura Fácil')]",
                "//button[contains(., 'Candidatura fácil')]",
            ]
            for xp in xpaths_botao:
                try:
                    encontrados = self.driver.find_elements(By.XPATH, xp)
                    if encontrados:
                        botoes = encontrados
                        logger.info(f"✅ {len(botoes)} botões de Candidatura Fácil encontrados")
                        break
                except:
                    continue

            if not botoes:
                logger.warning("⚠️ Nenhum botão de Candidatura Fácil encontrado")
                return []

            vagas = []
            for i, botao in enumerate(botoes):
                try:
                    # Sobe até o card pai para pegar título e empresa
                    card = None
                    try:
                        card = botao.find_element(By.XPATH, "./ancestor::article[1]")
                    except:
                        try:
                            card = botao.find_element(By.XPATH, "./ancestor::li[1]")
                        except:
                            pass

                    titulo = f"Vaga {i+1}"
                    empresa = "Não informado"
                    url_vaga = "#"

                    if card:
                        # Título
                        for sel in ["h2 a", "h3 a", "a[href*='/vagas/']"]:
                            try:
                                el = card.find_element(By.CSS_SELECTOR, sel)
                                if el and el.text.strip():
                                    titulo = el.text.strip()
                                    url_vaga = el.get_attribute("href") or "#"
                                    break
                            except:
                                continue

                        # Empresa
                        for sel in ["[class*='company']", "[class*='Company']", "[class*='employer']"]:
                            try:
                                el = card.find_element(By.CSS_SELECTOR, sel)
                                if el and el.text.strip():
                                    empresa = el.text.strip()
                                    break
                            except:
                                continue

                        # Pula se já candidatou
                        texto_card = card.text.lower()
                        if "candidatura fácil realizada" in texto_card or "currículo já enviado" in texto_card:
                            logger.debug(f"Pulando vaga já candidatada: {titulo}")
                            continue

                    vaga_id = extrair_id_vaga(url_vaga, "catho") or f"catho_{i}_{int(time.time())}"

                    vagas.append({
                        "id": vaga_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_vaga,
                        "_botao": botao,
                    })

                except Exception as e:
                    logger.debug(f"Erro ao processar botão {i}: {e}")
                    continue

            logger.info(f"Catho: {len(vagas)} vagas disponíveis para candidatura")
            return vagas

        except Exception as e:
            logger.error(f"❌ Erro ao buscar vagas Catho: {e}")
            return []

    def candidatar_vaga(self, vaga: dict) -> bool:
        """Clica em Candidatura Fácil, fecha modal upsell e confirma envio"""
        try:
            botao = vaga.get("_botao")

            if not botao:
                logger.warning("   ⚠️ Referência ao botão perdida")
                return False

            try:
                if not botao.is_displayed():
                    logger.warning("   ⚠️ Botão não está visível")
                    return False
            except:
                logger.warning("   ⚠️ Botão não está mais no DOM")
                return False

            logger.info(f"   🖱️  Clicando em Candidatura Fácil...")
            clicar_seguro(self.driver, botao)
            time.sleep(2)

            # Fecha modal upsell "Agora não"
            try:
                botao_agora_nao = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Agora não')] | //a[contains(., 'Agora não')]"
                    ))
                )
                logger.info("   💬 Modal de upsell detectado — fechando...")
                clicar_seguro(self.driver, botao_agora_nao)
                time.sleep(1)
            except:
                pass

            # Confirma via toast "Currículo enviado com sucesso!"
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//*[contains(., 'Currículo enviado com sucesso') or "
                        "contains(., 'Candidatura realizada') or "
                        "contains(., 'enviado com sucesso')]"
                    ))
                )
                logger.info("   🎉 Candidatura CONFIRMADA!")
                return True
            except:
                pass

            # Fallback — verifica texto na página
            try:
                corpo = self.driver.find_element(By.TAG_NAME, "body").text
                if any(t in corpo for t in [
                    "Currículo enviado com sucesso",
                    "Candidatura realizada",
                    "candidatura fácil realizada",
                    "enviado com sucesso",
                ]):
                    logger.info("   🎉 Candidatura CONFIRMADA!")
                    return True
            except:
                pass

            logger.warning("   ⚠️ Não confirmado — verifique manualmente no Catho")
            return False

        except Exception as e:
            logger.error(f"   ❌ Erro ao candidatar Catho: {e}")
            return False
