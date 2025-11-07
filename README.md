# EVCharge Manager

Sistema de linha de comando (CLI) para **gestão de recargas de veículos elétricos/híbridos em condomínios**.  
Com ele você cadastra condomínios e usuários (com **RFID**), registra/consulta a **última medida** (kWh, R$ e tempo), **importa** dados via TXT e **exporta** CSV. O sistema usa **SQLite** (arquivo local), **configuração externa** (YAML/variáveis de ambiente), **logging** e **testes** (unitários, integração, funcionais e estruturais) com cobertura.



---

## Sumário
- [Visão geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como executar (CLI)](#como-executar-cli)
- [Fluxos de uso](#fluxos-de-uso)
- [Importação/Exportação](#importaçãoexportação)
- [Testes automatizados](#testes-automatizados)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Comandos rápidos](#comandos-rápidos)
- [Dúvidas comuns (FAQ)](#dúvidas-comuns-faq)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Visão geral
O **EVCharge Manager** é uma CLI para gestão de recargas em condomínios. Funcionalidades principais:
- Cadastro de **condomínios** e **usuários** (com **RFID** de 8 hex únicos).
- Registro e consulta da **última medida** de abastecimento (Energia kWh, Custo R$, Tempo min).
- **Importação** de condomínios e usuários via **TXT** (UTF-8, `;` como separador).
- **Exportação** de relatórios em **CSV** para diretório configurável.
- Persistência em **SQLite** (arquivo local).
- **Configuração** via `app/config.yaml` e/ou **variáveis de ambiente**.
- **Logging** com arquivo dedicado.
- Suíte de **testes** com cobertura de código (HTML >= 80%).

---

## Pré-requisitos
- **Python 3.11+** (recomendado 3.13)
- `pip` e `venv` habilitados

---

## Instalação
Crie e ative um ambiente virtual e instale dependências:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

---

## Configuração

O sistema lê configurações de `app/config.yaml` e pode ser sobrescrito por variáveis de ambiente.

**Exemplo de `app/config.yaml`:**
```yaml
database:
  path: "evcharge.db"
logging:
  level: "INFO"
  file: "evcharge.log"
cli:
  export_dir: "exports"
```

**Variáveis de ambiente (opcionais):**
```bash
EVCHARGE_DB_PATH=evcharge.db
EVCHARGE_LOG_LEVEL=DEBUG
EVCHARGE_LOG_FILE=evcharge.log
EVCHARGE_EXPORT_DIR=exports
```

> As variáveis de ambiente têm precedência sobre o YAML.

---

## Como executar (CLI)

Sempre execute a partir da **raiz do projeto** (pasta que contém o diretório `app`):

```bash
python -m app.main
```

---

## Fluxos de uso

### [1] Cadastrar condomínio
- **Informe:** Nome, Tipo do carregador (*Lento/Rápido*), Qtde de carregadores, UF (ex.: SP), Preço kWh (R$), Nº de apartamentos.  
- **Saída:** `Condomínio cadastrado com ID X`.

### [2] Importar condomínios via TXT
- **Formato:** UTF-8, separador `;` (linhas em branco e com `#` são ignoradas)  
- **Cabeçalho e exemplo:**
  ```text
  nome;tipo_carregador;qtde_carregadores;estado;preco_kwh;qtde_apartamentos
  Alpha;Lento;2;SP;0.75;50
  Beta;Rápido;3;RJ;1.10;80
  ```
- **Saída:** `N condomínio(s) importado(s).`

### [3] Cadastrar usuário
- **Informe:** Nome, Apartamento, Condomínio (deve existir), Final da placa (2 dígitos), Tipo do veículo (*híbrido/elétrico*, com/sem acento), **RFID** (8 hex, **único**).  
- **Saída:** `Usuário cadastrado com ID X`.  
- **Erros:** `Condomínio não encontrado` (se não existir).

### [4] Consultar usuário (por id ou name)
- Exibe todos os campos do usuário.

### [5] Consultar condomínio (por id ou name)
- Exibe todos os campos do condomínio.

### [6] Atualizar usuário
- Deixe campos em branco para manter valores. **RFID permanece único**. Se trocar de condomínio, o novo deve existir.

### [7] Atualizar condomínio
- Deixe campos em branco para manter valores (ex.: alterar preço do kWh).

### [8] Medidas (último abastecimento do usuário)
- **set:** informe **Energia (kWh)**, **Custo (R$)** e **Tempo (min)** → `Medida registrada.`  
- **ver:** exibe a última medida formatada (ex.: `Energia 12.500 kWh | Custo R$ 9.37 | Tempo 45.0 min`).  
- **Sem medida completa:** `Usuário ainda não possui medidas registradas.`

### [9] Excluir usuário
- Remove o usuário.

### [10] Excluir condomínio
- **Regra de negócio:** bloqueado se houver usuários vinculados; permitido quando não houver.

### [11] Exportar usuários (CSV)
- Gera `exports/users.csv` (ou diretório definido em config).

### [12] Exportar condomínios (CSV)
- Gera `exports/condos.csv`.

### [13] Importar usuários via TXT
- **Formato:** UTF-8, separador `;`  
- **Cabeçalho e exemplo:**
  ```text
  nome;apartamento;condominio;final_placa;tipo_veiculo;rfid
  Ana;12B;Alpha;34;elétrico;b3950a25
  Bob;101;Beta;56;híbrido;0fbb65a9
  ```
- **Saída:** `Importação concluída: X criado(s), Y falha(s).` (lista de erros por linha inválida).

---

## Importação/Exportação

### Exemplos de arquivos TXT
**`condominios.txt`**
```text
# nome;tipo_carregador;qtde_carregadores;estado;preco_kwh;qtde_apartamentos
Alpha;Lento;2;SP;0.75;50
Beta;Rápido;3;RJ;1.10;80
```

**`usuarios.txt`**
```text
# nome;apartamento;condominio;final_placa;tipo_veiculo;rfid
Ana;12B;Alpha;34;elétrico;b3950a25
Bob;101;Beta;56;híbrido;0fbb65a9
```

### Arquivos gerados
- `exports/users.csv`
- `exports/condos.csv`
- `evcharge.db` (SQLite, após executar a CLI)
- `evcharge.log` (arquivo de log)

---

## Testes automatizados

### Rodar toda a suíte
```bash
pytest
# A cobertura HTML é gerada em ./cov_html
```

### Rodar por tipo
```bash
pytest -q tests/unit
pytest -q tests/integration
pytest -q tests/functional
pytest -q tests/structural
```

### Cobertura de código (HTML >= 80%)
> Já habilitada via `pytest.ini` com `--cov=app --cov-branch --cov-report=term-missing --cov-report=html:cov_html --cov-fail-under=80`.  
Após rodar os testes, abra `cov_html/index.html` no navegador.

### Dicas úteis
```bash
# Executar arquivo específico
pytest -q tests/unit/test_validators.py

# Executar por padrão textual
pytest -q -k rfid
```

---

## Estrutura de pastas
```
app/
  cli/, domain/, infrastructure/, services/, utils/
  config.yaml, main.py, logging_config.py, schema_sql.py
tests/
  unit/, integration/, functional/, structural/
  fixtures/
cov_html/   (gerado após cobertura)
exports/    (gerado pela CLI)
evcharge.db (gerado ao executar)
evcharge.log
```

---

## Comandos rápidos
```bash
# Criar e ativar venv
python -m venv .venv && .\.venv\Scripts\activate

# Instalar deps
pip install -r requirements.txt

# Rodar CLI
python -m app.main

# Rodar testes (todos)
pytest

# Rodar somente unitários
pytest -q tests/unit

# Abrir cobertura (depois dos testes)
# cov_html/index.html
```

---

## Contribuindo
- Issues e PRs são bem-vindos.  
- Sugestão: mantenha a cobertura **≥ 80%** e siga a organização de pastas e padrões existentes.
- Inclua testes (unitários/integração/funcionais/estruturais) quando alterar regras de negócio.


