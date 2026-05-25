# Spec: autos_infracao/autos_infracao

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
- `rules/autos_infracao/autos_infracao/pipeline.json`
- `rules/autos_infracao/autos_infracao/style.json`

A validacao estrutural de entrada deve usar
`rules/autos_infracao/autos_infracao/input_schema.json`, ignorando campos que
entram depois do tratamento (`acm_*`), `fid` e `geometry`.

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

Saidas secundarias configuradas:

- `brazil_bbox`

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

A saida secundaria `brazil_bbox` deve usar o limite:

```text
L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\others\bouding_box\brasil\pol_br_zona_costeira.gpkg
```

## Saidas Esperadas

Arquivo principal:

```text
output\autos_infracao\pnt_pcd_enov_20260514.gpkg
```

Arquivo secundario:

```text
output\autos_infracao\pnt_pcd_enov_bbox_brasil_20260514.gpkg
```

XML esperado no bronze e no silver:

```text
md_pcd_enov_20260514.xml
```

XML da saida secundaria no silver:

```text
md_pcd_enov_bbox_brasil_20260514.xml
```

SLD esperado somente no silver:

```text
pnt_pcd_enov_20260514.sld
pnt_pcd_enov_bbox_brasil_20260514.sld
```

Estilo SLD:

- `pnt_pcd_enov_20260514`: ponto circular, preenchimento `#ef8e03`,
  contorno `#232323`, largura `0.5`, tamanho `7`.
- `pnt_pcd_enov_bbox_brasil_20260514`: ponto circular, preenchimento
  `#1654ad`, contorno `#232323`, largura `0.5`, tamanho `7`.

O arquivo principal deve conter todos os pontos tratados. O arquivo secundario
deve conter apenas os pontos dentro do limite Brasil / zona costeira.

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

Esta base gera uma saida principal e uma saida secundaria. Pela regra operacional
atual de publicacao, cada pasta publicada deve conter apenas um conjunto
`dados + SLD + XML`. Se as duas saidas estiverem na mesma pasta, o flow de
publicacao deve registrar aviso e nao publicar automaticamente.

Para publicar `pnt_pcd_enov_20260514` e
`pnt_pcd_enov_bbox_brasil_20260514`, separe os conjuntos em pastas diferentes
ou execute a publicacao apontando para uma pasta que contenha somente o conjunto
desejado.

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
