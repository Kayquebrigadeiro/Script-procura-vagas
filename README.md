# 🤖 Bot de Candidaturas Automáticas

Bot profissional para enviar candidaturas automáticas em:
- **LinkedIn** (Easy Apply)
- **Catho**
- **InfoJobs**
- **Indeed**

## 📋 Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- Currículo em PDF

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar seus dados

Edite o arquivo `config.py`:

```python
PERFIL = {
    "nome_completo": "SEU NOME",
    "email": "seu@email.com",
    "telefone": "(11) 99999-9999",  # AJUSTE
    "curriculo_path": "c:\\safadeza\\Curriculo.pdf",
}

BUSCA = {
    "palavras_chave": [
        "Desenvolvedor Frontend Junior",
        "Desenvolvedor React Junior",
        # Adicione mais palavras-chave
    ],
    "localizacao": "São Paulo, SP",
}
```

## 📖 Como Usar

### Passo 1: Abrir Chrome com Debug

Execute o arquivo:
```bash
abrir_chrome.bat
```

Isso vai abrir o Chrome com porta de debug ativa.

### Passo 2: Fazer Login nos Sites

No Chrome que abriu, faça login manualmente em:
1. LinkedIn (https://linkedin.com)
2. Catho (https://catho.com.br)
3. InfoJobs (https://infojobs.com.br)
4. Indeed (https://br.indeed.com)

**IMPORTANTE:** Mantenha o Chrome aberto!

### Passo 3: Executar o Bot

```bash
python main.py
```

O bot vai:
1. Conectar ao Chrome já aberto
2. Verificar login em cada site
3. Buscar vagas com suas palavras-chave
4. Enviar candidaturas automaticamente
5. Salvar histórico para evitar duplicatas

## ⚙️ Configurações

### Limites

```python
LIMITES = {
    "max_candidaturas_por_site": 10,  # Máximo por site
    "max_candidaturas_total": 40,     # Máximo total
    "delay_entre_candidaturas": 5,    # Segundos entre cada
    "delay_entre_sites": 10,          # Segundos entre sites
}
```

### Filtros

```python
FILTROS = {
    "empresas_bloqueadas": [
        "Empresa X",  # Não candidatar nesta empresa
    ],
    
    "palavras_bloqueadas_titulo": [
        "senior", "pleno",  # Evitar vagas com essas palavras
    ],
}
```

## 📊 Arquivos Gerados

- `candidaturas.json` - Histórico de candidaturas (evita duplicatas)
- `bot.log` - Log detalhado de todas as ações

## 🔧 Solução de Problemas

### Erro: "Não foi possível conectar ao Chrome"

**Solução:** Execute `abrir_chrome.bat` ANTES de rodar `python main.py`

### Erro: "Login não detectado"

**Solução:** Faça login manualmente no site quando o bot pedir

### Bot não encontra vagas

**Possíveis causas:**
1. Palavras-chave muito específicas
2. Localização muito restrita
3. Filtros muito rigorosos (ex: Easy Apply no LinkedIn)

**Solução:** Ajuste as configurações em `config.py`

### Seletores desatualizados

Os sites mudam frequentemente. Se o bot parar de funcionar:

1. Abra uma issue no GitHub
2. Ou atualize os seletores nos arquivos `*_bot.py`

## 📝 Estrutura do Projeto

```
safadeza/
├── main.py              # Orquestrador principal
├── config.py            # Configurações
├── utils.py             # Utilitários
├── bot_base.py          # Classe base dos bots
├── linkedin_bot.py      # Bot LinkedIn
├── catho_bot.py         # Bot Catho
├── infojobs_bot.py      # Bot InfoJobs
├── indeed_bot.py        # Bot Indeed
├── abrir_chrome.bat     # Script para abrir Chrome
├── requirements.txt     # Dependências
├── Curriculo.pdf        # Seu currículo
├── candidaturas.json    # Histórico (gerado)
└── bot.log              # Logs (gerado)
```

## ⚠️ Avisos Importantes

1. **Use com responsabilidade** - Não abuse dos sites
2. **Respeite os limites** - Configure delays adequados
3. **Mantenha atualizado** - Sites mudam frequentemente
4. **Verifique candidaturas** - O bot pode falhar em alguns casos
5. **Privacidade** - Não compartilhe seus logs/histórico

## 🎯 Dicas

- Comece com limites baixos (5-10 candidaturas) para testar
- Ajuste as palavras-chave para sua área
- Use filtros para evitar vagas inadequadas
- Execute o bot regularmente (diariamente)
- Mantenha seu currículo atualizado

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs em `bot.log`
2. Leia a seção "Solução de Problemas"
3. Ajuste as configurações em `config.py`

## 🔄 Atualizações

Para atualizar o bot:
```bash
git pull
pip install -r requirements.txt --upgrade
```

---

**Boa sorte na busca por emprego! 🍀**
