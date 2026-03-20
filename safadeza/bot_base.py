"""
Classe Base para todos os Bots
"""

from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Dict
from utils import logger, tracker, delay_humano, vaga_passa_filtros
from config import LIMITES, BUSCA

class BotBase(ABC):
    """Classe base abstrata para todos os bots de candidatura"""
    
    def __init__(self, driver: WebDriver, nome_site: str):
        self.driver = driver
        self.nome_site = nome_site
        self.candidaturas_enviadas = 0
        logger.info(f"🤖 Bot {nome_site} inicializado")
    
    @abstractmethod
    def fazer_login(self) -> bool:
        """Verifica/faz login no site"""
        pass
    
    @abstractmethod
    def buscar_vagas(self, palavra_chave: str) -> List[Dict]:
        """Busca vagas com a palavra-chave"""
        pass
    
    @abstractmethod
    def candidatar_vaga(self, vaga: Dict) -> bool:
        """Envia candidatura para uma vaga"""
        pass
    
    def executar(self) -> int:
        """Executa o fluxo completo do bot"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 INICIANDO BOT: {self.nome_site.upper()}")
        logger.info(f"{'='*60}\n")
        
        # Verificar login
        if not self.fazer_login():
            logger.error(f"❌ Falha no login do {self.nome_site}")
            return 0
        
        logger.info(f"✅ Login confirmado no {self.nome_site}")
        
        # Buscar e candidatar para cada palavra-chave
        for idx, palavra_chave in enumerate(BUSCA["palavras_chave"], 1):
            if self.candidaturas_enviadas >= LIMITES["max_candidaturas_por_site"]:
                logger.info(f"🎯 Meta atingida: {self.candidaturas_enviadas} candidaturas")
                break
            
            logger.info(f"\n🔍 [{idx}/{len(BUSCA['palavras_chave'])}] Buscando: '{palavra_chave}'")
            
            try:
                vagas = self.buscar_vagas(palavra_chave)
                logger.info(f"📋 {len(vagas)} vagas encontradas")
                
                for vaga_idx, vaga in enumerate(vagas, 1):
                    if self.candidaturas_enviadas >= LIMITES["max_candidaturas_por_site"]:
                        break
                    
                    logger.info(f"\n📄 [{vaga_idx}/{len(vagas)}] {vaga['titulo']}")
                    logger.info(f"   🏢 {vaga['empresa']}")
                    
                    # Verificar se já candidatou
                    if tracker.ja_candidatou(self.nome_site, vaga["id"]):
                        logger.info(f"   ⏭️  Já candidatou antes")
                        continue
                    
                    # Aplicar filtros
                    if not vaga_passa_filtros(vaga["titulo"], vaga["empresa"]):
                        continue
                    
                    # Tentar candidatar
                    try:
                        sucesso = self.candidatar_vaga(vaga)
                        
                        if sucesso:
                            tracker.registrar(
                                self.nome_site,
                                vaga["id"],
                                vaga["titulo"],
                                vaga["empresa"]
                            )
                            self.candidaturas_enviadas += 1
                            logger.info(f"   ✅ CANDIDATURA ENVIADA!")
                            logger.info(f"   📊 Progresso: {self.candidaturas_enviadas}/{LIMITES['max_candidaturas_por_site']}")
                            
                            # Delay entre candidaturas
                            delay = LIMITES["delay_entre_candidaturas"]
                            logger.info(f"   ⏳ Aguardando {delay}s...")
                            delay_humano(delay, delay + 2)
                        else:
                            logger.warning(f"   ❌ Falha ao enviar candidatura")
                    
                    except Exception as e:
                        logger.error(f"   ❌ Erro ao candidatar: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"❌ Erro na busca '{palavra_chave}': {e}")
                continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ BOT {self.nome_site.upper()} FINALIZADO")
        logger.info(f"📊 Total de candidaturas: {self.candidaturas_enviadas}")
        logger.info(f"{'='*60}\n")
        
        return self.candidaturas_enviadas
