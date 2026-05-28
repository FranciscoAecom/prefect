# Spec: <projeto>/<theme_folder>

Status: Draft
Responsavel: <nome>
Data: <AAAA-MM-DD>

## Objetivo

Descrever o que esta base representa e qual resultado o pipeline deve entregar.

## Entrada

- Theme folder:
- Projeto:
- Status esperado na ingest para tratamento: `Waiting Update` ou `Reprocessing`
- Status esperado na ingest para download: `Download` ou nao aplicavel
- Registro(s) de referencia na ingest:
- Formato esperado:
- Geometria esperada:
- Fonte declarada:
- Caminho temporario declarado:
- Sistema de referencia declarado:
- Base de referencia usada para dominios:
- Base de referencia usada para relacoes:

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`:
- `theme_prefixes`:
- `output_name_template`:
- `reference_date`:

## Regras Do Perfil

- `rules/<projeto>/<theme_folder>/profile.json`
- `rules/<projeto>/<theme_folder>/input_schema.json`
- `rules/<projeto>/<theme_folder>/domains.json`
- `rules/<projeto>/<theme_folder>/relations.json`
- `rules/<projeto>/<theme_folder>/pipeline.json`
- `rules/<projeto>/<theme_folder>/style.json`, quando houver SLD

A validacao estrutural de entrada deve usar `input_schema.json`, permitindo ou
recusando colunas extras conforme configurado no perfil. Campos gerados depois
do tratamento (`acm_*`), `fid` e `geometry` nao entram nessa conferencia
estrutural.

## Schema De Entrada

Campos obrigatorios configurados:

- 

Tipos e observacoes:

- 

## Dominios

Fonte:

- `rules/<projeto>/<theme_folder>/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
|  |  |  |

Campos presentes no schema sem dominio:

- 

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- 

Regra de aplicacao:

- Quando houver divergencia entre campos relacionados, a relacao configurada
  deve prevalecer para normalizar o campo de destino.

## Datas

Campos tratados por `validate_date_fields`:

- nao aplicavel

Regra de saida para datas:

- se o campo original ja vier tipado como data, manter somente o `sdb_*`;
- se o campo vier como texto, preservar o `sdb_*` original e gerar o `acm_*`
  correspondente normalizado como `DATE`, sem horario;
- datas normalizadas devem sair como `DATE`, exceto quando a regra da base
  exigir explicitamente `DateTime`.

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

- 

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

O SLD deve ser gerado somente no `silver_data`; o bronze nao gera SLD.

## Saidas Esperadas

Arquivo principal:

```text

```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text

```

SLD esperado somente no silver:

```text
nao aplicavel
```

Quando aplicavel, usar o padrao `sld_<nome_do_dataset>.sld`.

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

```

Observacoes:

- A publicacao deve receber um unico conjunto de dado, XML e SLD por pasta.

## Prefect

Deployment:

```text

```

Comando para servir o deployment:

```powershell

```

Comando para disparar pelo Prefect:

```powershell

```

Parametros fixos do deployment:

```json
{}
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

- Status na ingest para baixar:
- Dataset key:
- Conector/script registrado:
- Deve tratar automaticamente apos baixar:
- Observacao para bases sem download automatico:

## Versionamento

- `Waiting Update`: pode criar nova versao quando houver novo bruto.
- `Reprocessing`: deve reutilizar a ultima versao existente e nao criar nova versao.
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
- [ ] O SLD configurado e gerado somente no silver.
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
