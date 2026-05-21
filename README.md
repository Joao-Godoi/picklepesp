# PicklePesp

Sistema web para gerenciamento e acompanhamento de um campeonato interno de pickleball.

## Acesso Rapido

| Ambiente | URL |
|----------|-----|
| Site publico | `https://picklepesp.up.railway.app/` |
| Painel Admin | `https://picklepesp.up.railway.app/admin/` |

---

## Telas do Site Publico

### Inicio (`/`)

Pagina principal com resumo do campeonato.

- **Progresso**: Barra mostrando quantas partidas ja foram finalizadas do total
- **Navegacao**: Cards rapidos para Grupos, Playoffs e Posicoes
- **Proximos Jogos**: Lista das 6 proximas partidas pendentes/prontas com as duplas e status
- **Estrutura do Campeonato**: Informacoes sobre formato (grupos, playoffs, posicoes)
- **Regras de Classificacao**: Criterios de desempate e classificados

### Grupos (`/groups`)

Exibe a classificacao e partidas de cada grupo (A, B e C).

**Tabela de Classificacao** (por grupo):

| Coluna | Significado |
|--------|-------------|
| `#` | Posicao no grupo (1°, 2°, 3°...) |
| `Dupla` | Numero da dupla (ex: Dupla 1) |
| `J` | Jogos disputados |
| `V` | Vitorias |
| `D` | Derrotas |
| `SS` | Saldo de sets (sets vencidos - sets perdidos) |
| `SP` | Saldo de pontos (pontos marcados - pontos sofridos) |

**Lista de Partidas**: Cada partida mostra as duas duplas, o placar (se finalizada) e o status.

### Playoffs (`/playoffs`)

Chave do mata-mata principal, organizado por fase:

1. **Quartas de final** (Jogos 5-8)
2. **Disputa de 5° ao 8°** (Jogos 9-10)
3. **Disputa de 7° e 8°** (Jogo 11)
4. **Disputa de 5° e 6°** (Jogo 12)
5. **Semifinal** (Jogos 13-14)
6. **Disputa de 3° lugar** (Jogo 15)
7. **Final** (Jogo 16)

Cada confronto mostra:
- Numero do jogo (J5, J6...)
- Duplas (ou descricao da origem, ex: "1° Grupo A", "Vencedor jogo 5")
- Placar por set (quando finalizada)
- Indicador visual de vencedor (destaque verde)

### Posicoes (`/placements`)

Disputas do 9° ao 14° lugar, organizado por fase:

1. **Disputa do 12° ao 14°** (Jogos 1-2)
2. **Disputa do 9° ao 11°** (Jogos 3-4)

Cada confronto mostra as mesmas informacoes de placar que os playoffs, alem da posicao final atribuida ao vencedor e perdedor.

---

## Estrutura do Campeonato

### Grupos

| Grupo | Duplas |
|-------|--------|
| Grupo A | Dupla 1, Dupla 2, Dupla 3, Dupla 4, Dupla 5 |
| Grupo B | Dupla 6, Dupla 7, Dupla 8, Dupla 9, Dupla 10 |
| Grupo C | Dupla 11, Dupla 12, Dupla 13, Dupla 14 |

### Classificados para Mata-Mata

- 3 melhores do Grupo A
- 3 melhores do Grupo B
- 2 melhores do Grupo C

### Formato dos Jogos

| Tipo | Formato | Pontuacao |
|------|---------|-----------|
| Fase de grupos | Melhor de 3 sets | Ate 11 pontos |
| Playoffs | Melhor de 3 sets | Ate 11 pontos |
| Disputa de posicoes | 1 set unico | Ate 11 pontos |

### Criterios de Desempate

1. Maior numero de vitorias
2. Maior saldo de sets
3. Maior saldo de pontos

---

## Painel Administrativo

Acesso em `/admin/` com usuario e senha.

### Credenciais Padrao

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Senha | `admin123` |

### Como Operar o Admin

#### 1. Registrar resultado de uma partida

Este e o fluxo principal do campeonato. Siga estes passos:

1. Acesse **Partidas** no admin
2. Clique na partida que deseja registrar o resultado
3. Na secao **Sets**, preencha os campos:
   - `Set number`: numero do set (1, 2 ou 3 para melhor de 3; apenas 1 para disputa de posicoes)
   - `Team A points`: pontos da dupla A neste set
   - `Team B points`: pontos da dupla B neste set
4. Altere o campo **Status** para `Finalizada`
5. Clique em **Salvar**

O sistema ira automaticamente:
- Calcular o vencedor com base nos sets
- Propagar o resultado para partidas dependentes (ex: vencedor avanca na chave)
- Recalcular a classificacao dos grupos
- Atualizar confrontos de playoffs e disputas de posicoes
- Exibir mensagens de confirmacao ou erro no topo da pagina

#### 2. Corrigir um resultado

1. Abra a partida finalizada
2. Altere os sets ou o status conforme necessario
3. Clique em **Salvar**
4. Se necessario, execute o comando de recalculo (ver secao Comandos)

#### 3. Entendendo os campos da Partida

| Campo | Descricao |
|-------|-----------|
| `Match number` | Numero oficial do jogo (1-16 para playoffs/posicoes, 1000+ para fase de grupos) |
| `Phase` | Fase da partida (Fase de grupos, Quartas de final, Semifinal, etc.) |
| `Bracket type` | Tipo de chave (Grupo, Mata-mata principal, Disputa de posicoes) |
| `Group` | Grupo associado (apenas para partidas de fase de grupos) |
| `Status` | Estado da partida |
| `Best of` | Formato (3 = melhor de 3 sets, 1 = set unico) |
| `Sort order` | Ordem de exibicao na pagina publica |
| `Team A` / `Team B` | Duplas participantes |
| `Source team A` / `Source team B` | Descricao de origem (ex: "1° Grupo A", "Vencedor jogo 5") |
| `Source match A` / `Source match B` | Partida de origem (para propagacao automatica) |
| `Source match A is winner` / `Source match B is winner` | Se a dupla vem do vencedor (True) ou perdedor (False) da partida de origem |
| `Winner` | Vencedor da partida (preenchido automaticamente, somente leitura) |
| `Final position winner` | Posicao final do vencedor (ex: 1 = campeao, 3 = 3° lugar) |
| `Final position loser` | Posicao final do perdedor (ex: 2 = vice, 4 = 4° lugar) |
| `Scheduled date` | Data/hora planejada (opcional) |

#### 4. Status das Partidas

| Status | Significado |
|--------|-------------|
| `Pendente` | Partida criada mas sem duplas definidas ou aguardando |
| `Bloqueada` | Aguardando resultado de partida anterior para definir duplas |
| `Pronta` | Ambas as duplas definidas, aguardando resultado |
| `Em andamento` | Sets salvos mas partida ainda nao finalizada |
| `Finalizada` | Resultado registrado e vencedor definido |

#### 5. Entendendo os campos do Set

| Campo | Descricao |
|-------|-----------|
| `Set number` | Ordem do set (1, 2 ou 3) |
| `Team A points` | Pontos da dupla A neste set (0-11) |
| `Team B points` | Pontos da dupla B neste set (0-11) |

**Regras de validacao**:
- Sets nao podem terminar empatados
- Pelo menos um lado deve atingir 11 pontos
- Nenhum lado pode ultrapassar 11 pontos
- Partida melhor de 3 precisa de 2 sets vencidos por uma dupla para ser finalizada
- Partida de 1 set precisa de exatamente 1 set

### Telas do Admin

#### Grupos

Lista de grupos (A, B, C). Ao clicar em um grupo, veja as duplas associadas.

#### Duplas

Lista de todas as duplas com numero, nomes dos jogadores e grupo.

| Campo | Descricao |
|-------|-----------|
| `Team number` | Numero identificador da dupla (1-14) |
| `Player 1 name` | Nome do primeiro jogador |
| `Player 2 name` | Nome do segundo jogador |
| `Group` | Grupo da dupla |

#### Partidas

Lista de todas as partidas com filtros por fase, tipo de chave e status. Aqui e onde se registra os resultados.

#### Sets (via inline dentro de Partida)

Os sets sao editados dentro da tela de cada partida, na secao "Sets" na parte inferior.

---

## Fluxo de Propagacao de Resultados

Quando uma partida e finalizada, o sistema propaga automaticamente:

### Mata-Mata Principal

```
Jogo 5 → Jogo 13 (vencedor) e Jogo 9 (perdedor)
Jogo 6 → Jogo 13 (vencedor) e Jogo 9 (perdedor)
Jogo 7 → Jogo 14 (vencedor) e Jogo 10 (perdedor)
Jogo 8 → Jogo 14 (vencedor) e Jogo 10 (perdedor)
Jogo 9 → Jogo 12 (vencedor) e Jogo 11 (perdedor)
Jogo 10 → Jogo 12 (vencedor) e Jogo 11 (perdedor)
Jogo 11 → 7° lugar (perdedor) e 8° lugar (vencedor) -- ATENCAO: o perdedor fica em 8°
Jogo 12 → 5° lugar (vencedor) e 6° lugar (perdedor)
Jogo 13 → Jogo 16 (vencedor) e Jogo 15 (perdedor)
Jogo 14 → Jogo 16 (vencedor) e Jogo 15 (perdedor)
Jogo 15 → 3° lugar (vencedor) e 4° lugar (perdedor)
Jogo 16 → Campeao (vencedor) e 2° lugar (perdedor)
```

### Disputa de Posicoes

```
Jogo 1 → Jogo 2 (vencedor) e 14° lugar (perdedor)
Jogo 2 → 12° lugar (vencedor) e 13° lugar (perdedor)
Jogo 3 → Jogo 4 (vencedor) e 11° lugar (perdedor)
Jogo 4 → 9° lugar (vencedor) e 10° lugar (perdedor)
```

### Resolucao por Classificacao

Os jogos 1, 3, 5, 6, 7 e 8 dependem da classificacao dos grupos:

| Jogo | Dupla A | Dupla B |
|------|---------|---------|
| Jogo 1 | 5° Grupo A | 5° Grupo B |
| Jogo 3 | 4° Grupo A | 4° Grupo B |
| Jogo 5 | 1° Grupo A | 3° Grupo B |
| Jogo 6 | 1° Grupo C | 2° Grupo A |
| Jogo 7 | 1° Grupo B | 3° Grupo A |
| Jogo 8 | 2° Grupo B | 2° Grupo C |

O sistema resolve automaticamente essas posicoes quando ha classificacao suficiente.

---

## Comandos de Gerenciamento

### Seed do Campeonato

```bash
python manage.py seed_tournament
```

Cria os dados iniciais: 3 grupos, 14 duplas, 26 partidas de grupo e 16 partidas de playoffs/posicoes. Idempotente (pode ser executado varias vezes sem duplicar dados).

### Recalculo Manual

```bash
python manage.py recalculate_tournament
```

Recalcula vencedores, propagacoes, classificacoes e resolucao de grupos a partir dos dados existentes. Use se houver inconsistencia.

### Criar Admin

```bash
python manage.py create_admin
```

Cria o superusuario `admin` com senha `admin123` caso nao exista.

---

## Deploy com Docker

### Build e Execucao

```bash
docker compose up --build
```

O container executa automaticamente:
1. `python manage.py migrate` - Aplica migracoes
2. `python manage.py seed_tournament` - Cria dados iniciais
3. `python manage.py create_admin` - Cria usuario admin
4. `gunicorn config.wsgi:application` - Inicia o servidor

### Comandos Operacionais

```bash
# Subir os containers
docker compose up -d

# Parar os containers
docker compose down

# Parar e remover volumes (reset completo)
docker compose down -v

# Executar migracoes
docker compose exec web python manage.py migrate

# Recalcular campeonato
docker compose exec web python manage.py recalculate_tournament

# Coletar arquivos estaticos
docker compose exec web python manage.py collectstatic --noinput

# Backup do banco SQLite
docker compose exec web cp /app/data/db.sqlite3 /app/data/db.sqlite3.bak
```

### Variaveis de Ambiente

| Variavel | Obrigatoria | Padrao | Descricao |
|----------|-------------|--------|-----------|
| `DJANGO_SECRET_KEY` | Sim | - | Chave secreta do Django |
| `DJANGO_DEBUG` | Sim | `True` | `0` em producao, `1` em desenvolvimento |
| `DJANGO_ALLOWED_HOSTS` | Sim | `*` | Hosts permitidos separados por virgula |
| `DATABASE_PATH` | Nao | `db.sqlite3` | Caminho do arquivo SQLite |

---

## Stack Tecnologica

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12+ |
| Framework | Django 6.0 |
| Banco de dados | SQLite |
| Templates | Django Templates |
| Estilizacao | CSS customizado (tema escuro) |
| Servidor WSGI | Gunicorn |
| Proxy reverso | Nginx |
| Containerizacao | Docker + Docker Compose |
| Arquivos estaticos | WhiteNoise |

---

## Visibilidade de Nomes

- **Rotas publicas**: Mostram apenas "Dupla N" (numero da dupla)
- **Painel Admin**: Mostra "Dupla N - Nome1 / Nome2" (apenas para usuarios autenticados como admin)

Isso garante que espectadores identifiquem as duplas apenas pelo numero, enquanto o administrador ve os nomes completos.
