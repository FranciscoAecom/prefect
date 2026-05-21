# Spec: sa_car/sa_car_*

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar bases estaduais de CAR de Servidao Administrativa, mantendo uma regra
comum para todos os perfis `sa_car_*`.

## Entrada

- Projeto: `sa_car`
- Theme folders: `sa_car_ac`, `sa_car_al`, `sa_car_am`, `sa_car_ap`, `sa_car_ba`, `sa_car_ce`, `sa_car_df`, `sa_car_es`, `sa_car_go`, `sa_car_ma`, `sa_car_mg`, `sa_car_ms`, `sa_car_mt`, `sa_car_pa`, `sa_car_pb`, `sa_car_pe`, `sa_car_pi`, `sa_car_pr`, `sa_car_rj`, `sa_car_rn`, `sa_car_ro`, `sa_car_rr`, `sa_car_rs`, `sa_car_sc`, `sa_car_se`, `sa_car_sp`, `sa_car_to`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `CAR de Servidao Administrativa`
- `theme_prefixes`: `("sa_car_",)`
- `output_name_template`: `pol_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260301`

## Regras Do Perfil

Cada UF possui perfil proprio em `rules/sa_car/<theme_folder>/`.

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
- `sdb_ind_status`: `validate_shapefile_attribute`
- `sdb_desc_condic`: `sa_car_transform_desc_condic`

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
- Dataset key: `car_servidao_administrativa`
- Conector/script registrado: `car_public_api`
- Deve tratar automaticamente apos baixar: sim
- Observacao: o estado/UF e inferido pelo sufixo do `theme_folder`, por exemplo `sa_car_ac` -> `AC`.

## Criterios De Aceite

- [ ] Cada perfil estadual roda isoladamente.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] `enforce_car_state_bounds` fica explicito em `pipeline.json`.
- [ ] Nao gera saida secundaria `brazil_bbox`.
- [ ] Testes automatizados relevantes passam.
