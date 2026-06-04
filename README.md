# Data Treatment Pipeline

Pipeline de validacao, transformacao e padronizacao de arquivos geoespaciais
em lote, orientado pela planilha de ingestao `input/st_Ingest_parameter.xlsx`.

O projeto processa bases `.shp` e `.gpkg`, valida schemas e dominios,
normaliza atributos, repara geometrias, calcula metricas espaciais e grava
saidas finais em GeoPackage.

## Objetivo

- Ler uma fila de processamento a partir da aba `datas` da planilha de ingestao.
- Processar arquivos geoespaciais por perfil de regras em `rules/`.
- Validar estrutura tabular contra o `input_schema.json` do perfil de regras.
- Preservar atributos originais com prefixo `sdb_*`.
- Gerar campos tratados e padronizados com prefixo `acm_*`.
- Produzir saidas em `output/<theme_folder>/` com logs e relatorios auxiliares.

## Entradas Suportadas

- Arquivos `.shp`.
- Arquivos `.gpkg`.
- Arquivos `.tif` e `.tiff` para tratamento raster com GDAL.
- Pastas contendo `.shp`, `.gpkg`, `.tif` e `.tiff`, inclusive em subpastas.

Arquivos `.zip` nao sao processados diretamente.

Uma linha entra na fila quando:

- `status` contem `treatment` para tratamento;
- `status` contem `download` para download automatico;
- `status` contem `publish` para publicacao;
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
|   |-- downloads/
|   |-- ingest/
|   |-- metadata/
|   |-- processing/
|   |-- publish/
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
|   |-- car_area_preservacao_permanente/
|   |-- car_reserva_legal/
|   |-- car_servidao_administrativa/
|   |-- car_uso_restrito/
|   |-- estado/
|   `-- autorizacao_para_supressao_vegetal/
|-- readme/
`-- tests/
```

Componentes principais:

- `main.py`: ponto de entrada da fila automatica.
- `settings.py`: configuracoes centrais do pipeline.
- `core/`: motor de ingestao, validacao, processamento, regras e escrita.
- `core/downloads/`: catalogo, conectores e utilitarios de download.
- `core/publish/`: descoberta, publicacao, titulos, SLD e XML para catalogo.
- `core/silver/`: persistencia da camada silver, saida principal, XML, SLD e qualidade.
- `core/rules/contracts.py`: contrato tecnico das chaves aceitas nos perfis JSON.
- `projects/`: configuracoes e funcoes especificas por projeto.
- `rules/`: perfis JSON modulares por tema e UF.
- `input/`: planilha de ingestao.
- `output/`: resultados gerados.

## Requisitos

- Python 3.14 ou superior.
- Dependencias declaradas em `pyproject.toml`.
- Ambiente recomendado com `uv`.
- Prefect 3 para orquestracao do pipeline.
- GDAL/`osgeo` apenas para processamento raster (`.tif`/`.tiff`).

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

### GDAL Para Raster

O GDAL nao e necessario para processar apenas `.shp` e `.gpkg`. Ele passa a ser
obrigatorio quando a ingest tiver `.tif` ou `.tiff` em `path_shapefile_temp`.

No Windows, evite depender de `pip install -e ".[raster]"` como primeira opcao,
porque o `pip` pode tentar compilar GDAL localmente e exigir Microsoft C++ Build
Tools. Para raster, a instalacao recomendada e um ambiente conda-forge separado:

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" create -n prefect-gdal -c conda-forge python=3.14 gdal geopandas pandas numpy pyarrow pyproj shapely openpyxl prefect pyogrio -y
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m pip install -e .
```

Valide o GDAL no ambiente:

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -c "from osgeo import gdal; print(gdal.VersionInfo('--version'))"
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m unittest tests.test_raster_gdal_integration
```

Quando houver raster na fila, execute tambem o Prefect pelo ambiente
`prefect-gdal`. Nao use `uv run` nesse caso, pois ele executa o `.venv` padrao
do projeto; se esse `.venv` nao tiver `osgeo`, o processamento `.tif/.tiff`
falhara.

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python main.py
```

Atalho equivalente:

```powershell
.\scripts\run_pipeline_gdal.ps1 -CheckOnly
.\scripts\run_pipeline_gdal.ps1
```

## Como Usar

1. Atualize `input/st_Ingest_parameter.xlsx`.
2. Na aba `datas`, defina `status = treatment` para tratar bases ja disponiveis.
3. Preencha `path_shapefile_temp`, `theme_folder` e `theme`.
4. Confira se existe um perfil correspondente em `rules/`.
5. Execute o tratamento:

```powershell
uv run python main.py
```

O comando acima executa o flow Prefect `Data Treatment`, com uma task para
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

O processamento raster com GDAL esta documentado em
`docs/raster_pipeline.md`.

### Painel Local

No primeiro terminal, dentro da pasta do projeto, inicie o servidor local:

```powershell
cd C:\Temp\Repositorios\prefect
uv run python -m prefect server start --host 127.0.0.1 --port 4200
```

Deixe esse terminal aberto. Ele fica segurando o servidor do Prefect.

Abra no navegador:

```text
http://127.0.0.1:4200
```

Em outro terminal, entre novamente na pasta do projeto:

```powershell
cd C:\Temp\Repositorios\prefect
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

### Deployments E Agendamentos

Os deployments ficam centralizados em `scripts/serve.py`. O comando recebe o
nome operacional do deployment e registra no Prefect o flow, os parametros e,
quando aplicavel, a agenda.

```powershell
uv run python scripts/serve.py <deployment>
```

Exemplos disponiveis:

```powershell
uv run python scripts/serve.py ur-car-processing
uv run python scripts/serve.py estado
.\.venv\Scripts\python.exe scripts\serve.py auto-infracoes
uv run python scripts/serve.py data-download
uv run python scripts/serve.py data-publish
```

Cada deployment deve deixar explicito quais `theme_folders` roda. Quando o
deployment possui agenda, o horario e o fuso ficam definidos no proprio
`scripts/serve.py` e podem ser alterados pelo painel do Prefect.

Se os flows ou deployments forem deletados no painel do Prefect, o dashboard
ficara vazio. Para recriar um deployment e seus agendamentos, deixe o servidor
Prefect aberto e rode novamente o `scripts/serve.py` correspondente.

Para bases com varios `theme_folders`, cada agenda pode passar um filtro
especifico para o flow. Exemplo: um deployment pode agendar uma UF por dia
usando parametros como:

```json
{"theme_folders": ["ur_car_ac"]}
```

Os runs agendados podem ser renomeados automaticamente para o nome da base,
quando houver rotina administrativa configurada. O nome mostrado na lista de
runs pode aparecer primeiro como um nome aleatorio do Prefect e depois ser
atualizado.

Para aplicar renomeacao manualmente, quando necessario:

```powershell
uv run python scripts/prefect_admin.py rename-scheduled-runs
```

Rotinas administrativas especificas, como recriar uma agenda diaria de um
conjunto de bases, ficam em `scripts/prefect_admin.py`.

Exemplo:

```powershell
uv run python scripts/prefect_admin.py reschedule-ur-car-daily-17h
```

### Variables

Algumas configuracoes operacionais ficam em Prefect Variables, com fallback
local quando o servidor Prefect nao estiver disponivel. Para gravar os valores
padrao no Prefect:

```powershell
uv run python scripts/prefect_admin.py set-default-variables
```

Variables usadas:

```text
car_public_api_base
download_archive_base
download_extract_base
ur_car_sequence_start_date
ur_car_sequence_hour
ur_car_sequence_minute
ur_car_sequence_timezone
```

Esses valores tambem podem ser alterados pelo painel em `Variables`.

### Download de dados + tratamento

O download passa por um catalogo de datasets. Hoje o conector CAR usa a API
publica do SICAR diretamente em Python; outros projetos, como
municipios, estados e terras indigenas, entram como novos itens/conectores sem
alterar o flow principal.

Para subir o deployment de download:

```powershell
uv run python scripts/serve.py data-download
```

Esse comando cria o deployment `Download de Dados`. Sem parametros manuais, o
flow le a aba `datas` da planilha ingest e baixa apenas linhas com
flag `download` no `status`.

Bases marcadas com `download` que nao possuem conector/script registrado no
catalogo de downloads sao ignoradas com mensagem no log. Para essas bases, use
`status = treatment` quando o dado ja estiver disponivel para tratamento.

Quando a fonte retorna HTML, pagina de certificado/proxy, login, acesso negado
ou URL assinada expirada no lugar do ZIP, o conector CAR registra um diagnostico
no erro e remove a assinatura da URL antes de exibir no log.

Status oficiais na coluna `status`:

```text
download: baixa a base quando ha conector/script registrado.
treatment: copia temp para bronze, trata/padroniza/valida e salva silver.
publish: publica a ultima versao silver disponivel.
```

As flags podem ser combinadas com hifen, por exemplo:

```text
download-treatment
treatment-publish
download-treatment-publish
```

O flow aceita os principais parametros:

```text
source_root: base opcional da API/fonte do conector
force: baixa novamente mesmo se o ZIP ja existir
emit_download_event: quando true, emite o evento Prefect dataset.downloaded
theme_folders: filtro opcional para baixar apenas alguns theme_folders com flag download
```

Fluxo padrao:

```text
Data Download
  -> le linhas com flag download na ingest
  -> resolve o dataset no catalogo pelo theme_folder
  -> ignora bases sem conector/script registrado
  -> chama o conector de download das bases elegiveis
  -> salva/cacheia o ZIP em <temp>/<...>/<version>/_downloads/<dataset_key>/<theme_folder>
  -> extrai o arquivo em <temp>/<...>/<version>/raw
  -> emite dataset.downloaded
```

Para usar Prefect Automations em vez do encadeamento direto, configure
`process_after_download=false` no deployment de download e crie a Automation:

```powershell
uv run python scripts/prefect_admin.py create-download-automation
```

A Automation ouve o evento `dataset.downloaded` e executa o deployment de
tratamento. O evento carrega no payload `theme_folders` e
`source_path_overrides`, que sao os parametros necessarios para tratar
exatamente o arquivo baixado.

### Publicacao GeoServer / GeoNetwork

O projeto possui um flow separado para publicar arquivos da etapa `silver_data`
no GeoServer e no GeoNetwork:

```text
Data Publish/Publish GeoServer GeoNetwork
```

Esse flow recebe uma pasta silver e publica exatamente um conjunto formado por:

```text
<nome>.gpkg
<nome>.sld
md_<restante_do_nome>.xml
```

Se a pasta tiver mais de um arquivo publicavel (`.gpkg`, `.rst` ou `.tif`), o
flow nao publica nada e registra no log que existe mais de um conjunto na mesma
pasta. Nesse caso, separe os conjuntos em pastas diferentes ou publique uma
pasta por vez.

Exemplo de pasta valida para publicacao:

```text
pnt_pcd_enov_20260514.gpkg
pnt_pcd_enov_20260514.sld
md_pcd_enov_20260514.xml
```

Exemplo de pasta que sera recusada por conter dois conjuntos:

```text
pol_pcd_tema_20260514.gpkg
pol_pcd_tema_20260514.sld
md_pcd_tema_20260514.xml
pol_pcd_tema_recorte_20260514.gpkg
pol_pcd_tema_recorte_20260514.sld
md_pcd_tema_recorte_20260514.xml
```

Para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py data-publish
```

As credenciais nao devem ser gravadas no repositorio. Configure no terminal ou
em Prefect Variables/ambiente da infraestrutura:

```powershell
$env:PUBLISH_GEOSERVER_USERNAME="usuario"
$env:PUBLISH_GEOSERVER_PASSWORD="senha"
$env:PUBLISH_GEONETWORK_USERNAME="usuario"
$env:PUBLISH_GEONETWORK_PASSWORD="senha"
```

Quando o deployment estiver sendo servido em outro terminal, tambem e possivel
passar as credenciais nos parametros do run. Isso evita prompt interativo, que
nao funciona dentro de task Prefect.

Para testar sem publicar de verdade, use `dry_run=true`:

```powershell
'{"folder":"<silver-folder>","environment":"qas","workspace":"gold","dry_run":true}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Publish/Publish GeoServer GeoNetwork" --params -
```

Para publicar de verdade, use `dry_run=false` ou omita o parametro:

```powershell
'{"folder":"<silver-folder>","environment":"qas","workspace":"gold"}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Publish/Publish GeoServer GeoNetwork" --params -
```

Exemplo passando credenciais por parametro:

```powershell
'{"folder":"<silver-folder>","environment":"qas","workspace":"gold","dry_run":false,"geoserver_username":"admin","geoserver_password":"<senha>","geonetwork_username":"admin","geonetwork_password":"<senha>"}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Publish/Publish GeoServer GeoNetwork" --params -
```

O flow publica o arquivo de dados no GeoServer, cria ou atualiza o SLD, associa
o estilo a camada, le os tipos dos atributos publicados e importa o XML no
GeoNetwork com o link do dicionario de dados.

### Execucao Por Etapas

Quando a ingest usar combinacoes como `download-treatment-publish`, execute os
flows na ordem operacional: `Data Download`, `Data Treatment` e `Data Publish`.
Cada flow seleciona apenas as linhas que contem a sua flag.

### Execucao Manual Pelo Terminal

Para executar uma base especifica por um deployment parametrizado, envie
`theme_folders`:

```powershell
'{"theme_folders":["<theme_folder>"]}' | uv run python -m prefect deployment run "Data Treatment/<deployment>" --params -
```

Exemplo:

```powershell
'{"theme_folders":["ur_car_pi"]}' | uv run python -m prefect deployment run "Data Treatment/CAR - Uso Restrito" --params -
```

Para executar uma lista de bases, informe todos os `theme_folders` desejados:

```powershell
'{"theme_folders":["<theme_folder_1>","<theme_folder_2>"]}' | uv run python -m prefect deployment run "Data Treatment/<deployment>" --params -
```

Deployments sem parametros manuais tambem podem ser disparados diretamente:

```powershell
uv run python -m prefect deployment run "Data Treatment/Autos de Infracao"
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
2. Abra o deployment desejado.
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

Cada perfil em `rules/` deve conter cinco arquivos obrigatorios e,
opcionalmente, `style.json` quando a base precisar gerar estilo SLD:

```text
rules/<projeto>/<perfil>/
|-- profile.json
|-- input_schema.json
|-- domains.json
|-- relations.json
|-- pipeline.json
`-- style.json
```

Exemplo:

```text
theme_folder = app_car_es
perfil esperado = rules/car_area_preservacao_permanente/app_car_es/
```

Associacoes principais:

- `app_car_*` usa `rules/car_area_preservacao_permanente/`.
- `rl_car_*` usa `rules/car_reserva_legal/`.
- `sa_car_*` usa `rules/car_servidao_administrativa/`.
- `ur_car_*` usa `rules/car_uso_restrito/`.
- `estado` usa `rules/estado/`.
- `auth_supn` usa `rules/autorizacao_para_supressao_vegetal/`.
- `autos_infracao` usa `rules/autos_infracao/autos_infracao/`.

`theme_folder` e `project_name` tem papeis diferentes. `theme_folder` continua
sendo a chave operacional recebida da ingest e usada em caminhos/nome de
saida, enquanto `project_name` e a familia interna de regras. Nomes antigos de
projeto (`app_car`, `reserva_legal_car`, `sa_car`, `ur_car`) sao aceitos apenas
como aliases de compatibilidade e devem apontar para os projetos `car_*`.

Use `rules/_template/` como base para novos perfis. O formato completo esta em
`readme/rules.md`.

Antes de criar ou alterar regras de uma base, registre a especificacao em
`docs/sdd/specs/`. O guia do fluxo Spec-Driven Development fica em
`docs/sdd/README.md`, e o template para novas bases fica em
`docs/sdd/spec-template.md`.

No `pipeline.json`, o perfil explicita tudo que roda de forma configuravel:

- `auto_functions`: validacoes ou transformacoes por atributo.
- `postprocess_functions`: etapas que alteram o GeoDataFrame final, como `enforce_car_state_bounds` ou `enrich_with_municipality_intersection`.
- `output_adjustments`: ajustes aplicados somente ao arquivo de dados persistido.

O `style.json` concentra configuracoes de estilo, como `sld`. O `pipeline.json`
nao deve conter configuracao visual.

As chaves permitidas dos perfis ficam centralizadas em
`core/rules/contracts.py`; ao adicionar uma nova opcao operacional, atualize o
contrato, a validacao e a documentacao do perfil.

Quando configurado, `output_adjustments.relocate_outside_brazil_bounds_to_centroid`
mantem todos os registros na saida de dados, mas reposiciona geometrias fora
do limite Brasil / zona costeira para um ponto unico dentro do limite
brasileiro.

O `input_schema.json` define as colunas esperadas na entrada e seus tipos
(`string`, `integer`, `number`, `date`, etc.). A validacao estrutural usa esse
arquivo e ignora campos gerados pelo tratamento, como `acm_*`, `fid` e
`geometry`.

## Convencoes de Colunas

- Colunas originais sao preservadas como `sdb_*`.
- Colunas tratadas, normalizadas ou derivadas sao gravadas como `acm_*`.
- Funcoes genericas do `core` nao devem sobrescrever valores `sdb_*`.
- Marcacoes tecnicas internas nao devem aparecer no GeoPackage final.
- Campos de data seguem o `input_schema.json`: se a coluna ja vier como data,
  permanece em `sdb_*`; se vier como texto e o schema esperar `date`, o valor
  original fica em `sdb_*` e a data normalizada e gravada em `acm_*`.

## Geometria

O pipeline:

- achata geometrias para 2D;
- repara geometrias invalidas quando possivel;
- valida geometrias OGC quando habilitado;
- calcula area, perimetro, longitude e latitude;
- usa `EPSG:4326` para saida e `EPSG:5880` para metricas;
- aplica validacao regional de bounding box para bases
  `car_area_preservacao_permanente` e `car_reserva_legal`.

## Saidas

O arquivo principal de saida e sempre `.gpkg`.

Tambem podem ser gerados:

- log contextual `.txt`;
- relatorio de inconsistencias de dominio;
- relatorio de duplicados por atributos;
- relatorio de duplicados geometricos;
- relatorio de geometrias invalidas OGC;
- consolidado por grupo, quando `ENABLE_GROUP_CONSOLIDATION = True`.
- metadados XML junto dos arquivos em `bronze_data` e `silver_data`.
- arquivos SLD junto dos GeoPackages na etapa `silver_data`.

O fluxo de persistencia segue a ordem:

1. Le arquivo no `temp`.
2. Copia o dado bruto para `bronze_data` sem alterar atributos, geometria ou
   nome do arquivo bruto.
3. Cria o XML do bronze.
4. Salva o XML do bronze.
5. Executa os tratamentos.
6. Salva o `.gpkg` tratado no `silver_data`.
7. Cria e salva o XML do silver.
8. Cria e salva o SLD do silver, quando houver configuracao em `style.json`.

O XML de metadados usa prefixo `md_`, preservando o restante do nome logico da
saida. Exemplo: `pnt_pcd_enov_20260514.gpkg` gera
`md_pcd_enov_20260514.xml`.

O SLD e gerado somente para arquivos persistidos em `silver_data`. A etapa
`bronze_data` preserva apenas o dado bruto e o XML de metadados.

Na etapa de persistencia, o log tambem lista as verificacoes obrigatorias de
qualidade executadas: `check_attribute_duplicates`,
`check_geometric_duplicates` e `check_ogc_invalid_geometries`.
Por padrao, essas verificacoes aparecem apenas no log. Para tambem exportar
arquivos de apoio, habilite `EXPORT_OUTPUT_QUALITY_REPORT_FILES = True`.

## Versionamento Temp/Bronze/Silver

O modulo `core.versioning` monta os caminhos padronizados das camadas
`temp`, `bronze_data` e `silver_data` a partir da variavel de ambiente:

```text
DATA_LAKE_BASE
```

Estrutura:

```text
<base>\<etapa>\<access_constraints>\<category_acronym>\<theme_folder>\<citation>\<date>\<version>
```

`date` e convertido para `YYYYMMDD`. A versao nao vem da ingest: ela e
calculada pela existencia de arquivos em `bronze_data`, iniciando em `00`.

## Configuracao

As constantes principais ficam em `settings.py`, incluindo:

- `DATA_LAKE_BASE`
- `DATA_LAKE_TEMP_STAGE`
- `DATA_LAKE_BRONZE_STAGE`
- `DATA_LAKE_SILVER_STAGE`
- `INGEST_WORKBOOK_PATH`
- `INGEST_SHEET_NAME`
- `DICTIONARIES_SHEET_NAME`
- `INGEST_READY_STATUS`
- `INGEST_DOWNLOAD_STATUS`
- `INGEST_REPROCESSING_STATUS`
- `INGEST_PROCESSING_STATUSES`
- `OUTPUT_BASE`
- `RULES_BASE`
- `BATCH_SIZE`
- `CRS_WGS84`
- `CRS_EQUAL_AREA`
- `ENABLE_GROUP_CONSOLIDATION`
- `EXPORT_OUTPUT_QUALITY_REPORT_FILES`
- `KEEP_INDIVIDUAL_OUTPUTS_WHEN_GROUPING`
- `USE_ARROW_IO`
- `INTERACTIVE_ATTRIBUTE_REVIEW`

Os caminhos dependentes do ambiente devem ser informados externamente:

- `DATA_LAKE_BASE`: raiz das camadas `temp`, `bronze_data` e `silver_data`.
- `MUNICIPALITIES_BASE_PATH`: arquivo de referencia de municipios.
- `BRAZIL_BBOX_PATH`: arquivo opcional com o limite Brasil / zona costeira.

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
