# Spec: ur_car/ur_car_*

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar bases estaduais de Area de Uso Restrito em imoveis rurais, mantendo
uma regra comum para todos os perfis `ur_car_*`.

## Entrada

- Projeto: `ur_car`
- Theme folders: `ur_car_ac`, `ur_car_al`, `ur_car_am`, `ur_car_ap`, `ur_car_ba`, `ur_car_ce`, `ur_car_df`, `ur_car_es`, `ur_car_go`, `ur_car_ma`, `ur_car_mg`, `ur_car_ms`, `ur_car_mt`, `ur_car_pa`, `ur_car_pb`, `ur_car_pe`, `ur_car_pi`, `ur_car_pr`, `ur_car_rj`, `ur_car_rn`, `ur_car_ro`, `ur_car_rr`, `ur_car_rs`, `ur_car_sc`, `ur_car_se`, `ur_car_sp`, `ur_car_to`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `Area de Uso Restrito nos imoveis rurais`
- `theme_prefixes`: `("ur_car_",)`
- `output_name_template`: `pol_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260514`

## Regras Do Perfil

Cada UF possui perfil proprio em `rules/ur_car/<theme_folder>/`.

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
- `sdb_desc_condic`: `ur_car_transform_desc_condic`

Postprocess configurado:

- nenhum

Saidas secundarias configuradas:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

## Saidas Esperadas

- Arquivo principal: `output\<theme_folder>\pol_pcd_<theme_folder>_20260514.gpkg`

## Prefect

Deployment atual:

```text
Data Pipeline/CAR - Uso Restrito
```

Comando para servir:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py ur-car-processing
```

## Download

- Status na ingest para baixar: `Download`
- Dataset key: `car_uso_restrito`
- Conector/script registrado: `car_public_api`
- Deve tratar automaticamente apos baixar: sim
- Observacao: o estado/UF e inferido pelo sufixo do `theme_folder`, por exemplo `ur_car_ac` -> `AC`.

## Criterios De Aceite

- [ ] Cada perfil estadual roda isoladamente.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] O deployment agendado usa o nome `CAR - Uso Restrito`.
- [ ] Testes automatizados relevantes passam.
