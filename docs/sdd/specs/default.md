# Spec: default/default

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Definir o comportamento de fallback para bases sem projeto especifico em
`projects/configs.py`.

## Entrada

- Theme folder: variavel
- Projeto: `default`
- Status esperado na ingest para tratamento: `treatment`, podendo combinar com `download` e/ou `publish`.
- Status esperado na ingest para download: nao aplicavel por padrao
- Registro(s) de referencia na ingest: variavel
- Formato esperado: camada vetorial suportada pelo pipeline
- Geometria esperada: depende da base
- Fonte declarada: variavel
- Caminho temporario declarado: variavel
- Sistema de referencia declarado: variavel
- Base de referencia usada para dominios: nao aplicavel por padrao
- Base de referencia usada para relacoes: nao aplicavel por padrao

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: nao configurado
- `theme_prefixes`: vazio
- `output_name_template`: `{input_stem}_validado`
- `reference_date`: `None`

## Regras Do Perfil

- `rules/default/profile.json`
- `rules/default/input_schema.json`
- `rules/default/domains.json`
- `rules/default/relations.json`
- `rules/default/treatment.json`
- `rules/default/style.json`: nao configurado

O perfil default deve ser usado apenas quando nao houver regra modular
especifica para a base.

## Schema De Entrada

Campos obrigatorios configurados:

- nenhum por padrao

Tipos e observacoes:

- O schema depende da base quando um perfil especifico nao existe.

## Dominios

Fonte:

- `rules/default/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| nao aplicavel | 0 | Nenhum campo com dominio por padrao |

Campos presentes no schema sem dominio:

- nao aplicavel por padrao

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- nenhuma por padrao

Regra de aplicacao:

- nao aplicavel

## Datas

Campos tratados por `validate_date_fields`:

- nenhum por padrao

Regra de saida para datas:

- nao aplicavel por padrao

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
output\<theme_folder>\<input_stem>_validado.gpkg
```

Outros arquivos de dados persistidos:

- nenhum por padrao

XML esperado no bronze e no silver:

```text
md_<input_stem>_validado.xml
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
<input_stem>_validado.gpkg
md_<input_stem>_validado.xml
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
nao configurado especificamente para default
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/<deployment>"
```

Parametros fixos do deployment:

```json
{}
```

Agenda:

- nao configurada por padrao

## Geracao De Rules

Comando ou processo para regenerar rules:

```powershell
nao aplicavel
```

Arquivos atualizados pelo processo:

- nao aplicavel

## Download

- Status na ingest para baixar: nao aplicavel por padrao
- Dataset key: nao registrado
- Conector/script registrado: nao
- Deve tratar automaticamente apos baixar: nao
- Observacao para bases sem download automatico: projetos que precisarem de download automatico devem ganhar entrada explicita em `core/downloads/catalog.py` e spec propria.

## Versionamento

- `treatment`: trata/padroniza/valida a base e pode criar nova versao quando houver novo bruto.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] O fallback nao sobrescreve regras de projetos conhecidos.
- [ ] A saida usa o nome do arquivo de entrada.
- [ ] As funcoes obrigatorias aparecem no log.
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

