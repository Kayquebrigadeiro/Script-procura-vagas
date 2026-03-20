"""
Configurações do Bot de Candidaturas Automáticas
"""

# ============================================================================
# DADOS PESSOAIS — ajuste antes de rodar
# ============================================================================
PERFIL = {
    "nome_completo": "Kayque Moura Gregorio",
    "email": "gregoriokayque352@gmail.com",
    "telefone": "(11) 98058-4791",
    "curriculo_path": "c:\\safadeza\\Curriculo.pdf",
    "linkedin_url": "",
    "github_url": "",
    "portfolio_url": "",
    "pretensao_salarial": "A combinar",
}

# ============================================================================
# BUSCA DE VAGAS
# ============================================================================
BUSCA = {
    "palavras_chave": [
        "Desenvolvedor Python Junior",
        "Desenvolvedor React Junior",
        "Desenvolvedor JavaScript Junior",
        "Desenvolvedor Frontend Junior",
        "Desenvolvedor Fullstack Junior",
    ],

    "localizacao": "São Paulo, SP",

    "linkedin": {
        "remote": False,
        "experience_level": ["entry_level", "associate"],
    },
    "catho":    {"nivel": "junior"},
    "infojobs": {"nivel": "junior"},
    "indeed":   {"experience": "entry_level"},
}

# ============================================================================
# LIMITES — comece baixo para testar
# ============================================================================
LIMITES = {
    "max_candidaturas_por_site": 5,   # aumenta depois que confirmar que funciona
    "max_candidaturas_total": 20,
    "delay_entre_candidaturas": 6,    # segundos — não reduza muito
    "delay_entre_sites": 12,
    "timeout_pagina": 30,
}

# ============================================================================
# FILTROS
# ============================================================================
FILTROS = {
    "empresas_bloqueadas": [],

    "palavras_bloqueadas_titulo": [
        "senior", "sênior", "sr.",
        "pleno", "pl.",
        "especialista",
        "tech lead", "lead",
        "gerente", "manager",
    ],

    "palavras_bloqueadas_descricao": [],
}

# ============================================================================
# CHROME
# ============================================================================
CHROME = {
    "debug_port": 9222,
    "user_data_dir": "C:\\selenium_chrome_profile",
    "profile": "Default",
}

# ============================================================================
# LOGS — caminho correto para c:\safadeza\
# ============================================================================
LOG = {
    "arquivo": "c:\\safadeza\\bot.log",
    "nivel": "INFO",
    "formato": "%(asctime)s [%(levelname)s] %(message)s",
}
