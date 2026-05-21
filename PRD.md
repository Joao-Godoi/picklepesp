# PRD - PicklePesp

## 1. Visao Geral

PicklePesp e um sistema web monolitico em Django para gerenciamento e acompanhamento publico de um campeonato interno de pickleball.

O sistema deve permitir que participantes e espectadores acompanhem, pelo navegador, a classificacao dos grupos, as partidas, os resultados, o mata-mata principal e as disputas de posicoes. A atualizacao dos resultados sera feita manualmente por um administrador autenticado no Django Admin.

A aplicacao deve priorizar simplicidade operacional, baixo custo, deploy facil, manutencao direta e boa experiencia em dispositivos moveis.

Nao havera atualizacao em tempo real. Usuarios publicos devem atualizar a pagina manualmente para visualizar novos resultados.

## 2. Objetivos do Produto

1. Disponibilizar uma area publica simples para acompanhamento do campeonato.
2. Exibir classificacao automatica dos grupos A, B e C.
3. Exibir partidas, placares e status de cada jogo.
4. Gerar automaticamente confrontos do mata-mata principal conforme o regulamento.
5. Gerar automaticamente confrontos das disputas de posicao do 9o ao 14o lugar.
6. Propagar vencedores e perdedores para partidas dependentes.
7. Permitir que administradores cadastrem e atualizem resultados pelo Django Admin.
8. Recalcular classificacao, vencedores, rankings e confrontos dependentes apos alteracoes relevantes.
9. Oferecer visual escuro, esportivo, compacto e mobile-first.
10. Permitir deploy simples com Docker, Docker Compose, Gunicorn, Nginx e SQLite.

## 3. Nao Objetivos e Fora de Escopo

O sistema nao deve implementar:

1. Microservicos.
2. React.
3. Next.js.
4. FastAPI.
5. Websocket.
6. Redis.
7. Mensageria.
8. Kubernetes.
9. AWS serverless.
10. APIs complexas.
11. Frontend separado.
12. Atualizacao em tempo real.
13. Aplicativo mobile nativo.
14. Notificacoes.
15. Chat.
16. Comentarios.
17. Uploads.
18. Streaming.
19. Multiplos campeonatos.
20. Permissoes avancadas.
21. APIs publicas.
22. Integracao social.
23. Analytics.
24. Integracao com terceiros.
25. Painel administrativo customizado complexo.

## 4. Publico-Alvo e Perfis de Usuario

| Perfil | Descricao | Permissoes |
| --- | --- | --- |
| Visitante publico | Participante ou espectador que acompanha o campeonato pelo navegador | Visualizar paginas publicas, grupos, partidas, playoffs e disputas de posicoes |
| Administrador | Pessoa responsavel por registrar resultados e manter o campeonato atualizado | Acessar Django Admin, editar partidas, cadastrar sets, finalizar partidas e corrigir resultados |

### User Stories

1. Como visitante, quero abrir a pagina inicial pelo celular para ver rapidamente o estado geral do campeonato.
2. Como visitante, quero consultar a classificacao dos grupos para saber quais duplas estao avancando.
3. Como visitante, quero ver os placares das partidas para acompanhar os resultados do evento.
4. Como visitante, quero visualizar as chaves de mata-mata para entender os proximos confrontos.
5. Como visitante, quero visualizar as disputas de posicoes para acompanhar as colocacoes finais.
6. Como administrador, quero registrar os sets de uma partida para que o sistema calcule o vencedor.
7. Como administrador, quero finalizar uma partida para que a classificacao e os confrontos dependentes sejam atualizados automaticamente.
8. Como administrador, quero ser impedido de salvar placares invalidos para manter a integridade do campeonato.

## 5. Principios do Produto

1. Simplicidade antes de flexibilidade excessiva.
2. Monolito Django com baixo acoplamento interno.
3. Regras de negocio centralizadas em servicos ou funcoes de dominio testaveis.
4. Uso do Django Admin como interface administrativa principal.
5. Interface publica mobile-first, rapida e legivel.
6. Persistencia simples com SQLite em volume Docker.
7. Sem dependencias de infraestrutura que aumentem custo ou complexidade.
8. Recalculo deterministico sempre que resultados forem salvos.
9. Validacoes fortes no backend.
10. Templates server-side com HTML simples, TailwindCSS e Alpine.js apenas quando necessario.

## 6. Stack Tecnologica Obrigatoria

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 ou superior |
| Framework web | Django 6.0 |
| Banco de dados | SQLite |
| Templates | Django Templates |
| Estilizacao | TailwindCSS |
| Interacoes simples | Alpine.js, somente se necessario |
| Servidor WSGI | Gunicorn |
| Proxy reverso | Nginx |
| Containerizacao | Docker |
| Orquestracao local | Docker Compose |

## 7. Arquitetura Recomendada

### Estilo Arquitetural

Aplicacao monolitica Django, com paginas publicas renderizadas no servidor e administracao feita pelo Django Admin.

### Componentes

| Componente | Responsabilidade |
| --- | --- |
| Models | Representar grupos, duplas, partidas e sets |
| Admin | Permitir edicao autenticada de resultados |
| Services | Concentrar calculos de classificacao, validacoes e propagacao de confrontos |
| Views publicas | Renderizar inicio, grupos, playoffs e disputas de posicoes |
| Templates | Exibir tabelas, cards de partidas e brackets |
| Management commands | Criar seed inicial e regenerar estrutura do campeonato quando necessario |
| Tests | Validar regras criticas de negocio e renderizacao basica |

### Decisoes Arquiteturais

1. Usar Django Templates para evitar frontend separado.
2. Usar SQLite por baixo volume, deploy simples e menor custo operacional.
3. Usar Django Admin para reduzir desenvolvimento de painel customizado.
4. Centralizar regras de classificacao e propagacao fora das views e do admin.
5. Evitar sinais complexos quando uma chamada explicita no `save_model` do admin ou servico de aplicacao for mais previsivel.
6. Usar transacoes nas rotinas que salvam resultados e recalculam dependencias.

## 8. Estrutura Esperada do Projeto

```txt
project/
├── app/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── tournament/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── services.py
│       ├── selectors.py
│       ├── views.py
│       ├── urls.py
│       ├── tests.py
│       └── management/
│           └── commands/
│               ├── seed_tournament.py
│               └── recalculate_tournament.py
├── templates/
│   ├── base.html
│   └── tournament/
│       ├── home.html
│       ├── groups.html
│       ├── playoffs.html
│       ├── placements.html
│       └── partials/
│           ├── match_card.html
│           ├── standings_table.html
│           └── bracket.html
├── static/
│   ├── css/
│   └── js/
├── media/
├── nginx/
│   └── default.conf
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 9. Mapa de Navegacao

| Rota | Nome | Acesso | Descricao |
| --- | --- | --- | --- |
| `/` | Inicio | Publico | Resumo do campeonato, proximos jogos e links principais |
| `/groups` | Grupos | Publico | Classificacao dos grupos A, B e C, jogos e resultados |
| `/playoffs` | Mata-mata | Publico | Quartas, semifinais, terceiro lugar, final e disputa de 5o ao 8o |
| `/placements` | Posicoes | Publico | Disputas do 9o ao 14o lugar |
| `/admin/login` | Login admin | Administrador | Login padrao do Django |
| `/admin` | Admin | Administrador | Cadastro e edicao de resultados pelo Django Admin |

## 10. Requisitos Funcionais

### Area Publica

1. RF01: O sistema deve exibir uma pagina inicial publica em `/`.
2. RF02: A pagina inicial deve exibir resumo do campeonato, proximos jogos e links para grupos, playoffs e posicoes.
3. RF03: O sistema deve exibir a pagina `/groups` com classificacao dos grupos A, B e C.
4. RF04: Cada grupo deve exibir posicao, dupla, jogos, vitorias, derrotas, saldo de sets e saldo de pontos.
5. RF05: Cada grupo deve exibir lista de partidas, placares e status.
6. RF06: O sistema deve exibir a pagina `/playoffs` com o mata-mata principal.
7. RF07: O mata-mata principal deve exibir jogos 5 a 16 conforme regulamento oficial.
8. RF08: O sistema deve exibir a pagina `/placements` com disputas do 9o ao 14o lugar.
9. RF09: As paginas de bracket devem exibir confrontos, vencedores e placares.
10. RF10: O usuario publico deve conseguir consultar as informacoes sem autenticacao.

### Administracao

1. RF11: O administrador deve conseguir acessar o Django Admin com login e senha.
2. RF12: O administrador deve conseguir cadastrar e editar grupos.
3. RF13: O administrador deve conseguir cadastrar e editar duplas.
4. RF14: O administrador deve conseguir cadastrar e editar partidas.
5. RF15: O administrador deve conseguir cadastrar e editar sets de uma partida.
6. RF16: O administrador deve conseguir marcar uma partida como finalizada quando o placar for valido.
7. RF17: O sistema deve impedir o salvamento de resultados invalidos.
8. RF18: O sistema deve calcular automaticamente o vencedor da partida a partir dos sets.
9. RF19: O sistema deve recalcular a classificacao apos salvar ou atualizar partidas de grupo.
10. RF20: O sistema deve atualizar confrontos dependentes apos salvar ou atualizar partidas eliminatorias.

### Geracao e Recalculo

1. RF21: O sistema deve possuir seed inicial com grupos, duplas e partidas da fase de grupos.
2. RF22: O sistema deve gerar partidas de grupo sem duplicidade dentro de cada grupo.
3. RF23: O sistema deve gerar jogos 5 a 8 do mata-mata principal apos existir classificacao suficiente.
4. RF24: O sistema deve gerar jogos 1 a 4 das disputas de posicoes apos existir classificacao suficiente.
5. RF25: O sistema deve propagar vencedores e perdedores para jogos dependentes.
6. RF26: O sistema deve permitir recalculo manual por management command.

## 11. Regras Oficiais do Campeonato

### Grupos

| Grupo | Quantidade de duplas |
| --- | ---: |
| Grupo A | 5 |
| Grupo B | 5 |
| Grupo C | 4 |

### Duplas do Grupo A

1. Arthur / Flavio.
2. Rogerio / Ana.
3. Jonas / Valmir.
4. Tati / Danilo.
5. Crepaldi / Angela.

### Duplas do Grupo B

1. Joao Vitor (Tati) / Flavia.
2. Fabio / Virginia.
3. Pena / Vincent.
4. Luciano / Marie.
5. Bustos / Joao.

### Duplas do Grupo C

1. Aoki / Bruno.
2. Pava / Fernanda.
3. Andre Hideki / Joao Vitor (CPD).
4. Sergio / Adriano.

### Fase de Classificacao

1. Todas as partidas da fase de grupos devem ser melhor de 3 sets.
2. Todos os sets da fase de grupos devem ser ate 11 pontos.
3. Os criterios de desempate devem ser aplicados exatamente nesta ordem:
   1. Vitorias.
   2. Saldo de sets.
   3. Saldo de pontos.

### Classificados para Mata-Mata Principal

1. 3 melhores do Grupo A.
2. 3 melhores do Grupo B.
3. 2 melhores do Grupo C.

### Regras dos Jogos

| Tipo de jogo | Formato | Pontuacao dos sets |
| --- | --- | --- |
| Jogos principais | Melhor de 3 sets | Ate 11 pontos |
| Jogos de disputa de posicao | 1 set | Ate 11 pontos |

### Mata-Mata Principal

| Jogo | Fase | Confronto |
| ---: | --- | --- |
| 5 | Quartas de final | 1o Grupo A vs 3o Grupo B |
| 6 | Quartas de final | 1o Grupo C vs 2o Grupo A |
| 7 | Quartas de final | 1o Grupo B vs 3o Grupo A |
| 8 | Quartas de final | 2o Grupo B vs 2o Grupo C |
| 9 | Disputa 5o ao 8o | Perdedor jogo 5 vs Perdedor jogo 6 |
| 10 | Disputa 5o ao 8o | Perdedor jogo 7 vs Perdedor jogo 8 |
| 11 | Disputa 7o e 8o | Perdedor jogo 9 vs Perdedor jogo 10 |
| 12 | Disputa 5o e 6o | Vencedor jogo 9 vs Vencedor jogo 10 |
| 13 | Semifinal | Vencedor jogo 5 vs Vencedor jogo 6 |
| 14 | Semifinal | Vencedor jogo 7 vs Vencedor jogo 8 |
| 15 | Disputa 3o lugar | Perdedor jogo 13 vs Perdedor jogo 14 |
| 16 | Final | Vencedor jogo 13 vs Vencedor jogo 14 |

### Definicao de Posicoes no Mata-Mata Principal

| Jogo | Resultado | Posicao |
| ---: | --- | --- |
| 11 | Perdedor | 8o lugar |
| 11 | Vencedor | 7o lugar |
| 12 | Perdedor | 6o lugar |
| 12 | Vencedor | 5o lugar |
| 15 | Perdedor | 4o lugar |
| 15 | Vencedor | 3o lugar |
| 16 | Perdedor | 2o lugar |
| 16 | Vencedor | Campeao |

### Disputa do 12o ao 14o Lugar

| Jogo | Confronto | Resultado |
| ---: | --- | --- |
| 1 | 5o Grupo A vs 5o Grupo B | Perdedor fica em 14o lugar |
| 2 | Vencedor jogo 1 vs 4o Grupo C | Perdedor fica em 13o lugar, vencedor fica em 12o lugar |

### Disputa do 9o ao 11o Lugar

| Jogo | Confronto | Resultado |
| ---: | --- | --- |
| 3 | 4o Grupo A vs 4o Grupo B | Perdedor fica em 11o lugar |
| 4 | Vencedor jogo 3 vs 3o Grupo C | Perdedor fica em 10o lugar, vencedor fica em 9o lugar |

## 12. Modelo de Dados

### Entidades Principais

| Entidade | Responsabilidade |
| --- | --- |
| Group | Representa um grupo da fase de classificacao |
| Team | Representa uma dupla participante |
| Match | Representa uma partida de grupo, mata-mata ou posicao |
| MatchSet | Representa um set de uma partida |

### Group

| Campo | Tipo sugerido | Obrigatorio | Observacao |
| --- | --- | --- | --- |
| id | AutoField ou BigAutoField | Sim | Identificador |
| name | CharField | Sim | Exemplo: `A`, `B`, `C` |

### Team

| Campo | Tipo sugerido | Obrigatorio | Observacao |
| --- | --- | --- | --- |
| id | AutoField ou BigAutoField | Sim | Identificador |
| player1_name | CharField | Sim | Nome do primeiro jogador |
| player2_name | CharField | Sim | Nome do segundo jogador |
| group | ForeignKey(Group) | Sim | Grupo da dupla |

### Match

| Campo | Tipo sugerido | Obrigatorio | Observacao |
| --- | --- | --- | --- |
| id | AutoField ou BigAutoField | Sim | Identificador |
| phase | CharField com choices | Sim | Fase da partida |
| match_number | PositiveIntegerField | Sim | Numero oficial do jogo quando aplicavel |
| bracket_type | CharField com choices | Sim | Grupo, principal ou posicoes |
| team_a | ForeignKey(Team) | Nao | Pode ser vazio enquanto confronto nao esta definido |
| team_b | ForeignKey(Team) | Nao | Pode ser vazio enquanto confronto nao esta definido |
| winner | ForeignKey(Team) | Nao | Preenchido quando houver vencedor valido |
| status | CharField com choices | Sim | Estado da partida |
| best_of | PositiveSmallIntegerField | Sim | `1` ou `3` |
| scheduled_date | DateTimeField | Nao | Data e hora planejada, se houver |
| source_match_winner | ForeignKey(Match) | Nao | Jogo de origem para vencedor, se aplicavel |
| source_match_loser | ForeignKey(Match) | Nao | Jogo de origem para perdedor, se aplicavel |
| sort_order | PositiveIntegerField | Sim | Ordenacao de exibicao |
| created_at | DateTimeField | Sim | Criacao |
| updated_at | DateTimeField | Sim | Atualizacao |

### MatchSet

| Campo | Tipo sugerido | Obrigatorio | Observacao |
| --- | --- | --- | --- |
| id | AutoField ou BigAutoField | Sim | Identificador |
| match | ForeignKey(Match) | Sim | Partida relacionada |
| set_number | PositiveSmallIntegerField | Sim | Ordem do set |
| team_a_points | PositiveSmallIntegerField | Sim | Pontos da dupla A |
| team_b_points | PositiveSmallIntegerField | Sim | Pontos da dupla B |

### Enumeracoes Sugeridas

#### MatchStatus

| Valor | Descricao |
| --- | --- |
| `pending` | Partida criada, mas ainda sem resultado |
| `ready` | Partida com duas duplas definidas e apta a receber resultado |
| `finished` | Partida encerrada com vencedor valido |

#### BracketType

| Valor | Descricao |
| --- | --- |
| `group` | Fase de grupos |
| `main` | Mata-mata principal |
| `placement` | Disputa de posicoes |

#### MatchPhase

| Valor | Descricao |
| --- | --- |
| `group_stage` | Fase de grupos |
| `quarterfinal` | Quartas de final |
| `fifth_to_eighth` | Disputa de 5o ao 8o |
| `seventh_place` | Disputa de 7o e 8o |
| `fifth_place` | Disputa de 5o e 6o |
| `semifinal` | Semifinal |
| `third_place` | Disputa de 3o lugar |
| `final` | Final |
| `twelfth_to_fourteenth` | Disputa do 12o ao 14o |
| `ninth_to_eleventh` | Disputa do 9o ao 11o |

### Restricoes de Banco Recomendadas

1. `Group.name` deve ser unico.
2. `Match.match_number` deve ser unico por `bracket_type`, quando preenchido.
3. `MatchSet.match` e `MatchSet.set_number` devem ser unicos em conjunto.
4. Uma dupla nao deve enfrentar a si mesma.
5. Partidas de grupo nao devem ser duplicadas para o mesmo par de duplas.

## 13. Regras de Validacao e Consistencia

### Validacoes de Match

1. Uma partida finalizada deve ter `team_a`, `team_b` e `winner` preenchidos.
2. O vencedor deve ser obrigatoriamente `team_a` ou `team_b`.
3. Uma partida finalizada deve possuir quantidade de sets compativel com `best_of`.
4. Uma partida com `best_of = 3` deve terminar quando uma dupla vencer 2 sets.
5. Uma partida com `best_of = 1` deve possuir exatamente 1 set valido e vencedor definido.
6. Uma partida nao pode ser finalizada empatada.
7. Uma partida nao pode ter `team_a` igual a `team_b`.
8. Uma partida com status `pending` pode ter duplas ausentes se depender de classificacao ou resultados futuros.
9. Uma partida com status `ready` deve ter `team_a` e `team_b` preenchidos.
10. Uma partida com status `finished` nao deve aceitar vencedor inconsistente com os sets.

### Validacoes de MatchSet

1. `set_number` deve iniciar em 1 e respeitar o limite de `best_of` da partida.
2. `team_a_points` e `team_b_points` devem ser inteiros maiores ou iguais a 0.
3. Um set nao pode terminar empatado.
4. Um set deve ter pelo menos uma dupla com 11 pontos.
5. Para o escopo atual, sets devem ser considerados ate 11 pontos.
6. Resultados com ambos os lados acima de 11 pontos devem ser bloqueados, salvo se uma pergunta em aberto decidir regra de vantagem.
7. Uma partida melhor de 3 nao pode ter mais de 3 sets.
8. Uma partida de 1 set nao pode ter mais de 1 set.

### Validacoes de Consistencia Geral

1. Nao permitir partidas duplicadas.
2. Nao permitir resultados impossiveis.
3. Nao permitir finalizacao sem quantidade minima de sets vencidos.
4. Nao permitir propagacao para confronto dependente se a partida de origem nao estiver finalizada.
5. Se resultado de partida ja propagada for alterado, confrontos dependentes devem ser recalculados.
6. Se confronto dependente ja tiver resultado e uma origem for alterada, o sistema deve impedir a alteracao ou limpar os resultados dependentes de forma controlada. A opcao escolhida deve ser documentada na implementacao.

## 14. Fluxos Principais

### Fluxo Publico de Consulta

1. Usuario acessa `/`.
2. Sistema exibe resumo do campeonato e links de navegacao.
3. Usuario acessa `/groups`, `/playoffs` ou `/placements`.
4. Sistema consulta dados salvos e renderiza tabelas ou brackets.
5. Usuario atualiza a pagina manualmente para ver novos resultados.

### Fluxo Administrativo de Resultado

1. Administrador acessa `/admin/login`.
2. Administrador autentica no Django Admin.
3. Administrador abre uma partida.
4. Administrador informa ou edita os sets.
5. Administrador marca a partida como finalizada.
6. Sistema valida sets, calcula vencedor e salva a partida.
7. Sistema recalcula classificacao ou propaga vencedor/perdedor conforme o tipo da partida.
8. Paginas publicas passam a refletir o novo estado apos recarregamento.

### Fluxo de Seed Inicial

1. Administrador ou deploy executa `python manage.py seed_tournament`.
2. Sistema cria grupos A, B e C.
3. Sistema cria as 14 duplas oficiais.
4. Sistema cria partidas de todos contra todos dentro de cada grupo.
5. Sistema deixa partidas futuras de mata-mata e posicoes pendentes ou as gera posteriormente quando houver classificacao.

### Fluxo de Recalculo Manual

1. Administrador executa `python manage.py recalculate_tournament`.
2. Sistema recalcula vencedores a partir dos sets.
3. Sistema recalcula classificacoes dos grupos.
4. Sistema atualiza confrontos de playoffs e posicoes se houver dados suficientes.
5. Sistema propaga vencedores e perdedores de partidas finalizadas.

## 15. Regras de Geracao Automatica de Partidas

### Partidas de Grupo

1. Cada dupla deve enfrentar todas as outras duplas do mesmo grupo uma unica vez.
2. Grupo A com 5 duplas deve gerar 10 partidas.
3. Grupo B com 5 duplas deve gerar 10 partidas.
4. Grupo C com 4 duplas deve gerar 6 partidas.
5. Total da fase de grupos: 26 partidas.
6. Todas as partidas de grupo devem ter `bracket_type = group`, `phase = group_stage` e `best_of = 3`.
7. Partidas de grupo nao devem usar os numeros oficiais 1 a 16 reservados para disputas de posicao e mata-mata, salvo decisao explicita de implementacao.

### Geracao do Mata-Mata Principal

Quando houver classificacao suficiente, o sistema deve gerar ou atualizar:

1. Jogo 5: 1o Grupo A vs 3o Grupo B.
2. Jogo 6: 1o Grupo C vs 2o Grupo A.
3. Jogo 7: 1o Grupo B vs 3o Grupo A.
4. Jogo 8: 2o Grupo B vs 2o Grupo C.

Os jogos 9 a 16 devem existir como partidas pendentes ou ser criados conforme as origens forem finalizadas. Para simplicidade de exibicao, recomenda-se criar todos os jogos 5 a 16 desde o inicio do bracket principal, preenchendo `team_a` e `team_b` conforme as origens forem conhecidas.

### Geracao das Disputas de Posicao

Quando houver classificacao suficiente, o sistema deve gerar ou atualizar:

1. Jogo 1: 5o Grupo A vs 5o Grupo B.
2. Jogo 2: Vencedor jogo 1 vs 4o Grupo C.
3. Jogo 3: 4o Grupo A vs 4o Grupo B.
4. Jogo 4: Vencedor jogo 3 vs 3o Grupo C.

Jogos de disputa de posicao devem ter `bracket_type = placement` e `best_of = 1`.

### Propagacao de Vencedores e Perdedores

| Origem | Destino | Regra |
| --- | --- | --- |
| Jogo 5 | Jogo 9 | Perdedor vai para jogo 9 |
| Jogo 6 | Jogo 9 | Perdedor vai para jogo 9 |
| Jogo 7 | Jogo 10 | Perdedor vai para jogo 10 |
| Jogo 8 | Jogo 10 | Perdedor vai para jogo 10 |
| Jogo 9 | Jogo 11 | Perdedor vai para jogo 11 |
| Jogo 10 | Jogo 11 | Perdedor vai para jogo 11 |
| Jogo 9 | Jogo 12 | Vencedor vai para jogo 12 |
| Jogo 10 | Jogo 12 | Vencedor vai para jogo 12 |
| Jogo 5 | Jogo 13 | Vencedor vai para jogo 13 |
| Jogo 6 | Jogo 13 | Vencedor vai para jogo 13 |
| Jogo 7 | Jogo 14 | Vencedor vai para jogo 14 |
| Jogo 8 | Jogo 14 | Vencedor vai para jogo 14 |
| Jogo 13 | Jogo 15 | Perdedor vai para jogo 15 |
| Jogo 14 | Jogo 15 | Perdedor vai para jogo 15 |
| Jogo 13 | Jogo 16 | Vencedor vai para jogo 16 |
| Jogo 14 | Jogo 16 | Vencedor vai para jogo 16 |
| Jogo 1 | Jogo 2 | Vencedor vai para jogo 2 |
| Jogo 3 | Jogo 4 | Vencedor vai para jogo 4 |

## 16. Calculo de Classificacao

### Estatisticas por Dupla

Para cada dupla dentro de seu grupo, calcular:

1. Jogos: quantidade de partidas finalizadas no grupo envolvendo a dupla.
2. Vitorias: quantidade de partidas vencidas.
3. Derrotas: quantidade de partidas perdidas.
4. Sets vencidos: quantidade de sets vencidos.
5. Sets perdidos: quantidade de sets perdidos.
6. Saldo de sets: sets vencidos menos sets perdidos.
7. Pontos marcados: soma dos pontos feitos em todos os sets.
8. Pontos sofridos: soma dos pontos sofridos em todos os sets.
9. Saldo de pontos: pontos marcados menos pontos sofridos.

### Ordenacao Oficial

As duplas devem ser ordenadas exatamente por:

1. Maior numero de vitorias.
2. Maior saldo de sets.
3. Maior saldo de pontos.

### Empate Persistente

Se duas ou mais duplas permanecerem empatadas apos os tres criterios oficiais, o sistema nao deve inventar criterio esportivo adicional. Para estabilidade visual, pode ordenar por nome da dupla ou id, mas deve registrar que o empate permanece sem criterio esportivo definido.

### Eventos que Disparam Recalculo

1. Criacao de `MatchSet`.
2. Edicao de `MatchSet`.
3. Exclusao de `MatchSet`.
4. Alteracao de status de `Match`.
5. Alteracao de duplas de uma partida.
6. Alteracao manual do vencedor, se permitido pelo admin.
7. Execucao do comando `recalculate_tournament`.

## 17. Interface e UX

### Direcao Visual

1. Tema escuro.
2. Estetica esportiva inspirada em Liquipedia, HLTV e Challonge.
3. Tabelas compactas.
4. Cards de partidas com placar em destaque.
5. Contraste alto para leitura em ambiente de evento.
6. Navegacao simples e persistente.
7. Evitar elementos decorativos que prejudiquem consulta rapida.

### Layout Base

1. Cabecalho com nome PicklePesp e links para Inicio, Grupos, Mata-mata e Posicoes.
2. Conteudo centralizado com largura maxima em desktop.
3. Fundo escuro com paineis em tons de cinza escuro.
4. Cores de destaque para vencedores, status finalizado e chamadas importantes.
5. Rodape simples opcional.

### Tela de Grupos

Cada grupo deve mostrar:

1. Posicao.
2. Dupla.
3. Jogos.
4. Vitorias.
5. Derrotas.
6. Saldo de sets.
7. Saldo de pontos.
8. Lista de partidas.
9. Placares.
10. Status.

### Tela de Brackets

1. Exibir confrontos em formato de chave.
2. Exibir nome das duplas.
3. Exibir placar resumido por sets.
4. Destacar vencedores.
5. Mostrar partidas pendentes com identificacao clara de origem, quando a dupla ainda nao estiver definida.

## 18. Responsividade

1. A aplicacao deve ser mobile-first.
2. Todas as paginas publicas devem funcionar em celular.
3. Tabelas devem ser compactas e legiveis em telas pequenas.
4. Em mobile, brackets podem ser empilhados verticalmente.
5. Em desktop, brackets devem usar disposicao horizontal quando houver espaco.
6. A navegacao deve ser facil de tocar em telas pequenas.
7. O tamanho de fonte deve preservar legibilidade durante consulta rapida.
8. Conteudos largos devem evitar rolagem horizontal desnecessaria.

## 19. Administracao

### Uso do Django Admin

O Django Admin sera a interface administrativa principal. Nao deve ser criado painel customizado complexo.

### Cadastros no Admin

1. Group.
2. Team.
3. Match.
4. MatchSet.

### Recomendacoes de Admin

1. Usar `TabularInline` para editar sets dentro de uma partida.
2. Exibir filtros por `bracket_type`, `phase` e `status`.
3. Permitir busca por nomes de jogadores.
4. Exibir colunas com numero do jogo, fase, duplas, status e vencedor.
5. Tornar campos calculados somente leitura quando apropriado.
6. Validar resultados antes de salvar.
7. Acionar recalculo apos salvar partida e sets.

### Permissoes

1. Apenas usuarios autenticados com acesso ao admin podem alterar dados.
2. Usuarios publicos nao podem alterar dados.
3. Nao ha necessidade de permissoes avancadas por perfil no escopo atual.

## 20. Seed Inicial de Dados

### Comando Recomendado

```bash
python manage.py seed_tournament
```

### Dados Criados

1. Grupo A.
2. Grupo B.
3. Grupo C.
4. 14 duplas oficiais.
5. 26 partidas de grupos em todos contra todos.
6. Estrutura inicial dos jogos 1 a 4 de posicoes, se houver classificacao suficiente ou como pendentes.
7. Estrutura inicial dos jogos 5 a 16 do mata-mata principal, se houver classificacao suficiente ou como pendentes.

### Idempotencia

O comando deve ser idempotente:

1. Nao deve duplicar grupos.
2. Nao deve duplicar duplas.
3. Nao deve duplicar partidas.
4. Deve poder ser executado novamente com seguranca em ambiente de desenvolvimento.

### Comando de Recalculo

```bash
python manage.py recalculate_tournament
```

Esse comando deve recalcular classificacao, vencedores e propagacoes a partir dos dados existentes.

## 21. Testes

### Estrategia Minima

Usar testes automatizados do Django com banco de teste padrao.

### Testes de Dominio

1. Calculo de classificacao por grupo.
2. Desempate por vitorias.
3. Desempate por saldo de sets.
4. Desempate por saldo de pontos.
5. Cenario de empate persistente apos todos os criterios oficiais.
6. Validacao de sets validos.
7. Bloqueio de sets empatados.
8. Bloqueio de sets acima de 11 pontos enquanto regra de vantagem nao estiver definida.
9. Definicao de vencedor em melhor de 3.
10. Definicao de vencedor em jogo de 1 set.
11. Bloqueio de partida finalizada sem vencedor valido.
12. Bloqueio de vencedor que nao participa da partida.

### Testes de Geracao

1. Geracao das 26 partidas de grupos.
2. Geracao das quartas de final conforme jogos 5 a 8.
3. Geracao das disputas de 9o ao 14o conforme jogos 1 a 4.
4. Propagacao de vencedores para semifinais e final.
5. Propagacao de perdedores para disputas de 5o ao 8o e 3o lugar.
6. Propagacao nas disputas de posicoes.

### Testes de Interface

1. Renderizacao de `/` com status HTTP 200.
2. Renderizacao de `/groups` com status HTTP 200.
3. Renderizacao de `/playoffs` com status HTTP 200.
4. Renderizacao de `/placements` com status HTTP 200.
5. Exibicao de grupos e duplas nas paginas publicas.

### Testes de Admin

1. Usuario nao autenticado deve ser redirecionado ao acessar `/admin`.
2. Superusuario deve conseguir acessar `/admin`.
3. Salvamento de placar invalido deve gerar erro.
4. Salvamento de placar valido deve atualizar vencedor.

## 22. Deploy

### Requisitos

1. A aplicacao deve subir com `docker compose up`.
2. O Django deve rodar com Gunicorn.
3. O Nginx deve atuar como proxy reverso quando aplicavel.
4. O SQLite deve ser persistido em volume.
5. Arquivos estaticos devem ser coletados com `collectstatic`.

### Dockerfile

O Dockerfile deve:

1. Usar imagem Python compativel com Python 3.12 ou superior.
2. Instalar dependencias de `requirements.txt`.
3. Copiar o projeto para o container.
4. Executar migracoes conforme estrategia de entrada definida.
5. Expor a aplicacao via Gunicorn.

### docker-compose.yml

O Docker Compose deve conter:

1. Servico Django.
2. Volume para SQLite.
3. Volume ou mapeamento para arquivos estaticos, se necessario.
4. Servico Nginx quando aplicavel ao deploy.

### Variaveis de Ambiente

| Variavel | Obrigatoria | Descricao |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Sim | Chave secreta do Django |
| `DJANGO_DEBUG` | Sim | `0` em producao, `1` em desenvolvimento |
| `DJANGO_ALLOWED_HOSTS` | Sim | Hosts permitidos separados por virgula |
| `DATABASE_PATH` | Nao | Caminho do SQLite, se diferente do padrao |

### Comandos Operacionais

```bash
docker compose up
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_tournament
```

## 23. Observabilidade e Operacao Simples

1. Usar logs padrao do Django e Gunicorn em stdout/stderr.
2. Registrar erros de validacao relevantes no admin sem expor detalhes tecnicos ao publico.
3. Nao adicionar ferramentas externas de observabilidade no escopo inicial.
4. Manter pagina publica resiliente a confrontos ainda nao definidos.
5. Manter comando de recalculo para recuperacao operacional simples.
6. Fazer backup do arquivo SQLite antes de alteracoes manuais importantes.
7. Documentar procedimento de restauracao simples do volume SQLite.

## 24. Plano Incremental de Implementacao

### Roadmap de Sprints

#### Fase 1: Setup Django, Docker e Estrutura Base

Entregaveis:

1. Projeto Django criado.
2. App `tournament` criado.
3. Configuracao basica de settings, urls e templates.
4. Dockerfile funcional.
5. docker-compose.yml funcional.
6. Gunicorn configurado.
7. Estrutura de templates e static criada.

Tarefas:

- [x] Criar projeto Django.
- [x] Criar app `tournament`.
- [x] Configurar `settings.py` para templates, static e SQLite.
- [x] Configurar rotas publicas iniciais.
- [x] Criar Dockerfile.
- [x] Criar docker-compose.yml.
- [x] Validar subida com `docker compose up`.

Criterios de conclusao:

1. Aplicacao sobe localmente.
2. `/admin` responde.
3. `/` responde com pagina basica.

#### Fase 2: Modelos, Admin e Seed Inicial

Entregaveis:

1. Models `Group`, `Team`, `Match` e `MatchSet`.
2. Migrations criadas.
3. Admin configurado.
4. Seed inicial com grupos, duplas e partidas de grupo.

Tarefas:

- [x] Implementar models principais.
- [x] Criar choices de fase, status e tipo de bracket.
- [x] Configurar restricoes de unicidade.
- [x] Registrar models no admin.
- [x] Criar inline de sets em partidas.
- [x] Criar comando `seed_tournament`.
- [x] Validar idempotencia do seed.

Criterios de conclusao:

1. Admin permite visualizar e editar entidades.
2. Seed cria todos os grupos e duplas oficiais.
3. Seed cria 26 partidas de grupos sem duplicidade.

#### Fase 3: Validacoes e Calculo de Classificacao

Entregaveis:

1. Validacoes de `Match` e `MatchSet`.
2. Calculo automatico de vencedor.
3. Calculo de estatisticas por grupo.
4. Ordenacao oficial da classificacao.
5. Testes das regras criticas de placar e classificacao.

Tarefas:

- [x] Implementar validacao de sets empatados.
- [x] Implementar validacao de limite de pontos ate 11.
- [x] Implementar validacao de quantidade de sets por `best_of`.
- [x] Implementar validacao de vencedor pertencente a partida.
- [x] Implementar calculo de vencedor a partir dos sets.
- [x] Implementar calculo de jogos, vitorias e derrotas.
- [x] Implementar calculo de saldo de sets.
- [x] Implementar calculo de saldo de pontos.
- [x] Implementar ordenacao por vitorias, saldo de sets e saldo de pontos.
- [x] Criar testes automatizados para validacoes.
- [x] Criar testes automatizados para classificacao.

Criterios de conclusao:

1. Partidas invalidas nao podem ser finalizadas.
2. Vencedor e calculado corretamente para melhor de 3 e jogo unico.
3. Classificacao respeita os tres criterios oficiais.
4. Testes criticos passam.

#### Fase 4: Paginas Publicas de Grupos

Entregaveis:

1. Pagina `/groups` completa.
2. Tabelas de classificacao por grupo.
3. Lista de partidas por grupo.
4. Layout mobile-first.

Tarefas:

- [ ] Criar view de grupos.
- [ ] Criar selector para buscar classificacao.
- [ ] Criar template de tabela de classificacao.
- [ ] Criar template de lista de partidas.
- [ ] Aplicar visual escuro e compacto.
- [ ] Testar renderizacao em mobile e desktop.

Criterios de conclusao:

1. `/groups` exibe grupos A, B e C.
2. Cada grupo exibe classificacao e partidas.
3. Dados exibidos refletem resultados salvos.

#### Fase 5: Geracao e Exibicao de Brackets

Entregaveis:

1. Geracao dos jogos 1 a 4 de posicoes.
2. Geracao dos jogos 5 a 16 do mata-mata principal.
3. Paginas `/playoffs` e `/placements`.
4. Templates de bracket.

Tarefas:

- [ ] Implementar geracao dos jogos 5 a 8.
- [ ] Implementar estrutura dos jogos 9 a 16.
- [ ] Implementar geracao dos jogos 1 a 4.
- [ ] Criar view de playoffs.
- [ ] Criar view de placements.
- [ ] Criar template de bracket responsivo.
- [ ] Criar testes de geracao de confrontos.

Criterios de conclusao:

1. Jogos 5 a 8 seguem exatamente o regulamento.
2. Jogos 1 a 4 seguem exatamente o regulamento.
3. Paginas de brackets exibem confrontos definidos e pendentes.

#### Fase 6: Recalculo Automatico e Propagacao de Resultados

Entregaveis:

1. Rotina de recalculo global.
2. Propagacao de vencedores e perdedores.
3. Atualizacao automatica apos salvar resultado.
4. Management command de recalculo.

Tarefas:

- [ ] Implementar servico de recalculo global.
- [ ] Implementar propagacao no mata-mata principal.
- [ ] Implementar propagacao nas disputas de posicoes.
- [ ] Integrar recalculo ao salvamento no admin.
- [ ] Criar comando `recalculate_tournament`.
- [ ] Criar testes de propagacao.

Criterios de conclusao:

1. Resultado salvo atualiza confrontos dependentes.
2. Comando manual reconstrui estado derivado.
3. Testes de propagacao passam.

#### Fase 7: UX, Responsividade e Acabamento Visual

Entregaveis:

1. Tema escuro final.
2. Ajustes mobile-first.
3. Cards e tabelas refinados.
4. Navegacao publica consistente.

Tarefas:

- [ ] Refinar `base.html`.
- [ ] Refinar pagina inicial.
- [ ] Melhorar tabelas em telas pequenas.
- [ ] Melhorar brackets em desktop.
- [ ] Melhorar brackets em mobile.
- [ ] Destacar vencedores e status.

Criterios de conclusao:

1. Aplicacao e legivel em celular.
2. Navegacao publica e simples.
3. Visual final segue tema escuro esportivo.

#### Fase 8: Testes, Hardening e Deploy

Entregaveis:

1. Cobertura minima dos fluxos criticos.
2. Validacao de deploy com Docker Compose.
3. Configuracao de Nginx.
4. Documentacao operacional curta.

Tarefas:

- [ ] Completar testes de dominio.
- [ ] Completar testes de views publicas.
- [ ] Testar admin basico.
- [ ] Configurar Nginx.
- [ ] Validar Gunicorn.
- [ ] Validar persistencia do SQLite em volume.
- [ ] Documentar comandos operacionais.

Criterios de conclusao:

1. Testes automatizados passam.
2. `docker compose up` sobe a aplicacao.
3. Dados persistem apos reinicio do container.
4. Admin e paginas publicas funcionam em ambiente containerizado.

## 25. Criterios de Aceite

### Classificacao

| Cenario | Criterio de aceite |
| --- | --- |
| Todas as partidas de grupo foram finalizadas | Quando a classificacao for exibida, as duplas devem aparecer ordenadas por vitorias, saldo de sets e saldo de pontos |
| Duas duplas empatam em vitorias | A dupla com maior saldo de sets deve ficar acima |
| Duas duplas empatam em vitorias e saldo de sets | A dupla com maior saldo de pontos deve ficar acima |
| Empate permanece apos todos os criterios oficiais | O sistema deve manter ordenacao estavel sem inventar criterio esportivo adicional |

### Validacao de Resultados

| Cenario | Criterio de aceite |
| --- | --- |
| Administrador informa set empatado | Sistema impede salvamento e exibe erro |
| Administrador informa placar acima do limite permitido | Sistema impede salvamento e exibe erro |
| Administrador finaliza partida sem vencedor valido | Sistema impede salvamento e exibe erro |
| Administrador informa vencedor que nao participa da partida | Sistema impede salvamento e exibe erro |
| Partida melhor de 3 tem apenas uma vitoria de set | Sistema impede finalizacao |

### Mata-Mata Principal

| Cenario | Criterio de aceite |
| --- | --- |
| Classificados estao definidos | Jogos 5 a 8 devem seguir exatamente o mapeamento oficial |
| Jogo 5 e finalizado | Vencedor deve ir para jogo 13 e perdedor para jogo 9 |
| Jogos 13 e 14 sao finalizados | Vencedores devem ir para jogo 16 e perdedores para jogo 15 |
| Jogo 16 e finalizado | Vencedor deve ser identificado como campeao e perdedor como 2o lugar |

### Disputas de Posicao

| Cenario | Criterio de aceite |
| --- | --- |
| Classificacao dos grupos esta definida | Jogos 1 a 4 devem seguir exatamente o regulamento |
| Jogo 1 e finalizado | Perdedor deve ser 14o lugar e vencedor deve ir para jogo 2 |
| Jogo 2 e finalizado | Perdedor deve ser 13o lugar e vencedor deve ser 12o lugar |
| Jogo 3 e finalizado | Perdedor deve ser 11o lugar e vencedor deve ir para jogo 4 |
| Jogo 4 e finalizado | Perdedor deve ser 10o lugar e vencedor deve ser 9o lugar |

### Paginas Publicas

| Cenario | Criterio de aceite |
| --- | --- |
| Usuario acessa `/` | Sistema exibe resumo e links principais |
| Usuario acessa `/groups` | Sistema exibe classificacao e partidas dos grupos A, B e C |
| Usuario acessa `/playoffs` | Sistema exibe bracket principal |
| Usuario acessa `/placements` | Sistema exibe disputas de posicoes |
| Usuario acessa pelo celular | Conteudo permanece legivel e funcional |

### Deploy

| Cenario | Criterio de aceite |
| --- | --- |
| Operador executa `docker compose up` | Aplicacao sobe sem passos manuais complexos |
| Container reinicia | Dados do SQLite persistem em volume |
| Admin acessa `/admin` | Login padrao do Django funciona |

## 26. Riscos e Mitigacoes

| Risco | Impacto | Mitigacao |
| --- | --- | --- |
| Ambiguidade sobre placares acima de 11 | Pode bloquear resultados reais se houver regra de vantagem | Registrar pergunta em aberto e manter validacao simples ate decisao |
| Alteracao de resultado ja propagado | Pode deixar brackets inconsistentes | Usar recalculo global transacional e testes de propagacao |
| Edicao manual incorreta no admin | Pode corromper estado do campeonato | Validacoes fortes em models/forms/admin |
| SQLite sem backup | Risco de perda de dados | Persistir volume e orientar backup do arquivo SQLite |
| Bracket horizontal ruim em celular | Baixa usabilidade durante evento | Usar layout empilhado em mobile |
| Regras espalhadas por views/admin | Manutencao dificil | Centralizar regras em `services.py` e cobrir com testes |
| Seed duplicando dados | Dados inconsistentes | Comando idempotente com chaves naturais e restricoes de unicidade |
| Dependencia de criterio de desempate nao definido | Discussao durante campeonato | Nao inventar criterio; registrar empate persistente e pergunta em aberto |

## 27. Perguntas em Aberto

1. Em sets ate 11 pontos, existe regra de vantagem por 2 pontos ou o placar maximo deve ser exatamente 11 para o vencedor?
2. Se duas duplas continuarem empatadas apos vitorias, saldo de sets e saldo de pontos, qual criterio oficial deve ser usado, se houver?
3. As partidas terao horario definido ou `scheduled_date` sera usado apenas opcionalmente?
4. O administrador podera alterar resultado de partida que ja propagou duplas para jogos seguintes com resultados preenchidos?
5. Ao alterar resultado ja propagado, o sistema deve bloquear a alteracao ou limpar automaticamente resultados dependentes?
6. A pagina inicial deve exibir quantos proximos jogos pendentes?
7. A ordem das partidas de grupo deve seguir alguma agenda especifica ou pode ser gerada automaticamente por combinacao simples?
8. Deve haver exibicao explicita de colocacao final consolidada apos todos os jogos?
9. O nome oficial do grupo deve ser exibido como `Grupo A` ou apenas `A` internamente com formatacao no template?
10. Ha necessidade de proteger o site publico por senha ou ele sera totalmente publico dentro do ambiente de acesso?
