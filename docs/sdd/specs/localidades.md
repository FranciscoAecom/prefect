# Spec: localidades/localidades

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-27

## Objetivo

Processar a base de localidades do Brasil, preservando os campos de origem como
`sdb_*`, validando dominios territoriais e categorias de localidade, gerando a
saida final de pontos `pnt_loc_loc_br_20251119.gpkg` e o SLD categorizado por
tipo de localidade.

## Entrada

- Theme folder: `localidades`
- Projeto: `localidades`
- Status esperado na ingest para tratamento: `Waiting Update`
- Registro de referencia na ingest: `ID 641`
- Formato esperado: camada vetorial de pontos
- Geometria esperada: ponto
- Fonte declarada na ingest: `https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/27385-localidades.html`
- Caminho temporario declarado na ingest: `L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\temp\localidade\Localidades_Brasil_gpkg`
- Sistema de referencia declarado: `SIRGAS 2000`
- Base de referencia usada para montar dominios: `C:\Temp\Repositorios\explorer\teste.xlsx`
- Base vetorial usada para montar relacoes: `L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\temp\localidade\Localidades_Brasil_gpkg\BR_localidades_2022.gpkg`

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Localidades do Brasil`
- `theme_prefixes`: `("loc",)`
- `output_name_template`: `pnt_loc_loc_br_{date_yyyymmdd}`
- `reference_date`: `20251119`

## Regras Do Perfil

- `rules/localidades/localidades/profile.json`
- `rules/localidades/localidades/input_schema.json`
- `rules/localidades/localidades/domains.json`
- `rules/localidades/localidades/relations.json`
- `rules/localidades/localidades/pipeline.json`
- `rules/localidades/localidades/style.json`

A validacao estrutural de entrada deve usar
`rules/localidades/localidades/input_schema.json`, permitindo colunas extras.

## Schema De Entrada

Campos obrigatorios configurados:

- `sdb_cd_uf`
- `sdb_nm_uf`
- `sdb_sigla_uf`
- `sdb_cd_mun`
- `sdb_nm_mun`
- `sdb_cd_rgint`
- `sdb_nm_rgint`
- `sdb_cd_rgi`
- `sdb_nm_rgi`
- `sdb_ct_localidade`
- `sdb_sct_localidade`
- `sdb_cd_localidade`
- `sdb_nm_localidade`
- `sdb_lat_localidade`
- `sdb_long_localidade`

`sdb_lat_localidade` e `sdb_long_localidade` devem ser numericos. Os demais
campos do schema devem ser tratados como texto.

## Dominios

Fonte:

- `rules/localidades/localidades/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_cd_uf` | 27 | Codigo da unidade da federacao |
| `sdb_nm_uf` | 27 | Nome da unidade da federacao |
| `sdb_sigla_uf` | 27 | Sigla da unidade da federacao |
| `sdb_cd_mun` | 5571 | Codigo do municipio |
| `sdb_nm_mun` | 5297 | Nome do municipio |
| `sdb_cd_rgint` | 133 | Codigo da regiao geografica intermediaria |
| `sdb_nm_rgint` | 133 | Nome da regiao geografica intermediaria |
| `sdb_cd_rgi` | 510 | Codigo da regiao geografica imediata |
| `sdb_nm_rgi` | 508 | Nome da regiao geografica imediata |
| `sdb_ct_localidade` | 12 | Categoria da localidade |
| `sdb_sct_localidade` | 7 | Subcategoria da localidade |

Campos presentes no schema sem dominio:

- `sdb_cd_localidade`
- `sdb_nm_localidade`
- `sdb_lat_localidade`
- `sdb_long_localidade`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- `cd_uf_to_nm_uf`
- `cd_uf_to_sigla_uf`
- `cd_mun_to_nm_mun`
- `cd_mun_to_cd_uf`
- `cd_rgint_to_nm_rgint`
- `cd_rgint_to_cd_uf`
- `cd_rgi_to_nm_rgi`
- `cd_rgi_to_cd_rgint`
- `cd_rgi_to_cd_uf`

Quando houver divergencia entre codigo e nome para campos relacionados, a regra
de relacao deve prevalecer para normalizar o campo de destino.

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

- `validate_shapefile_attribute`

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

O SLD deve ser gerado somente no silver e usar `sdb_ct_localidade` como campo de
categorizacao.

Arquivo:

```text
rules/localidades/localidades/style.json
```

Regra principal:

- `rule_name`: `Categorias de localidade`
- geometria: ponto circular
- fallback: preenchimento `#817E7C`, contorno `#232323`, largura `0.5`, tamanho `7`

Categorias esperadas:

- `Agrovila do PA`
- `Cidade`
- `Distrito Estadual de Fernando de Noronha`
- `Localidade Indigena`
- `Localidade Quilombola`
- `Lugarejo`
- `Nucleo Rural`
- `Nucleo Urbano`
- `Outras Localidades`
- `Povoado`
- `Regioes Administrativas do Distrito Federal`
- `Vila`

## Saidas Esperadas

Arquivo principal:

```text
output\localidades\pnt_loc_loc_br_20251119.gpkg
```

XML esperado no bronze e no silver:

```text
md_loc_loc_br_20251119.xml
```

SLD esperado somente no silver:

```text
pnt_loc_loc_br_20251119.sld
```

O bronze nao deve gerar SLD. Ele deve conter somente o dado bruto e o XML de
metadados.

O fluxo deve seguir esta ordem no log:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.
8. Criar e salvar o SLD do silver.

## Publicacao

Esta base gera um unico conjunto publicavel:

```text
pnt_loc_loc_br_20251119.gpkg
pnt_loc_loc_br_20251119.sld
md_loc_loc_br_20251119.xml
```

## Prefect

Deployment:

```text
Data Pipeline/Localidades
```

Comando para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py localidades
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Pipeline/Localidades"
```

Parametros fixos do deployment:

```json
{"theme_folders": ["localidades"]}
```

Agenda:

- nao configurada

## Geracao De Rules

As rules de dominios e relacoes podem ser regeneradas com:

```powershell
.\.venv\Scripts\python.exe scripts\generate_localidades_rules.py
```

O script atualiza:

- `rules/localidades/localidades/domains.json`
- `rules/localidades/localidades/relations.json`

## Download

- Status na ingest para baixar: nao aplicavel no momento
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao: como nao existe conector de download para `localidades`, a base deve usar `status = Waiting Update` quando o dado ja estiver disponivel para tratamento.

## Versionamento

- `Waiting Update`: pode criar nova versao quando houver novo bruto.
- `Reprocessing`: deve reutilizar a ultima versao existente e nao criar nova versao.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] A base roda isolada, sem disparar todas as bases.
- [ ] O arquivo principal `.gpkg` e gerado com nome `pnt_loc_loc_br_20251119.gpkg`.
- [ ] O arquivo principal abre no QGIS como camada de pontos.
- [ ] A validacao estrutural usa `input_schema.json`.
- [ ] Os 11 campos com dominio passam por `validate_shapefile_attribute`.
- [ ] As 9 relacoes de codigo/nome e hierarquia territorial sao aplicadas.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] O XML do bronze e do silver usa prefixo `md_`.
- [ ] O bronze preserva o bruto sem alterar dados nem nome do arquivo.
- [ ] O SLD categorizado por `sdb_ct_localidade` e gerado somente no silver.
- [ ] O deployment `Localidades` recebe `theme_folders=["localidades"]`.
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
