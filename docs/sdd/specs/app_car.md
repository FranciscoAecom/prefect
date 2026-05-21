# Spec: app_car/app_car_*

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar bases estaduais de Areas de Preservacao Permanente em imoveis rurais,
mantendo uma regra comum para todos os perfis `app_car_*`.

## Entrada

- Projeto: `app_car`
- Theme folders: `app_car_ac`, `app_car_al`, `app_car_am`, `app_car_ap`, `app_car_ba`, `app_car_ce`, `app_car_df`, `app_car_es`, `app_car_go`, `app_car_ma`, `app_car_mg`, `app_car_ms`, `app_car_mt`, `app_car_pa`, `app_car_pb`, `app_car_pe`, `app_car_pi`, `app_car_pr`, `app_car_rj`, `app_car_rn`, `app_car_ro`, `app_car_rr`, `app_car_rs`, `app_car_sc`, `app_car_se`, `app_car_sp`, `app_car_to`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `Areas de Preservacao Permanentes (APP) nos imoveis rurais`
- `theme_prefixes`: `("app_car_",)`
- `output_name_template`: `pol_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260301`

## Regras Do Perfil

Cada UF possui perfil proprio em `rules/app_car/<theme_folder>/`.

Arquivos esperados por perfil:

- `profile.json`
- `input_schema.json`
- `domains.json`
- `relations.json`
- `pipeline.json`

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

- `sdb_cod_tema`: `validate_shapefile_attribute`
- `sdb_nom_tema`: `validate_shapefile_attribute`
- `sdb_desc_condic`: `car_app_transform_desc_condic`

Postprocess configurado:

- `enforce_car_state_bounds`

Saidas secundarias configuradas:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

## Saidas Esperadas

- Arquivo principal: `output\<theme_folder>\pol_pcd_<theme_folder>_20260301.gpkg`
- A saida deve respeitar o recorte regional da UF por `enforce_car_state_bounds`.

## Prefect

Execucao via deployment CAR:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Pipeline/CAR - Uso Restrito"
```

Quando rodar uma base especifica, informar `theme_folders` com o perfil desejado.

## Download

- Status na ingest para baixar: `Download`
- Dataset key: `car_app`
- Conector/script registrado: `car_public_api`
- Deve tratar automaticamente apos baixar: sim
- Observacao: o estado/UF e inferido pelo sufixo do `theme_folder`, por exemplo `app_car_ac` -> `AC`.

## Criterios De Aceite

- [ ] Cada perfil estadual roda isoladamente.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] `enforce_car_state_bounds` fica explicito em `pipeline.json`.
- [ ] Nao gera saida secundaria `brazil_bbox`.
- [ ] Testes automatizados relevantes passam.
