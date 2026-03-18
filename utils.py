"""
Utilitários do Bot - Logging, Tracking, Helpers
"""

import logging
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import LOG, FILTROS

# ============================================================================
# LOGGING
# ============================================================================
def setup_logger():
    """Configura o sistema de logs"""
    logging.basicConfig(
        level=getattr(logging, LOG["nivel"]),
        format=LOG["formato"],
        handlers=[
            logging.FileHandler(LOG["arquivo"], encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("BOT")

logger = setup_logger()

# ============================================================================
# TRACKING DE CANDIDATURAS
# ============================================================================
class CandidaturasTracker:
    """Rastreia candidaturas já enviadas para evitar duplicatas"""
    
    def __init__(self, arquivo="c:\\safadeza\\candidaturas.json"):
        self.arquivo = Path(arquivo)
        self.candidaturas = self._carregar()
    
    def _carregar(self) -> Dict:
        """Carrega histórico de candidaturas"""
        if self.arquivo.exists():
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _salvar(self):
        """Salva histórico de candidaturas"""
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.candidaturas, f, indent=2, ensure_ascii=False)
    
    def ja_candidatou(self, site: str, vaga_id: str) -> bool:
        """Verifica se já se candidatou a esta vaga"""
        return vaga_id in self.candidaturas.get(site, {})
    
    def registrar(self, site: str, vaga_id: str, titulo: str, empresa: str):
        """Registra uma nova candidatura"""
        if site not in self.candidaturas:
            self.candidaturas[site] = {}
        
        self.candidaturas[site][vaga_id] = {
            "titulo": titulo,
            "empresa": empresa,
            "data": datetime.now().isoformat()
        }
        self._salvar()
        logger.info(f"✅ Candidatura registrada: {titulo} @ {empresa}")
    
    def total_candidaturas(self) -> int:
        """Retorna total de candidaturas"""
        return sum(len(vagas) for vagas in self.candidaturas.values())
    
    def candidaturas_por_site(self, site: str) -> int:
        """Retorna total de candidaturas em um site específico"""
        return len(self.candidaturas.get(site, {}))

tracker = CandidaturasTracker()

# ============================================================================
# FILTROS
# ============================================================================
def vaga_passa_filtros(titulo: str, empresa: str, descricao: str = "") -> bool:
    """Verifica se a vaga passa pelos filtros configurados"""
    
    titulo_lower = titulo.lower()
    empresa_lower = empresa.lower()
    descricao_lower = descricao.lower()
    
    # Filtro de empresas bloqueadas
    for empresa_bloqueada in FILTROS["empresas_bloqueadas"]:
        if empresa_bloqueada.lower() in empresa_lower:
            logger.info(f"🚫 Vaga bloqueada: empresa '{empresa}' está na lista de bloqueio")
            return False
    
    # Filtro de palavras bloqueadas no título
    for palavra in FILTROS["palavras_bloqueadas_titulo"]:
        if palavra.lower() in titulo_lower:
            logger.info(f"🚫 Vaga bloqueada: título contém '{palavra}'")
            return False
    
    # Filtro de palavras bloqueadas na descrição
    if descricao:
        for palavra in FILTROS["palavras_bloqueadas_descricao"]:
            if palavra.lower() in descricao_lower:
                logger.info(f"🚫 Vaga bloqueada: descrição contém '{palavra}'")
                return False
    
    return True

# ============================================================================
# HELPERS SELENIUM
# ============================================================================
def esperar_elemento(driver: WebDriver, by: By, valor: str, timeout: int = 10):
    """Espera um elemento aparecer na página"""
    try:
        elemento = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, valor))
        )
        return elemento
    except TimeoutException:
        logger.warning(f"⏱️ Timeout esperando elemento: {valor}")
        return None

def esperar_clicavel(driver: WebDriver, by: By, valor: str, timeout: int = 10):
    """Espera um elemento ficar clicável"""
    try:
        elemento = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, valor))
        )
        return elemento
    except TimeoutException:
        logger.warning(f"⏱️ Timeout esperando elemento clicável: {valor}")
        return None

def clicar_seguro(driver: WebDriver, elemento):
    """Clica em um elemento de forma segura"""
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
        time.sleep(0.5)
        elemento.click()
        return True
    except Exception as e:
        logger.warning(f"⚠️ Erro ao clicar: {e}")
        try:
            driver.execute_script("arguments[0].click();", elemento)
            return True
        except:
            return False

def digitar_humano(elemento, texto: str):
    """Digita texto simulando comportamento humano"""
    for char in texto:
        elemento.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def scroll_aleatorio(driver: WebDriver, vezes: int = 3):
    """Faz scroll aleatório na página"""
    for _ in range(vezes):
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))

def delay_humano(min_seg: float = 1, max_seg: float = 3):
    """Delay aleatório para simular comportamento humano"""
    time.sleep(random.uniform(min_seg, max_seg))

# ============================================================================
# EXTRAÇÃO DE IDs
# ============================================================================
def extrair_id_vaga(url: str, site: str) -> Optional[str]:
    """Extrai ID único da vaga a partir da URL"""
    try:
        if site == "linkedin":
            # LinkedIn: /jobs/view/123456789/
            if "/jobs/view/" in url:
                return url.split("/jobs/view/")[1].split("/")[0].split("?")[0]
        
        elif site == "catho":
            # Catho: /vagas/123456/
            if "/vagas/" in url:
                return url.split("/vagas/")[1].split("/")[0].split("?")[0]
        
        elif site == "infojobs":
            # InfoJobs: /vaga-de-...-em-...-123456.html
            if ".html" in url:
                return url.split("-")[-1].replace(".html", "")
        
        elif site == "indeed":
            # Indeed: jk=abc123def456
            if "jk=" in url:
                return url.split("jk=")[1].split("&")[0]
        
        return None
    except:
        return None
