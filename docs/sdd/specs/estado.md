# Spec: estado/estado

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de limites das unidades da federacao do Brasil.

## Entrada

- Projeto: `estado`
- Theme folder: `estado`
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono

## Configuracao Do Projeto

- `display_name`: `Limites das unidades da federacao do Brasil`
- `theme_prefixes`: `("estado",)`
- `output_name_template`: `pol_loc_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20241215`

## Regras Do Perfil

- `rules/estado/estado/profile.json`
- `rules/estado/estado/input_schema.json`
- `rules/estado/estado/domains.json`
- `rules/estado/estado/relations.json`
- `rules/estado/estado/pipeline.json`

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

- `sdb_nm_uf`: `validate_shapefile_attribute`
- `sdb_sigla_uf`: `validate_shapefile_attribute`
- `sdb_nm_regiao`: `validate_shapefile_attribute`
- `sdb_cd_uf`: `validate_shapefile_attribute`
- `sdb_cd_regiao`: `validate_shapefile_attribute`

Postprocess configurado:

- nenhum

Saidas secundarias configuradas:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

## Saidas Esperadas

- Arquivo principal: `output\estado\pol_loc_estado_20241215.gpkg`

## Prefect

Comando para servir:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py estado
```

O deployment `Estado` possui agenda diaria as 02:00 no fuso
`America/Sao_Paulo`.

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
- [ ] O deployment `Estado` recebe `theme_folders=["estado"]`.
- [ ] Testes automatizados relevantes passam.
