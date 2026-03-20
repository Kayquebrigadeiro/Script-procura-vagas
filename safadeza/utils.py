"""
Utilitários do Bot - Logging, Tracking, Helpers
"""

import logging
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import LOG, FILTROS

# ============================================================================
# LOGGING
# ============================================================================
def setup_logger():
    log_path = Path(LOG["arquivo"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, LOG["nivel"]),
        format=LOG["formato"],
        handlers=[
            logging.FileHandler(str(log_path), encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("BOT")

logger = setup_logger()

# ============================================================================
# TRACKING
# ============================================================================
class CandidaturasTracker:
    """Rastreia candidaturas já enviadas para evitar duplicatas"""

    def __init__(self, arquivo="c:\\safadeza\\candidaturas.json"):
        self.arquivo = Path(arquivo)
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.candidaturas = self._carregar()

    def _carregar(self) -> Dict:
        if self.arquivo.exists():
            try:
                with open(self.arquivo, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.candidaturas, f, indent=2, ensure_ascii=False)

    def ja_candidatou(self, site: str, vaga_id: str) -> bool:
        return str(vaga_id) in self.candidaturas.get(site, {})

    def registrar(self, site: str, vaga_id: str, titulo: str, empresa: str):
        if site not in self.candidaturas:
            self.candidaturas[site] = {}
        self.candidaturas[site][str(vaga_id)] = {
            "titulo": titulo,
            "empresa": empresa,
            "data": datetime.now().isoformat()
        }
        self._salvar()

    def total_candidaturas(self) -> int:
        return sum(len(v) for v in self.candidaturas.values())

    def candidaturas_por_site(self, site: str) -> int:
        return len(self.candidaturas.get(site, {}))

tracker = CandidaturasTracker()

# ============================================================================
# FILTROS
# ============================================================================
def vaga_passa_filtros(titulo: str, empresa: str, descricao: str = "") -> bool:
    titulo_lower = titulo.lower()
    empresa_lower = empresa.lower()

    for emp in FILTROS["empresas_bloqueadas"]:
        if emp.lower() in empresa_lower:
            logger.info(f"🚫 Empresa bloqueada: {empresa}")
            return False

    for palavra in FILTROS["palavras_bloqueadas_titulo"]:
        if palavra.lower() in titulo_lower:
            logger.info(f"🚫 Título contém palavra bloqueada: {palavra}")
            return False

    if descricao:
        for palavra in FILTROS["palavras_bloqueadas_descricao"]:
            if palavra.lower() in descricao.lower():
                logger.info(f"🚫 Descrição contém palavra bloqueada: {palavra}")
                return False

    return True

# ============================================================================
# HELPERS SELENIUM
# ============================================================================
def esperar_elemento(driver: WebDriver, by: By, valor: str, timeout: int = 10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, valor))
        )
    except TimeoutException:
        logger.warning(f"⏱️ Timeout: {valor}")
        return None

def esperar_clicavel(driver: WebDriver, by: By, valor: str, timeout: int = 10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, valor))
        )
    except TimeoutException:
        logger.warning(f"⏱️ Timeout clicável: {valor}")
        return None

def clicar_seguro(driver: WebDriver, elemento):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elemento)
        time.sleep(0.5)
        elemento.click()
        return True
    except Exception as e:
        logger.warning(f"⚠️ Click normal falhou: {e} — tentando JS")
        try:
            driver.execute_script("arguments[0].click();", elemento)
            return True
        except:
            return False

def digitar_humano(elemento, texto: str):
    for char in texto:
        elemento.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def scroll_aleatorio(driver: WebDriver, vezes: int = 3):
    for _ in range(vezes):
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
        time.sleep(random.uniform(0.5, 1.5))

def delay_humano(min_seg: float = 1, max_seg: float = 3):
    time.sleep(random.uniform(min_seg, max_seg))

# ============================================================================
# EXTRAÇÃO DE IDs
# ============================================================================
def extrair_id_vaga(url: str, site: str) -> Optional[str]:
    try:
        if not url:
            return None
        if site == "linkedin" and "/jobs/view/" in url:
            return url.split("/jobs/view/")[1].split("/")[0].split("?")[0]
        elif site == "catho" and "/vagas/" in url:
            return url.split("/vagas/")[1].split("/")[0].split("?")[0]
        elif site == "infojobs" and ".html" in url:
            return url.split("-")[-1].replace(".html", "")
        elif site == "indeed" and "jk=" in url:
            return url.split("jk=")[1].split("&")[0]
        return None
    except:
        return None
