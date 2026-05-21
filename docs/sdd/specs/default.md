# Spec: default

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Definir o comportamento de fallback para bases sem projeto especifico em
`projects/configs.py`.

## Entrada

- Projeto: `default`
- Theme folder: variavel
- Formato esperado: camada vetorial suportada pelo pipeline
- Geometria esperada: depende da base

## Configuracao Do Projeto

- `project_name`: `default`
- `theme_prefixes`: vazio
- `output_name_template`: `{input_stem}_validado`
- `reference_date`: `None`

## Regras Do Perfil

- `rules/default/profile.json`

O perfil default deve ser usado apenas quando nao houver regra modular
especifica para a base.

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

- nenhuma por padrao

Postprocess configurado:

- nenhum

Saidas secundarias configuradas:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

## Saidas Esperadas

- Arquivo principal: `output\<theme_folder>\<input_stem>_validado.gpkg`

## Download

- Status na ingest para baixar: nao aplicavel por padrao
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao: projetos que precisarem de download automatico devem ganhar entrada explicita em `core/downloads/catalog.py` e spec propria.

## Criterios De Aceite

- [ ] O fallback nao sobrescreve regras de projetos conhecidos.
- [ ] A saida usa o nome do arquivo de entrada.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] Testes automatizados relevantes passam.
