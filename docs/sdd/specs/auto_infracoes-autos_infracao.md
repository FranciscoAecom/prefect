# Spec: auto_infracoes/autos_infracao

Status: Implementado
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de autos de infracao ambiental, preservando os campos de
origem como `sdb_*`, aplicando validacoes de dominio e data, enriquecendo os
pontos com municipio/UF por intersecao espacial e gerando uma saida secundaria
com os pontos dentro do limite Brasil / zona costeira.

## Entrada

- Theme folder: `autos_infracao`
- Projeto: `auto_infracoes`
- Status esperado na ingest: `waiting update`
- Formato esperado: camada vetorial de pontos
- Geometria esperada: ponto
- Base de referencia usada para montar dominios: `C:\Temp\Repositórios\explorer\teste.xlsx`
- Atributos considerados em `domains.json`: apenas campos marcados em verde na planilha de referencia.

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Autos de infracao ambiental`
- `theme_prefixes`: `("autos_infracao",)`
- `output_name_template`: `pnt_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260514`

## Regras Do Perfil

- `rules/auto_infracoes/autos_infracao/profile.json`
- `rules/auto_infracoes/autos_infracao/input_schema.json`
- `rules/auto_infracoes/autos_infracao/domains.json`
- `rules/auto_infracoes/autos_infracao/relations.json`
- `rules/auto_infracoes/autos_infracao/pipeline.json`

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

Na saida GeoPackage, os campos derivados dessas regras devem ser gravados como
`DATE`, sem horario.

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

Saidas secundarias configuradas:

- `brazil_bbox`

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

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

A saida secundaria `brazil_bbox` deve usar o limite:

```text
L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\others\bouding_box\brasil\pol_br_zona_costeira.gpkg
```

## Saidas Esperadas

Arquivo principal:

```text
output\autos_infracao\pnt_pcd_autos_infracao_20260514.gpkg
```

Arquivo secundario:

```text
output\autos_infracao\pnt_pcd_autos_infracao_20260514_bbox_brasil.gpkg
```

O arquivo principal deve conter todos os pontos tratados. O arquivo secundario
deve conter apenas os pontos dentro do limite Brasil / zona costeira.

## Prefect

Deployment:

```text
Data Pipeline/Autos de Infracao
```

Comando para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py auto-infracoes
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Pipeline/Autos de Infracao"
```

Parametros fixos do deployment:

```json
{"theme_folders": ["autos_infracao"]}
```

## Download

- Status na ingest para baixar: nao aplicavel no momento
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao: como nao existe conector de download para `autos_infracao`, a base deve usar `status = Waiting Update` quando o dado ja estiver disponivel para tratamento.

## Criterios De Aceite

- [x] A base roda isolada, sem disparar todas as bases.
- [x] O deployment Prefect existe para acompanhamento em `Runs`.
- [x] O arquivo principal `.gpkg` e gerado.
- [x] O arquivo secundario `_bbox_brasil.gpkg` e gerado quando configurado.
- [x] O arquivo principal passa pelas funcoes obrigatorias.
- [x] `clean_whitespace` aparece no log de funcoes obrigatorias.
- [x] A intersecao municipal cria `acm_cod_munici`, `acm_municipio` e `acm_uf`.
- [x] Registros sem municipio recebem mensagem de fora do limite territorial.
- [x] Os campos de data passam por `validate_date_fields`.
- [x] Os campos de data saem como `DATE` no GeoPackage.
- [x] As verificacoes obrigatorias de qualidade aparecem no log.
- [x] Testes automatizados passam.

## Validacao

Comando executado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Resultado registrado em 2026-05-21:

```text
Ran 93 tests
OK
```
