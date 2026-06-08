# Data Treatment

Tratamento de validacao, transformacao e padronizacao de arquivos geoespaciais
em lote, orientado pela planilha de ingestao `input/st_Ingest_parameter.xlsx`.

O projeto processa bases `.shp` e `.gpkg`, valida schemas e dominios,
normaliza atributos, repara geometrias, calcula metricas espaciais e grava
saidas finais em GeoPackage.

## Objetivo

- Ler registros de tratamento a partir da aba `datas` da planilha de ingestao.
- Processar arquivos geoespaciais por perfil de regras em `rules/`.
- Validar estrutura tabular contra o `input_schema.json` do perfil de regras.
- Preservar atributos originais com prefixo `sdb_*`.
- Gerar campos tratados e padronizados com prefixo `acm_*`.
- Produzir saidas em `output/<theme_folder>/` com logs e relatorios auxiliares.

## Entradas Suportadas

- Arquivos `.shp`.
- Arquivos `.gpkg`.
- Pastas contendo `.shp` e `.gpkg`, inclusive em subpastas.

Arquivos `.zip` nao sao processados diretamente.

Uma linha entra no tratamento quando:

- `status` contem `treatment` para tratamento;
- `status` contem `download` para download automatico;
- `status` contem `publish` para publicacao;
- `path_shapefile_temp` aponta para um arquivo ou pasta suportada;
- `theme_folder` encontra um perfil correspondente em `rules/`.

## Estrutura

```text
geodata-workflow/
|-- main.py
|-- settings.py
|-- input/
|   `-- st_Ingest_parameter.xlsx
|-- output/
|-- core/
|   |-- downloads/
|   |-- ingest/
|   |-- metadata/
|   |-- publish/
|   |-- rules/
|   |-- spatial/
|   |-- treatment/
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

- `main.py`: ponto de entrada do tratamento por planilha ingest.
- `settings.py`: configuracoes centrais do tratamento.
- `core/`: motor de ingestao, validacao, tratamento, regras e escrita.
- `core/downloads/`: catalogo, conectores e utilitarios de download.
- `core/treatment/`: servico, execucao e processador vetorial do tratamento.
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
- Prefect 3 para orquestracao do tratamento.

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
2. Na aba `datas`, defina `status = treatment` para tratar bases ja disponiveis.
3. Preencha `path_shapefile_temp`, `theme_folder` e `theme`.
4. Confira se existe um perfil correspondente em `rules/`.
5. Execute o tratamento:

```powershell
uv run python main.py
```

O comando acima executa o flow Prefect `Data Treatment`, com uma task para
preparar o tratamento e uma task para cada registro processado.

Ou, usando o Python instalado diretamente:

```powershell
py -3.14 main.py
```

As saidas ficam em:

```text
output/<theme_folder>/
```

## Prefect

O projeto opera com tres flows oficiais:

```text
Data Download
Data Treatment
Data Publish
```

Use o script operacional para iniciar o Prefect local, recriar deployments e,
quando necessario, resetar o banco local:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting
.\scripts\start_prefect_local.ps1 -StopExisting -ResetDatabase
```

O guia completo de operacao, publicacao, reset do banco e comandos de suporte
fica em `docs/production.md`.

### Comandos Uteis

Entrar na pasta do projeto e apontar o terminal para a API local do Prefect:

```powershell
cd "C:\Temp\Repositórios\prefect"
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
```

Confirmar que o servidor Prefect esta ativo:

```powershell
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
.\.venv\Scripts\python.exe -m prefect flow ls
```

Executar o tratamento diretamente pelo `main.py`, lendo a planilha ingest:

```powershell
uv run python main.py
```

Executar o flow de download pela planilha ingest. Use este comando quando
existirem linhas com `status` contendo `download`, como `download`,
`download-treatment` ou `download-treatment-publish`:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Download/Download de Dados"
```

Observacao: a flag `download` so baixa bases com conector/script registrado no
catalogo de downloads. Para tratar arquivo ja existente em `path_shapefile_temp`,
use `treatment` ou `treatment-publish`.

Quando o status for `download-treatment-publish`, o encadeamento esperado e:

```text
Data Download -> Data Treatment -> Data Publish
```

Esse encadeamento depende das automacoes criadas pelo script
`start_prefect_local.ps1`: `dataset.downloaded -> treatment` e
`dataset.treatment.completed -> publish`.

Executar uma base especifica pelo deployment de tratamento:

```powershell
'{"theme_folders":["ur_car_pi"]}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/Treatment Agendado pela Ingest" --params -
```

Reiniciar o Prefect local de forma limpa, mantendo o banco:

```powershell
cd "C:\Temp\Repositórios\prefect"
.\scripts\start_prefect_local.ps1 -StopExisting
```

Apagar o banco local do Prefect e recriar tudo do zero:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting -ResetDatabase
```

Depois de alterar ou inserir linhas `schedule YYYY-MM-DD HH:MM` na planilha
ingest, recrie os deployments para o Prefect carregar os novos agendamentos:
Após rodar o comando abaixo, não feche o terminal, para que os agendamentos
entrem em execução no devido momento.

```powershell
cd "C:\Temp\Repositórios\prefect"
.\scripts\start_prefect_local.ps1 -StopExisting
```

O agendamento aparece no deployment em `Schedules`. Ele pode nao aparecer ainda
na lista de flow runs agendados quando a data estiver muito distante, pois o
Prefect materializa runs futuros dentro de uma janela propria do scheduler.

Para apagar todos os agendamentos do deployment de tratamento:

```powershell
cd "C:\Temp\Repositórios\prefect"
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
.\.venv\Scripts\python.exe -m prefect deployment schedule clear "Data Treatment/Treatment Agendado pela Ingest" -y
```

Para listar os agendamentos carregados no deployment:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment schedule ls "Data Treatment/Treatment Agendado pela Ingest"
```

Para recriar as automacoes padrao manualmente:

```powershell
.\.venv\Scripts\python.exe scripts\prefect_admin.py create-download-automation
.\.venv\Scripts\python.exe scripts\prefect_admin.py create-treatment-publish-automation
```

Configurar credenciais de publicacao antes de iniciar o Prefect local:

```powershell
cd "C:\Temp\Repositórios\prefect"

$env:PUBLISH_GEOSERVER_USERNAME="admin"
$env:PUBLISH_GEOSERVER_PASSWORD="<sua_senha>"

$env:PUBLISH_GEONETWORK_USERNAME="admin"
$env:PUBLISH_GEONETWORK_PASSWORD="<sua_senha>"

.\scripts\start_prefect_local.ps1 -StopExisting
```

Nao grave senhas reais no repositorio. Use o placeholder acima na documentacao
e informe a senha real apenas no terminal/ambiente de execucao.

Para recriar os agendamentos com banco zerado:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting -ResetDatabase
```

## Regras Modulares

Cada perfil em `rules/` deve conter cinco arquivos obrigatorios e,
opcionalmente, `style.json` quando a base precisar gerar estilo SLD:

```text
rules/<projeto>/<perfil>/
|-- profile.json
|-- input_schema.json
|-- domains.json
|-- relations.json
|-- treatment.json
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

No `treatment.json`, o perfil explicita os tratamentos configuraveis da base.
Esse arquivo e contrato dos perfis de regras, nao um flow do Prefect. Os flows
Prefect continuam sendo `download`, `treatment` e `publish`.

- `auto_functions`: validacoes ou transformacoes por atributo.
- `postprocess_functions`: etapas que alteram o GeoDataFrame final, como `enforce_car_state_bounds` ou `enrich_with_municipality_intersection`.
- `output_adjustments`: ajustes aplicados somente ao arquivo de dados persistido.
- `quality_outputs`: liga/desliga verificacoes e relatorios de qualidade.

O `style.json` concentra configuracoes de estilo, como `sld`. O `treatment.json`
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

O tratamento:

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
- `INGEST_DOWNLOAD_STATUS`
- `INGEST_TREATMENT_STATUS`
- `INGEST_PUBLISH_STATUS`
- `INGEST_TREATMENT_STATUSES`
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





