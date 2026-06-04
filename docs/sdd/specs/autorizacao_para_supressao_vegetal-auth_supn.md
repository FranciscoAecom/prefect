# Spec: autorizacao_para_supressao_vegetal/auth_supn

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar a base de Autorizacao para Supressao Vegetal, preservando os campos
de origem como `sdb_*`, validando dominios configurados e normalizando datas de
autorizacao, expiracao e data-base.

## Entrada

- Theme folder: `auth_supn`
- Projeto: `autorizacao_para_supressao_vegetal`
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
- `display_name`: `Autorizacao para Supressao Vegetal`
- `theme_prefixes`: `("auth_supn",)`
- `output_name_template`: `pol_env_auth_supn_{date_yyyymmdd}`
- `reference_date`: `20250701`

## Regras Do Perfil

- `rules/autorizacao_para_supressao_vegetal/auth_supn/profile.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/input_schema.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/domains.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/relations.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/pipeline.json`
- `rules/autorizacao_para_supressao_vegetal/auth_supn/style.json`: nao configurado

A validacao estrutural de entrada deve usar
`rules/autorizacao_para_supressao_vegetal/auth_supn/input_schema.json`,
permitindo colunas extras conforme o perfil.

## Schema De Entrada

Campos obrigatorios configurados:

- definidos em `rules/autorizacao_para_supressao_vegetal/auth_supn/input_schema.json`

Tipos e observacoes:

- Os campos de data configurados devem ser tratados conforme a secao `Datas`.

## Dominios

Fonte:

- `rules/autorizacao_para_supressao_vegetal/auth_supn/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_descriptio` | 3 | Descricao/categoria configurada na regra |
| `sdb_transparen` | 1 | Valor de transparencia configurado na regra |
| `sdb_jurisdicti` | 1 | Jurisdicao configurada na regra |

Campos presentes no schema sem dominio:

- `sdb_author_dat`
- `sdb_expira_dat`
- `sdb_dat_d_base`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- configuradas em `rules/autorizacao_para_supressao_vegetal/auth_supn/relations.json`

Regra de aplicacao:

- Quando houver divergencia entre campos relacionados, a relacao configurada
  deve prevalecer para normalizar o campo de destino.

## Datas

Campos tratados por `validate_date_fields`:

- `sdb_author_dat`
- `sdb_expira_dat`
- `sdb_dat_d_base`

Regra de saida para datas:

- se o campo original ja vier tipado como data, manter somente o `sdb_*`;
- se o campo vier como texto, preservar o `sdb_*` original e gerar o `acm_*`
  correspondente normalizado como `DATE`, sem horario;
- datas normalizadas devem sair como `DATE`.

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
output\auth_supn\pol_env_auth_supn_20250701.gpkg
```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text
md_env_auth_supn_20250701.xml
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
- campos `acm_*` derivados das datas quando o campo de entrada vier como texto

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
pol_env_auth_supn_20250701.gpkg
md_env_auth_supn_20250701.xml
```

Observacoes:

- Se nao houver `style.json`, nao ha SLD para publicacao.

## Prefect

Deployment:

```text
Data Treatment
```

Comando para servir o deployment:

```powershell
nao configurado especificamente para auth_supn
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/<deployment>" --param theme_folders='["auth_supn"]'
```

Parametros fixos do deployment:

```json
{"theme_folders": ["auth_supn"]}
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
- [ ] Os campos de data passam por `validate_date_fields`.
- [ ] Os campos de data normalizados saem como `DATE`.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] As funcoes opcionais configuradas aparecem no log.
- [ ] As verificacoes obrigatorias de qualidade aparecem no log.
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
