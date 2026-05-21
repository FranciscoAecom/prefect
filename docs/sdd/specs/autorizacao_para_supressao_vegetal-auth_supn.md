# Spec: autorizacao_para_supressao_vegetal/auth_supn

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de Autorizacao para Supressao Vegetal.

## Entrada

- Projeto: `autorizacao_para_supressao_vegetal`
- Theme folder: `auth_supn`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `Autorizacao para Supressao Vegetal`
- `theme_prefixes`: `("auth_supn",)`
- `output_name_template`: `pol_env_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20250701`

## Regras Do Perfil

- `rules/autorizacao_para_supressao_vegetal/auth_supn/profile.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/input_schema.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/domains.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/relations.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/pipeline.json`

## Datas

Campos tratados como data:

- `sdb_author_dat`
- `sdb_expira_dat`
- `sdb_dat_d_base`

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

- `sdb_descriptio`: `validate_shapefile_attribute`
- `sdb_transparen`: `validate_shapefile_attribute`
- `sdb_jurisdicti`: `validate_shapefile_attribute`
- `sdb_author_dat`: `validate_date_fields`
- `sdb_expira_dat`: `validate_date_fields`
- `sdb_dat_d_base`: `validate_date_fields`

Postprocess configurado:

- nenhum

Saidas secundarias configuradas:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

## Saidas Esperadas

- Arquivo principal: `output\auth_supn\pol_env_auth_supn_20250701.gpkg`

## Download

- Status na ingest para baixar: nao aplicavel no momento
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao: usar `status = Waiting Update` quando o dado ja estiver disponivel para tratamento.

## Criterios De Aceite

- [ ] A base roda isolada.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] Os campos de data passam por `validate_date_fields`.
- [ ] Testes automatizados relevantes passam.
