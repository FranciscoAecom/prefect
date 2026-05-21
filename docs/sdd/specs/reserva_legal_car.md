# Spec: reserva_legal_car/rl_car_*

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar bases estaduais de Reserva Legal em imoveis rurais, mantendo uma regra
comum para todos os perfis `rl_car_*`.

## Entrada

- Projeto: `reserva_legal_car`
- Theme folders: `rl_car_ac`, `rl_car_al`, `rl_car_am`, `rl_car_ap`, `rl_car_ba`, `rl_car_ce`, `rl_car_df`, `rl_car_es`, `rl_car_go`, `rl_car_ma`, `rl_car_mg`, `rl_car_ms`, `rl_car_mt`, `rl_car_pa`, `rl_car_pb`, `rl_car_pe`, `rl_car_pi`, `rl_car_pr`, `rl_car_rj`, `rl_car_rn`, `rl_car_ro`, `rl_car_rr`, `rl_car_rs`, `rl_car_sc`, `rl_car_se`, `rl_car_sp`, `rl_car_to`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `Reserva Legal (RL) nos imoveis rurais`
- `theme_prefixes`: `("rl_car_",)`
- `output_name_template`: `pol_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260301`

## Regras Do Perfil

Cada UF possui perfil proprio em `rules/reserva_legal_car/<theme_folder>/`.

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
- `sdb_desc_condic`: `reserva_legal_car_transform_desc_condic`

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
- Dataset key: `car_reserva_legal`
- Conector/script registrado: `car_public_api`
- Deve tratar automaticamente apos baixar: sim
- Observacao: o estado/UF e inferido pelo sufixo do `theme_folder`, por exemplo `rl_car_ac` -> `AC`.

## Criterios De Aceite

- [ ] Cada perfil estadual roda isoladamente.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] `enforce_car_state_bounds` fica explicito em `pipeline.json`.
- [ ] Nao gera saida secundaria `brazil_bbox`.
- [ ] Testes automatizados relevantes passam.
