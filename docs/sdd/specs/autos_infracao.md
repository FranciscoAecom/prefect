# Spec: autos_infracao/autos_infracao

Status: Implementado
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de autos de infracao ambiental, preservando os campos de
origem como `sdb_*`, aplicando validacoes de dominio e data, enriquecendo os
pontos com municipio/UF por intersecao espacial e gerando somente a saida final
completa `pnt_pcd_enov_20260514.gpkg`.

## Entrada

- Theme folder: `autos_infracao`
- Projeto: `autos_infracao`
- Status esperado na ingest: `waiting update`
- Formato esperado: camada vetorial de pontos
- Geometria esperada: ponto
- Base de referencia usada para montar dominios: `C:\Temp\Repositórios\explorer\teste.xlsx`
- Atributos considerados em `domains.json`: apenas campos marcados em verde na planilha de referencia.

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Autos de infracao ambiental`
- `theme_prefixes`: `("enov",)`
- `output_name_template`: `pnt_pcd_enov_{date_yyyymmdd}`
- `reference_date`: `20260514`

## Regras Do Perfil

- `rules/autos_infracao/autos_infracao/profile.json`
- `rules/autos_infracao/autos_infracao/input_schema.json`
- `rules/autos_infracao/autos_infracao/domains.json`
- `rules/autos_infracao/autos_infracao/relations.json`
- `rules/autos_infracao/autos_infracao/treatment.json`
- `rules/autos_infracao/autos_infracao/style.json`

A validacao estrutural de entrada deve usar
`rules/autos_infracao/autos_infracao/input_schema.json`, ignorando campos que
entram depois do tratamento (`acm_*`), `fid` e `geometry`.

## Schema De Entrada

Campos obrigatorios configurados:

- 67 campos definidos em `rules/autos_infracao/autos_infracao/input_schema.json`

Tipos e observacoes:

- `sdb_num_longit`, `sdb_num_latitu`, `sdb_val_auto_i` e `sdb_qt_area` devem ser numericos.
- Campos de identificador e contagem configurados como `integer` devem ser
  coercidos conforme `input_schema.json`.
- Os campos de data configurados devem seguir a secao `Datas`.
- Os demais campos do schema devem ser tratados como texto.

## Dominios

Fonte:

- `rules/autos_infracao/autos_infracao/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_des_status` | 4 | Status do auto |
| `sdb_ds_sit_aut` | 2 | Situacao do auto |
| `sdb_sit_cancel` | 2 | Situacao de cancelamento |
| `sdb_tipo_auto` | 3 | Tipo do auto |
| `sdb_patrimonio` | 2 | Classificacao de patrimonio |
| `sdb_gravidade_` | 3 | Gravidade |
| `sdb_cd_nivel_g` | 5 | Nivel de gravidade |
| `sdb_motivacao_` | 2 | Motivacao |
| `sdb_efeito_mei` | 5 | Efeito no meio ambiente |
| `sdb_efeito_sau` | 5 | Efeito na saude |
| `sdb_passivel_r` | 3 | Passivel de reparacao |
| `sdb_forma_entr` | 5 | Forma de entrega |
| `sdb_tipo_infra` | 12 | Tipo de infracao |
| `sdb_des_receit` | 13 | Receita |
| `sdb_infracao_a` | 7 | Infracao associada |
| `sdb_tipo_acao` | 5 | Tipo de acao |
| `sdb_tp_ult_alt` | 5 | Tipo da ultima alteracao |
| `sdb_tp_origem_` | 2 | Tipo de origem |

Campos presentes no schema sem dominio:

- demais campos definidos em `input_schema.json`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- nenhuma

Regra de aplicacao:

- nao aplicavel

## Datas

Os campos abaixo devem ser tratados como data por `validate_date_fields`:

- `sdb_dat_hora_a`
- `sdb_dat_cienci`
- `sdb_dt_fato_in`
- `sdb_dt_inicio_`
- `sdb_dt_fim_ato`
- `sdb_dt_lancame`
- `sdb_dt_ult_alt`
- `sdb_dt_ult_al0`
- `sdb_dt_atualiz`

Regra de saida para datas:

- se o campo original ja vier tipado como data, manter somente o `sdb_*`;
- se o campo vier como texto, preservar o `sdb_*` original e gerar o `acm_*`
  correspondente normalizado como `DATE`, sem horario.

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

- `validate_shapefile_attribute`
- `validate_date_fields`

Postprocess configurado:

- `enrich_with_municipality_intersection`


Ajuste de saida configurado:

- `relocate_outside_brazil_bounds_to_centroid`

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

Essas verificacoes devem aparecer no log, mas nao devem gerar arquivos fisicos
de relatorio enquanto `EXPORT_OUTPUT_QUALITY_REPORT_FILES = False`.

## Intersecao Municipal

A base deve fazer intersecao com municipios usando:

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

## Limite Brasil / Zona Costeira

A saida principal deve usar o limite abaixo para identificar pontos fora do
Brasil / zona costeira e reposiciona-los para um centroide unico dentro do
limite brasileiro:

```text
L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\others\bouding_box\brasil\pol_br_zona_costeira.gpkg
```

Campos derivados para controle do reposicionamento:

- `acm_long_centroide_brasil`
- `acm_lat_centroide_brasil`

Esses campos devem ser preenchidos somente para registros cuja geometria
original esta fora do limite Brasil / zona costeira e foi reposicionada para o
centroide unico do limite brasileiro. Para registros ja contidos no limite, os
dois campos devem permanecer nulos.

Quando um registro for reposicionado:

- a geometria final deve ser movida para o centroide unico do limite brasileiro;
- `acm_long` e `acm_lat`, quando existirem, devem refletir a geometria final
  reposicionada;
- `acm_long_centroide_brasil` e `acm_lat_centroide_brasil` devem registrar as
  coordenadas do centroide aplicado, arredondadas para 6 casas decimais.

## Estilo SLD

Arquivo:

```text
rules/autos_infracao/autos_infracao/style.json
```

Regra principal:

- `pnt_pcd_enov_20260514`: ponto circular, preenchimento `#ef8e03`,
  contorno `#232323`, largura `0.5`, tamanho `7`.

O SLD deve ser gerado somente no `silver_data`; o bronze nao gera SLD.

## Saidas Esperadas

Arquivo principal:

```text
output\autos_infracao\pnt_pcd_enov_20260514.gpkg
```

XML esperado no bronze e no silver:

```text
md_pcd_enov_20260514.xml
```

SLD esperado somente no silver:

```text
sld_pcd_enov_20260514.sld
```

O arquivo principal deve conter todos os pontos tratados. Pontos fora do limite
Brasil / zona costeira devem ser mantidos no arquivo principal, mas com a
geometria reposicionada para um ponto unico dentro do limite brasileiro. Quando
existirem `acm_long` e `acm_lat`, esses campos devem refletir a nova geometria.
Os campos `acm_long_centroide_brasil` e `acm_lat_centroide_brasil` devem
permitir identificar quais registros tiveram a geometria substituida pelo
centroide brasileiro.

O fluxo deve seguir esta ordem no log:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.
8. Criar e salvar o SLD do silver.

O bronze nao deve gerar SLD. Ele deve conter somente o dado bruto e o XML de
metadados.

## Publicacao

Esta base gera um unico conjunto publicavel:

```text
pnt_pcd_enov_20260514.gpkg
sld_pcd_enov_20260514.sld
md_pcd_enov_20260514.xml
```

## Prefect

Deployment:

```text
Data Treatment/Treatment Agendado pela Ingest
```

Comando para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py scheduled-treatment
```

Comando para disparar pelo Prefect:

```powershell
'{"theme_folders":["autos_infracao"]}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/Treatment Agendado pela Ingest" --params -
```

Parametros fixos do deployment:

```json
{"theme_folders": ["autos_infracao"]}
```

Agenda:

- nao configurada

## Geracao De Rules

Comando ou processo para regenerar rules:

```powershell
nao aplicavel
```

Arquivos atualizados pelo processo:

- nao aplicavel

## Download

- Status na ingest para baixar: nao aplicavel no momento
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao: como nao existe conector de download para `autos_infracao`, a base deve usar `status = treatment` quando o dado ja estiver disponivel para tratamento.

## Versionamento

- `treatment`: trata/padroniza/valida a base e pode criar nova versao quando houver novo bruto.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [x] A base roda isolada, sem disparar todas as bases.
- [x] O deployment Prefect existe para acompanhamento em `Runs`.
- [x] O arquivo principal `.gpkg` e gerado.
- [x] A saida principal mantem registros fora do limite Brasil / zona costeira reposicionados para um ponto unico dentro do Brasil.
- [x] Registros reposicionados preenchem `acm_long_centroide_brasil` e `acm_lat_centroide_brasil`.
- [x] Registros dentro do limite Brasil / zona costeira mantem `acm_long_centroide_brasil` e `acm_lat_centroide_brasil` nulos.
- [x] Quando houver reposicionamento, `acm_long` e `acm_lat` refletem a geometria final.
- [x] O arquivo principal passa pelas funcoes obrigatorias.
- [x] `clean_whitespace` aparece no log de funcoes obrigatorias.
- [x] A intersecao municipal cria `acm_cod_munici`, `acm_municipio` e `acm_uf`.
- [x] Registros sem municipio recebem mensagem de fora do limite territorial.
- [x] Os campos de data passam por `validate_date_fields`.
- [x] Os campos de data saem como `DATE` no GeoPackage.
- [x] A validacao estrutural usa `input_schema.json`.
- [x] O XML do bronze e do silver usa prefixo `md_`.
- [x] O bronze preserva o bruto sem alterar dados nem nome do arquivo.
- [x] O SLD e gerado somente no silver.
- [x] As verificacoes obrigatorias de qualidade aparecem no log.
- [x] Relatorios fisicos de qualidade ficam desabilitados por flag.
- [x] Testes automatizados passam.

## Validacao

Comando executado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Resultado registrado em 2026-05-25:

```text
Ran 158 tests
OK
```

