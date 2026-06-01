# Spec: degradacao/degradacao

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-06-01

## Objetivo

Processar a base de degradacao da Amazonia do DETER, preservando os campos de
origem como `sdb_*`, validando dominios configurados, tratando a data de
visualizacao e enriquecendo os poligonos com municipio/UF por intersecao
espacial.

## Entrada

- Theme folder: `degradacao`
- Projeto: `degradacao`
- Pasta fisica das rules: `rules/degradacao_amazonia/degradacao`
- Status esperado na ingest para tratamento: `Waiting Update` ou `Reprocessing`
- Status esperado na ingest para download: nao aplicavel no momento
- Registro(s) de referencia na ingest: ainda nao cadastrado
- Formato esperado: shapefile
- Geometria esperada: poligono ou multipoligono
- Fonte declarada: DETER Amazonia
- Caminho temporario usado para montar as rules:
  `L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\temp\degradacao\deter-amz-public-2026mai20\deter-amz-deter-public.shp`
- Sistema de referencia observado: `EPSG:4674`
- Base de referencia usada para dominios:
  `C:\Temp\Repositórios\explorer\teste.xlsx`
- Base de referencia usada para relacoes: nao aplicavel

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Degradacao da Amazonia`
- `theme_prefixes`: `("dfaab",)`
- `output_name_template`: `pol_dfaab_imb_{date_yyyymmdd}`
- `reference_date`: `None`

Como `reference_date` nao esta fixada, `{date_yyyymmdd}` deve ser resolvida na
execucao.

## Regras Do Perfil

- `rules/degradacao_amazonia/degradacao/profile.json`
- `rules/degradacao_amazonia/degradacao/input_schema.json`
- `rules/degradacao_amazonia/degradacao/domains.json`
- `rules/degradacao_amazonia/degradacao/relations.json`
- `rules/degradacao_amazonia/degradacao/pipeline.json`
- `rules/degradacao_amazonia/degradacao/style.json`: nao configurado

A validacao estrutural de entrada deve usar
`rules/degradacao_amazonia/degradacao/input_schema.json`, permitindo colunas
extras conforme o perfil.

## Schema De Entrada

Campos obrigatorios configurados:

- `sdb_fid`
- `sdb_classname`
- `sdb_quadrant`
- `sdb_path_row`
- `sdb_view_date`
- `sdb_sensor`
- `sdb_satellite`
- `sdb_areauckm`
- `sdb_uc`
- `sdb_areamunkm`
- `sdb_municipali`
- `sdb_geocodibge`
- `sdb_uf`

Tipos e observacoes:

- `sdb_fid` deve ser tratado como texto.
- `sdb_areauckm` e `sdb_areamunkm` devem ser numericos.
- `sdb_view_date` deve ser tratado como data.
- `sdb_quadrant` e `sdb_uc` aceitam valores nulos.
- Os demais campos configurados nao aceitam valores nulos.

## Dominios

Fonte:

- `rules/degradacao_amazonia/degradacao/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_classname` | 8 | Classe do alerta |
| `sdb_quadrant` | 4 | Quadrante |
| `sdb_sensor` | 3 | Sensor |
| `sdb_satellite` | 4 | Satelite |
| `sdb_uc` | 107 | Unidade de conservacao |
| `sdb_uf` | 9 | Sigla da unidade da federacao |

Campos presentes no schema sem dominio:

- `sdb_fid`
- `sdb_path_row`
- `sdb_view_date`
- `sdb_areauckm`
- `sdb_areamunkm`
- `sdb_municipali`
- `sdb_geocodibge`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- nenhuma

Regra de aplicacao:

- nao aplicavel

## Datas

Campos tratados por `validate_date_fields`:

- `sdb_view_date`

Regra de saida para datas:

- se o campo original ja vier tipado como data, manter somente o `sdb_*`;
- se o campo vier como texto, preservar o `sdb_*` original e gerar o `acm_*`
  correspondente normalizado como `DATE`, sem horario;
- datas normalizadas devem sair como `DATE`.

## Funcoes Do Pipeline

Obrigatorias para todas as bases:

- `clean_whitespace`
- `reproject_shapefile`
- `force_geometry_2d`
- `add_sequential_id`
- `calculate_area_hectares`
- `calculate_perimeter_km`
- `add_centroid_coordinates`

Opcionais por atributo:

- `sdb_classname`: `validate_shapefile_attribute`
- `sdb_quadrant`: `validate_shapefile_attribute`
- `sdb_view_date`: `validate_date_fields`
- `sdb_sensor`: `validate_shapefile_attribute`
- `sdb_satellite`: `validate_shapefile_attribute`
- `sdb_uc`: `validate_shapefile_attribute`
- `sdb_uf`: `validate_shapefile_attribute`

Postprocess configurado:

- `enrich_with_municipality_intersection`

Saida principal configurada:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

Essas verificacoes devem aparecer no log. A geracao fisica de relatorios segue
o valor de `EXPORT_OUTPUT_QUALITY_REPORT_FILES`.

## Intersecao Municipal

A base deve fazer intersecao com municipios. A resolucao da base municipal
segue esta ordem:

1. caminho informado explicitamente;
2. Prefect Variable `municipios_base_path`;
3. ultima base `municipios` com status `Complete` na ingest;
4. caminho padrao:

```text
L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\silver_data\restricted\loc\municipios\IBGE\20240101\00\pol_loc_mun_20230101.gpkg
```

Campos derivados esperados:

- `acm_cod_munici`
- `acm_municipio`
- `acm_uf`

Quando a intersecao nao encontrar municipio, preencher os campos derivados com:

```text
Fora do limite territorial brasileiro / zona costeira
```

## Estilo SLD

- Arquivo: nao aplicavel
- Campo de categorizacao: nao aplicavel
- Regra principal: nao aplicavel

## Saidas Esperadas

Arquivo principal:

```text
output\degradacao\pol_dfaab_imb_{date_yyyymmdd}.gpkg
```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text
md_dfaab_imb_{date_yyyymmdd}.xml
```

SLD esperado somente no silver:

```text
nao aplicavel
```

Campos `acm_*` obrigatorios:

- `acm_id`
- `acm_a_ha`
- `acm_prm_km`
- `acm_long`
- `acm_lat`
- `acm_cod_munici`
- `acm_municipio`
- `acm_uf`

O fluxo deve seguir esta ordem no log:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.
8. Criar e salvar o SLD do silver, quando houver `style.json`.

## Publicacao

Conjunto publicavel esperado:

```text
pol_dfaab_imb_{date_yyyymmdd}.gpkg
md_dfaab_imb_{date_yyyymmdd}.xml
```

Observacoes:

- Como nao existe `style.json`, nao ha SLD para publicacao.

## Prefect

Deployment:

```text
Data Pipeline
```

Comando para servir o deployment:

```powershell
nao configurado especificamente para degradacao
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Pipeline/<deployment>" --param theme_folders='["degradacao"]'
```

Parametros fixos do deployment:

```json
{"theme_folders": ["degradacao"]}
```

Agenda:

- nao configurada

## Geracao De Rules

Comando ou processo usado como apoio para montar os dominios:

```text
C:\Temp\Repositórios\explorer
```

Arquivo de referencia gerado:

- `C:\Temp\Repositórios\explorer\teste.xlsx`

## Download

- Status na ingest para baixar: nao aplicavel no momento
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao para bases sem download automatico: usar `status = Waiting Update`
  quando o dado ja estiver disponivel para tratamento.

## Versionamento

- `Waiting Update`: pode criar nova versao quando houver novo bruto.
- `Reprocessing`: deve reutilizar a ultima versao existente e nao criar nova versao.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] A base roda isolada, sem disparar todas as bases.
- [ ] O arquivo principal `.gpkg` e gerado com o nome esperado.
- [ ] O arquivo principal abre no QGIS.
- [x] A validacao estrutural usa `input_schema.json`.
- [x] `sdb_fid` e tratado como texto.
- [x] Os dominios cobrem os valores da planilha de referencia.
- [x] `sdb_view_date` passa por `validate_date_fields`.
- [ ] A intersecao municipal cria `acm_cod_munici`, `acm_municipio` e `acm_uf`.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] As funcoes opcionais configuradas aparecem no log.
- [ ] As verificacoes obrigatorias de qualidade aparecem no log.
- [x] Testes automatizados relevantes passam.

## Validacao

Comando executado:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_rule_profiles_integration tests.test_municipality_intersection
```

Resultado registrado em 2026-06-01:

```text
Ran 12 tests
OK
```
