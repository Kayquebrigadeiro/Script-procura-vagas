"""
Configurações do Bot de Candidaturas Automáticas
"""

# ============================================================================
# DADOS PESSOAIS
# ============================================================================
PERFIL = {
    "nome_completo": "FUTURO",
    "email": "gregoriokayque352@gmail.com",
    "telefone": "(11) 98058-4791",
    "curriculo_path": "c:\\safadeza\\Curriculo.pdf",
    
    # Dados adicionais (preencha conforme necessário)
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
        "Desenvolvedor Java Junior",
        "Desenvolvedor React Junior",
        "Desenvolvedor JavaScript Junior",
        "Desenvolvedor Node.js Junior",
        "Desenvolvedor Backend Junior",
        "Desenvolvedor Frontend Junior",
        "Desenvolvedor Fullstack Junior",
    ],
    
    "localizacao": "São Paulo, SP",
    
    # Filtros específicos por site
    "linkedin": {
        "easy_apply_only": False,  # DESATIVADO - candidatar em todas as vagas
        "remote": False,
        "experience_level": ["entry_level", "associate"]  # Junior
    },
    
    "catho": {
        "home_office": False,
        "nivel": "junior"
    },
    
    "infojobs": {
        "home_office": False,
        "nivel": "junior"
    },
    
    "indeed": {
        "remote": False,
        "experience": "entry_level"
    }
}

# ============================================================================
# LIMITES E CONTROLES
# ============================================================================
LIMITES = {
    "max_candidaturas_por_site": 10,
    "max_candidaturas_total": 40,
    "delay_entre_candidaturas": 5,  # segundos
    "delay_entre_sites": 10,  # segundos
    "timeout_pagina": 30,  # segundos
}

# ============================================================================
# FILTROS (Evitar certas vagas)
# ============================================================================
FILTROS = {
    "empresas_bloqueadas": [
        # Adicione empresas que você NÃO quer se candidatar
    ],
    
    "palavras_bloqueadas_titulo": [
        "senior", "sênior", "sr.",
        "pleno", "pl.",
        "especialista",
        "tech lead", "lead",
        "gerente", "manager",
    ],
    
    "palavras_bloqueadas_descricao": [
        # Adicione palavras que, se aparecerem na descrição, você quer evitar
    ]
}

# ============================================================================
# CHROME
# ============================================================================
CHROME = {
    "debug_port": 9222,
    "user_data_dir": "C:\\Users\\Desktop\\AppData\\Local\\Google\\Chrome\\User Data",
    "profile": "Profile 1"
}

# ============================================================================
# LOGS
# ============================================================================
LOG = {
    "arquivo": "c:\\safadeza\\bot.log",
    "nivel": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "formato": "%(asctime)s [%(levelname)s] %(message)s"
}
