# Spec: setor_censitario/setor_censitario

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-28

## Objetivo

Processar a malha de setores censitarios do Brasil, preservando os campos de
origem como `sdb_*`, validando apenas dominios controlados e gerando a saida
final poligonal `pol_loc_cse_20241114.gpkg`, com XML de metadados e SLD simples
somente na camada silver.

## Entrada

- Theme folder: `setor_censitario`
- Projeto: `setor_censitario`
- Status esperado na ingest para tratamento: `Waiting Update` ou `Reprocessing`
- Status esperado na ingest para download: nao aplicavel no momento
- Registro de referencia na ingest: `ID 644`
- Formato esperado: camada vetorial poligonal em GPKG
- Geometria esperada: poligono ou multipoligono
- Fonte declarada: IBGE
- Caminho temporario declarado: `L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\temp\setor_censitario\BR_setores_CD2022.gpkg`
- Sistema de referencia declarado: nao registrado nesta spec
- Base de referencia usada para dominios: `C:\Users\RibeiroF\Downloads\Dicionario_de_dados_malha_agregados.xlsx`
- Base vetorial usada para montar relacoes: `BR_setores_CD2022.gpkg`

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Setores censitarios do Brasil`
- `theme_prefixes`: `("setor_censitario",)`
- `output_name_template`: `pol_loc_cse_{date_yyyymmdd}`
- `reference_date`: `20241114`

## Regras Do Perfil

- `rules/setor_censitario/setor_censitario/profile.json`
- `rules/setor_censitario/setor_censitario/input_schema.json`
- `rules/setor_censitario/setor_censitario/domains.json`
- `rules/setor_censitario/setor_censitario/relations.json`
- `rules/setor_censitario/setor_censitario/pipeline.json`
- `rules/setor_censitario/setor_censitario/style.json`

A validacao estrutural de entrada deve usar
`rules/setor_censitario/setor_censitario/input_schema.json`, permitindo colunas
extras.

## Schema De Entrada

Campos obrigatorios configurados:

- `sdb_cd_setor`
- `sdb_situacao`
- `sdb_cd_sit`
- `sdb_cd_tipo`
- `sdb_area_km2`
- `sdb_cd_regiao`
- `sdb_nm_regiao`
- `sdb_cd_uf`
- `sdb_nm_uf`
- `sdb_cd_mun`
- `sdb_nm_mun`
- `sdb_cd_dist`
- `sdb_nm_dist`
- `sdb_cd_subdist`
- `sdb_nm_subdist`
- `sdb_cd_bairro`
- `sdb_nm_bairro`
- `sdb_cd_nu`
- `sdb_nm_nu`
- `sdb_cd_fcu`
- `sdb_nm_fcu`
- `sdb_cd_aglom`
- `sdb_nm_aglom`
- `sdb_cd_rgint`
- `sdb_nm_rgint`
- `sdb_cd_rgi`
- `sdb_nm_rgi`
- `sdb_cd_concurb`
- `sdb_nm_concurb`

Tipos e observacoes:

- `sdb_area_km2` deve ser numerico.
- Os demais campos do schema devem ser tratados como texto.
- A geometria e obrigatoria.

## Dominios

Fonte:

- `rules/setor_censitario/setor_censitario/domains.json`

Aplicacao:

- Somente os campos listados no `pipeline.json` devem ser validados por
  `validate_shapefile_attribute`.
- Campos territoriais de alta cardinalidade, como municipio, distrito,
  subdistrito, bairro, nucleo urbano, favela/comunidade urbana, aglomerado e
  concentracao urbana, fazem parte do schema, mas nao devem ser validados por
  dominio nesta baseline.

Campos com dominio validado:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_situacao` | 2 | Situacao ampla do setor: `Urbana` ou `Rural` |
| `sdb_cd_sit` | 8 | Situacao detalhada, incluindo codigo `9` para massas de agua |
| `sdb_cd_tipo` | 10 | Tipo do setor censitario |
| `sdb_cd_regiao` | 5 | Codigo da grande regiao |
| `sdb_nm_regiao` | 5 | Nome da grande regiao |
| `sdb_cd_uf` | 27 | Codigo da unidade da federacao |
| `sdb_nm_uf` | 27 | Nome da unidade da federacao |
| `sdb_cd_rgint` | 133 | Codigo da regiao geografica intermediaria |
| `sdb_nm_rgint` | 133 | Nome da regiao geografica intermediaria |
| `sdb_cd_rgi` | 510 | Codigo da regiao geografica imediata |
| `sdb_nm_rgi` | 508 | Nome da regiao geografica imediata |

Aliases configurados:

- `sdb_nm_rgint`: 1 alias para corrigir separador mojibake `¿`.
- `sdb_nm_rgi`: 8 aliases para corrigir separador mojibake `¿`.

Regra importante:

- `sdb_cd_sit = 9` e valor valido no dominio de `sdb_cd_sit`, mas nao deve ser
  usado para preencher `sdb_situacao`, pois `sdb_situacao` aceita apenas
  `Urbana` e `Rural`.

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- `cd_regiao_to_nm_regiao`
- `cd_uf_to_nm_uf`
- `cd_rgint_to_nm_rgint`
- `cd_rgi_to_nm_rgi`

Quando houver divergencia entre codigo e nome para campos relacionados, a regra
de relacao deve prevalecer para normalizar o campo de destino.

Relacoes removidas por risco de correcao indevida:

- `cd_sit_to_situacao`: nao configurada porque `CD_SITUACAO` e mais detalhado
  que `SITUACAO`, e o codigo `9` representa massas de agua, sem equivalencia
  valida em `Urbana` ou `Rural`.
- Relacoes de municipio, distrito, subdistrito, bairro, nucleo urbano,
  favela/comunidade urbana, aglomerado e concentracao urbana nao devem ser
  configuradas nesta baseline.

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

- `sdb_situacao`: `validate_shapefile_attribute`
- `sdb_cd_sit`: `validate_shapefile_attribute`
- `sdb_cd_tipo`: `validate_shapefile_attribute`
- `sdb_cd_regiao`: `validate_shapefile_attribute`
- `sdb_nm_regiao`: `validate_shapefile_attribute`
- `sdb_cd_uf`: `validate_shapefile_attribute`
- `sdb_nm_uf`: `validate_shapefile_attribute`
- `sdb_cd_rgint`: `validate_shapefile_attribute`
- `sdb_nm_rgint`: `validate_shapefile_attribute`
- `sdb_cd_rgi`: `validate_shapefile_attribute`
- `sdb_nm_rgi`: `validate_shapefile_attribute`

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

O SLD deve ser gerado somente no silver.

Arquivo:

```text
rules/setor_censitario/setor_censitario/style.json
```

Regra principal:

- `version`: `1.1.0`
- `rule_name`: `Single symbol`
- geometria: poligono
- preenchimento: `#ef8e03`
- contorno: `#232323`
- largura do contorno: `1`
- juncao do contorno: `bevel`

## Saidas Esperadas

Arquivo principal:

```text
output\setor_censitario\pol_loc_cse_20241114.gpkg
```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text
md_loc_cse_20241114.xml
```

SLD esperado somente no silver:

```text
sld_pol_loc_cse_20241114.sld
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
8. Criar e salvar o SLD do silver.

O bronze nao deve gerar SLD. Ele deve conter somente o dado bruto e o XML de
metadados.

## Publicacao

Esta base gera um unico conjunto publicavel:

```text
pol_loc_cse_20241114.gpkg
sld_pol_loc_cse_20241114.sld
md_loc_cse_20241114.xml
```

## Prefect

Deployment:

```text
nao configurado
```

Comando para servir o deployment:

```powershell
nao aplicavel
```

Comando para disparar pelo Prefect:

```powershell
nao aplicavel
```

Parametros fixos do deployment:

```json
{"theme_folders": ["setor_censitario"]}
```

Agenda:

- nao configurada

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
- Observacao: como nao existe conector de download para `setor_censitario`, a base deve usar `status = Waiting Update` quando o dado ja estiver disponivel para tratamento.

## Versionamento

- `Waiting Update`: pode criar nova versao quando houver novo bruto.
- `Reprocessing`: deve reutilizar a ultima versao existente e nao criar nova versao.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] A base roda isolada quando `theme_folders=["setor_censitario"]`.
- [ ] O arquivo principal `.gpkg` e gerado com nome `pol_loc_cse_20241114.gpkg`.
- [ ] O arquivo principal abre no QGIS como camada poligonal.
- [ ] A validacao estrutural usa `input_schema.json`.
- [ ] Apenas os 11 dominios controlados passam por `validate_shapefile_attribute`.
- [ ] `sdb_cd_sit = 9` e aceito sem gerar correcao automatica para `sdb_situacao`.
- [ ] As 4 relacoes de codigo/nome configuradas sao aplicadas.
- [ ] Relacoes de municipio/distrito/subdistrito/bairro e demais campos de alta cardinalidade nao sao configuradas.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] O XML do bronze e do silver usa prefixo `md_`.
- [ ] O bronze preserva o bruto sem alterar dados nem nome do arquivo.
- [ ] O SLD simples e gerado somente no silver com nome `sld_pol_loc_cse_20241114.sld`.
- [ ] Testes automatizados relevantes passam.

## Validacao

Comando executado:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_setor_censitario_rules tests.test_sld_persistence
```

Resultado:

```text
OK
```
