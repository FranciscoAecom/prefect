# Spec: estado/estado

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de limites das unidades da federacao do Brasil.

## Entrada

- Theme folder: `estado`
- Projeto: `estado`
- Status esperado na ingest para tratamento: `treatment`, podendo combinar com `download` e/ou `publish`.
- Status esperado na ingest para download: nao aplicavel no momento
- Registro(s) de referencia na ingest: nao registrado nesta spec
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono
- Fonte declarada: nao registrado nesta spec
- Caminho temporario declarado: nao registrado nesta spec
- Sistema de referencia declarado: nao registrado nesta spec
- Base de referencia usada para dominios: rules existentes
- Base de referencia usada para relacoes: rules existentes

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Limites das unidades da federacao do Brasil`
- `theme_prefixes`: `("estado",)`
- `output_name_template`: `pol_loc_sta_{date_yyyymmdd}`
- `reference_date`: `20241215`

## Regras Do Perfil

- `rules/estado/estado/profile.json`
- `rules/estado/estado/input_schema.json`
- `rules/estado/estado/domains.json`
- `rules/estado/estado/relations.json`
- `rules/estado/estado/treatment.json`
- `rules/estado/estado/style.json`: nao configurado

A validacao estrutural de entrada deve usar
`rules/estado/estado/input_schema.json`, permitindo colunas extras conforme o
perfil.

## Schema De Entrada

Campos obrigatorios configurados:

- `sdb_nm_uf`
- `sdb_sigla_uf`
- `sdb_nm_regiao`
- `sdb_cd_uf`
- `sdb_cd_regiao`
- `sdb_area_km2`

Tipos e observacoes:

- `sdb_area_km2` deve ser numerico.
- Os demais campos do schema devem ser tratados como texto.

## Dominios

Fonte:

- `rules/estado/estado/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_nm_uf` | 27 | Nome da unidade da federacao |
| `sdb_sigla_uf` | 27 | Sigla da unidade da federacao |
| `sdb_nm_regiao` | 5 | Nome da regiao |
| `sdb_cd_uf` | 27 | Codigo da unidade da federacao |
| `sdb_cd_regiao` | 5 | Codigo da regiao |

Campos presentes no schema sem dominio:

- `sdb_area_km2`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- configuradas em `rules/estado/estado/relations.json`

Regra de aplicacao:

- Quando houver divergencia entre campos relacionados, a relacao configurada
  deve prevalecer para normalizar o campo de destino.

## Datas

Campos tratados por `validate_date_fields`:

- nenhum

Regra de saida para datas:

- nao aplicavel

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


Saida principal configurada:

- nenhuma

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`
- `check_geometric_duplicates`
- `check_ogc_invalid_geometries`

Essas verificacoes devem aparecer no log. A geracao fisica de relatorios segue
o valor de `EXPORT_OUTPUT_QUALITY_REPORT_FILES`.

## Estilo SLD

- Arquivo: nao aplicavel
- Campo de categorizacao: nao aplicavel
- Regra principal: nao aplicavel

## Saidas Esperadas

Arquivo principal:

```text
output\estado\pol_loc_sta_20241215.gpkg
```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text
md_loc_sta_20241215.xml
```

SLD esperado somente no silver:

```text
nao aplicavel
```

Campos `acm_*` obrigatorios:

- `acm_id`
- `acm_a_ha`
- `acm_prm_km`
- `acm_long`
- `acm_lat`

O fluxo deve seguir esta ordem no log:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.
8. Criar e salvar o SLD do silver, quando houver `style.json`.

## Publicacao

Conjunto publicavel esperado:

```text
pol_loc_sta_20241215.gpkg
md_loc_sta_20241215.xml
```

Observacoes:

- Se nao houver `style.json`, nao ha SLD para publicacao.

## Prefect

Deployment:

```text
Data Treatment/Treatment Agendado pela Ingest
```

Comando para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py estado
```

Comando para disparar pelo Prefect:

```powershell
'{"theme_folders":["estado"]}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/Treatment Agendado pela Ingest" --params -
```

Parametros fixos do deployment:

```json
{"theme_folders": ["estado"]}
```

Agenda:

- diaria as 02:00 no fuso `America/Sao_Paulo`

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
- Observacao para bases sem download automatico: usar `status = treatment` quando o dado ja estiver disponivel para tratamento.

## Versionamento

- `treatment`: trata/padroniza/valida a base e pode criar nova versao quando houver novo bruto.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] A base roda isolada, sem disparar todas as bases.
- [ ] O arquivo principal `.gpkg` e gerado com o nome esperado.
- [ ] O arquivo principal abre no QGIS.
- [ ] A validacao estrutural usa `input_schema.json`.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] As funcoes opcionais configuradas aparecem no log.
- [ ] As verificacoes obrigatorias de qualidade aparecem no log.
- [ ] O deployment generico recebe `theme_folders=["estado"]`.
- [ ] Testes automatizados relevantes passam.

## Validacao

Comando executado:

```powershell
nao executado
```

Resultado:

```text
nao registrado
```

