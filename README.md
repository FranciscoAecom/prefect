# Data Pipeline

Pipeline de validacao, transformacao e padronizacao de arquivos geoespaciais
em lote, orientado pela planilha de ingestao `input/st_Ingest_parameter.xlsx`.

O projeto processa bases `.shp` e `.gpkg`, valida schemas e dominios,
normaliza atributos, repara geometrias, calcula metricas espaciais e grava
saidas finais em GeoPackage.

## Objetivo

- Ler uma fila de processamento a partir da aba `datas` da planilha de ingestao.
- Processar arquivos geoespaciais por perfil de regras em `rules/`.
- Validar estrutura tabular contra a aba `dictionaries`.
- Preservar atributos originais com prefixo `sdb_*`.
- Gerar campos tratados e padronizados com prefixo `acm_*`.
- Produzir saidas em `output/<theme_folder>/` com logs e relatorios auxiliares.

## Entradas Suportadas

- Arquivos `.shp`.
- Arquivos `.gpkg`.
- Pastas contendo `.shp` e `.gpkg`, inclusive em subpastas.

Arquivos `.zip` nao sao processados diretamente.

Uma linha entra na fila quando:

- `status = Waiting Update`;
- `path_shapefile_temp` aponta para um arquivo ou pasta suportada;
- `theme_folder` encontra um perfil correspondente em `rules/`.

## Estrutura

```text
data-pipeline/
|-- main.py
|-- settings.py
|-- input/
|   `-- st_Ingest_parameter.xlsx
|-- output/
|-- core/
|   |-- ingest/
|   |-- processing/
|   |-- queue/
|   |-- rules/
|   |-- spatial/
|   |-- validation/
|   `-- output/
|-- projects/
|   |-- configs.py
|   |-- registry.py
|   `-- functions/
|-- rules/
|   |-- _template/
|   |-- app_car/
|   |-- reserva_legal_car/
|   |-- estado/
|   `-- autorizacao_para_supressao_vegetal/
|-- readme/
`-- tests/
```

Componentes principais:

- `main.py`: ponto de entrada da fila automatica.
- `settings.py`: configuracoes centrais do pipeline.
- `core/`: motor de ingestao, validacao, processamento, regras e escrita.
- `projects/`: configuracoes e funcoes especificas por projeto.
- `rules/`: perfis JSON modulares por tema e UF.
- `input/`: planilha de ingestao.
- `output/`: resultados gerados.

## Requisitos

- Python 3.14 ou superior.
- Dependencias declaradas em `pyproject.toml`.
- Ambiente recomendado com `uv`.
- Prefect 3 para orquestracao do pipeline.

Clone do repositorio:

```powershell
git clone https://github.com/FranciscoAecom/prefect.git
cd prefect
```

Instalacao das dependencias:

```powershell
uv sync
```

Alternativa com `pip`:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.14 -m pip install --upgrade pip
py -3.14 -m pip install -e .
```

## Como Usar

1. Atualize `input/st_Ingest_parameter.xlsx`.
2. Na aba `datas`, defina `status = Waiting Update` para as linhas que devem ser processadas.
3. Preencha `path_shapefile_temp`, `theme_folder` e `theme`.
4. Confira se existe um perfil correspondente em `rules/`.
5. Execute o pipeline:

```powershell
uv run python main.py
```

O comando acima executa o flow Prefect `Data Pipeline`, com uma task para
preparar a fila e uma task para cada registro processado.

Ou, usando o Python instalado diretamente:

```powershell
py -3.14 main.py
```

As saidas ficam em:

```text
output/<theme_folder>/
```

## Prefect

O projeto usa Prefect 3 para visualizar execucoes, agendar rotinas e disparar
bases especificas pelo painel.

### Painel Local

No primeiro terminal, dentro da pasta do projeto, inicie o servidor local:

```powershell
cd C:\Temp\Repositórios\prefect
uv run python -m prefect server start --host 127.0.0.1 --port 4200
```

Deixe esse terminal aberto. Ele fica segurando o servidor do Prefect.

Abra no navegador:

```text
http://127.0.0.1:4200
```

Em outro terminal, entre novamente na pasta do projeto:

```powershell
cd C:\Temp\Repositórios\prefect
```

Configure a API local do Prefect, se ainda nao estiver configurada:

```powershell
uv run python -m prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Depois execute o pipeline:

```powershell
uv run python main.py
```

Se o navegador mostrar `ERR_CONNECTION_REFUSED`, o servidor nao esta rodando
ou caiu. Inicie novamente o comando acima em um terminal separado.

Em alguns ambientes Windows, o comando `uv run prefect ...` pode falhar com
`uv trampoline failed to canonicalize script path`. Quando isso acontecer, use
sempre `uv run python -m prefect ...`.

Se a porta 4200 ja estiver ocupada, veja o processo que esta usando a porta:

```powershell
Get-NetTCPConnection -LocalPort 4200 | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

Depois veja o nome do processo:

```powershell
Get-Process -Id <PID>
```

Para encerrar o processo:

```powershell
Stop-Process -Id <PID> -Force
```

Tambem e possivel iniciar em outra porta:

```powershell
uv run python -m prefect server start --host 127.0.0.1 --port 4201
```

### Agendamento UR CAR

Para servir os agendamentos mensais das 27 bases `ur_car`, uma por dia do mes:

```powershell
uv run python serve_ur_car_schedule.py
```

Esse comando cria o deployment `CAR - Uso Restrito` com execucoes mensais as
02:00, no fuso `America/Sao_Paulo`. Cada agenda passa `theme_folders` para o
flow, entao a execucao do dia 1 roda apenas `ur_car_ac`, a do dia 2 roda
apenas `ur_car_al`, e assim por diante ate `ur_car_to` no dia 27.

Se os flows ou deployments forem deletados no painel do Prefect, o dashboard
ficara vazio. Para recriar o deployment e os agendamentos, deixe o servidor
Prefect aberto e rode novamente:

```powershell
uv run python serve_ur_car_schedule.py
```

Os runs agendados sao renomeados automaticamente para o nome da base, por
exemplo `ur_car_pi`. O nome mostrado na lista de runs pode aparecer primeiro
como um nome aleatorio do Prefect; depois o script de renomeacao troca para o
valor da base.

Para aplicar a renomeacao manualmente:

```powershell
uv run python rename_prefect_scheduled_runs.py
```

### Agendamento Estado

Para criar o deployment da base `estado` no painel do Prefect:

```powershell
uv run python serve_estado_schedule.py
```

Esse comando cria o deployment `Estado` com agenda diaria as 02:00, no fuso
`America/Sao_Paulo`, passando o parametro:

```json
{"theme_folders": ["estado"]}
```

Depois disso, o deployment aparece em `http://127.0.0.1:4200/deployments` e o
horario pode ser alterado pelo painel.

### Execucao Manual Pelo Terminal

Para executar uma base especifica pelo deployment:

```powershell
'{"theme_folders":["ur_car_pi"]}' | uv run prefect deployment run "Data Pipeline/CAR - Uso Restrito" --params -
```

Para executar todas as 27 bases `ur_car` de uma vez, informe todos os perfis
em `theme_folders`:

```powershell
'{"theme_folders":["ur_car_ac","ur_car_al","ur_car_am","ur_car_ap","ur_car_ba","ur_car_ce","ur_car_df","ur_car_es","ur_car_go","ur_car_ma","ur_car_mg","ur_car_ms","ur_car_mt","ur_car_pa","ur_car_pb","ur_car_pe","ur_car_pi","ur_car_pr","ur_car_rj","ur_car_rn","ur_car_ro","ur_car_rr","ur_car_rs","ur_car_sc","ur_car_se","ur_car_sp","ur_car_to"]}' | uv run prefect deployment run "Data Pipeline/CAR - Uso Restrito" --params -
```

Para listar flow runs:

```powershell
uv run prefect flow-run ls
```

Para ver deployments:

```powershell
uv run prefect deployment ls
```

### Alterar Horario Pelo Painel

No painel:

1. Va em `Deployments`.
2. Abra `CAR - Uso Restrito`.
3. Entre em `Configuration`.
4. Edite o cron da agenda desejada.
5. Salve.

O cron usa o formato:

```text
minuto hora dia-do-mes mes dia-da-semana
```

Exemplo para rodar todo dia 17 as 02:00:

```text
0 2 17 * *
```

Exemplo para rodar todo dia 16 as 15:19:

```text
19 15 16 * *
```

O agendamento usa o fuso `America/Sao_Paulo`.

Quando uma base e filtrada, o pipeline cria um lock local por base para evitar
duas execucoes concorrentes da mesma saida.

## Regras Modulares

Cada perfil em `rules/` deve conter cinco arquivos:

```text
rules/<projeto>/<perfil>/
|-- profile.json
|-- input_schema.json
|-- domains.json
|-- relations.json
`-- pipeline.json
```

Exemplo:

```text
theme_folder = app_car_es
perfil esperado = rules/app_car/app_car_es/
```

Associacoes principais:

- `app_car_*` usa `rules/app_car/`.
- `rl_car_*` usa `rules/reserva_legal_car/`.
- `estado` usa `rules/estado/`.
- `auth_supn` usa `rules/autorizacao_para_supressao_vegetal/`.

Use `rules/_template/` como base para novos perfis. O formato completo esta em
`readme/rules.md`.

## Convencoes de Colunas

- Colunas originais sao preservadas como `sdb_*`.
- Colunas tratadas, normalizadas ou derivadas sao gravadas como `acm_*`.
- Funcoes genericas do `core` nao devem sobrescrever valores `sdb_*`.
- Marcacoes tecnicas internas nao devem aparecer no GeoPackage final.

## Geometria

O pipeline:

- achata geometrias para 2D;
- repara geometrias invalidas quando possivel;
- valida geometrias OGC quando habilitado;
- calcula area, perimetro, longitude e latitude;
- usa `EPSG:4326` para saida e `EPSG:5880` para metricas;
- aplica validacao regional de bounding box para bases `app_car` e
  `reserva_legal_car`.

## Saidas

O arquivo principal de saida e sempre `.gpkg`.

Tambem podem ser gerados:

- log contextual `.txt`;
- relatorio de inconsistencias de dominio;
- relatorio de duplicados por atributos;
- relatorio de duplicados geometricos;
- relatorio de geometrias invalidas OGC;
- consolidado por grupo, quando `ENABLE_GROUP_CONSOLIDATION = True`.

## Configuracao

As constantes principais ficam em `settings.py`, incluindo:

- `INGEST_WORKBOOK_PATH`
- `INGEST_SHEET_NAME`
- `DICTIONARIES_SHEET_NAME`
- `INGEST_READY_STATUS`
- `OUTPUT_BASE`
- `RULES_BASE`
- `BATCH_SIZE`
- `CRS_WGS84`
- `CRS_EQUAL_AREA`
- `ENABLE_GROUP_CONSOLIDATION`
- `KEEP_INDIVIDUAL_OUTPUTS_WHEN_GROUPING`
- `USE_ARROW_IO`
- `INTERACTIVE_ATTRIBUTE_REVIEW`

Configuracoes por projeto ficam em `projects/configs.py`, e funcoes opcionais
ficam registradas em `projects/registry.py`.

## Testes

Executar a suite:

```powershell
uv run pytest
```

Ou:

```powershell
py -3.14 -m pytest
```

Validar especificamente os perfis de regras:

```powershell
py -3.14 -m unittest tests.test_rule_profiles_integration
```

## Documentacao

Documentacao complementar:

- `readme/README.md`: descricao operacional detalhada.
- `readme/rules.md`: contrato dos perfis modulares em `rules/`.

## Observacoes

- Os JSONs em `rules/` devem ser mantidos em UTF-8.
- Caminhos de regras, nomes de projeto, nomes de perfil e chaves em
  `projects/configs.py` devem permanecer em ASCII.
- Em ambientes nao interativos, mantenha `INTERACTIVE_ATTRIBUTE_REVIEW = False`.
- Se a entrada estiver em `EPSG:4326`, nao ha reprojecao desnecessaria.
- Em bases grandes, transformacoes espaciais sao feitas em fatias para reduzir
  risco de estouro de memoria.
