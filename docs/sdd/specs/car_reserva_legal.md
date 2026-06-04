# Spec: car_reserva_legal/rl_car_*

Status: Baseline atual
Responsavel: Ribeiro / Codex
Data: 2026-05-21

## Objetivo

Processar bases estaduais de Reserva Legal em imoveis rurais, mantendo uma
regra comum para todos os perfis `rl_car_*`.

## Entrada

- Theme folder: `rl_car_*`
- Projeto: `car_reserva_legal`
- Status esperado na ingest para tratamento: `treatment`, podendo combinar com `download` e/ou `publish`.
- Status esperado na ingest para download: `Download`
- Registro(s) de referencia na ingest: um registro por UF
- Formato esperado: camada vetorial poligonal
- Geometria esperada: poligono ou multipoligono
- Fonte declarada: CAR publico por UF
- Caminho temporario declarado: calculado pela ingest/versionamento
- Sistema de referencia declarado: variavel por fonte, reprojetado pelo pipeline
- Base de referencia usada para dominios: rules estaduais existentes
- Base de referencia usada para relacoes: rules estaduais existentes

## Configuracao Do Projeto

- Arquivo: `projects/configs.py`
- `display_name`: `Reserva Legal (RL) nos imoveis rurais`
- `theme_prefixes`: `("rl_car_",)`
- `output_name_template`: `pol_pcd_{theme_folder}_{date_yyyymmdd}`
- `reference_date`: `20260301`

## Regras Do Perfil

Cada UF possui perfil proprio em `rules/car_reserva_legal/<theme_folder>/`.

- `rules/car_reserva_legal/<theme_folder>/profile.json`
- `rules/car_reserva_legal/<theme_folder>/input_schema.json`
- `rules/car_reserva_legal/<theme_folder>/domains.json`
- `rules/car_reserva_legal/<theme_folder>/relations.json`
- `rules/car_reserva_legal/<theme_folder>/pipeline.json`
- `rules/car_reserva_legal/<theme_folder>/style.json`: nao configurado

A validacao estrutural de entrada deve usar o `input_schema.json` do perfil da
UF, permitindo colunas extras conforme configurado.

## Schema De Entrada

Campos obrigatorios configurados:

- definidos por UF em `rules/car_reserva_legal/<theme_folder>/input_schema.json`

Tipos e observacoes:

- O schema deve preservar os campos de origem como `sdb_*`.

## Dominios

Fonte:

- `rules/car_reserva_legal/<theme_folder>/domains.json`

Aplicacao:

- Campos listados em `domains.json` devem ser validados por
  `validate_shapefile_attribute`.

Campos com dominio:

| Campo | Valores aceitos | Observacao |
| --- | ---: | --- |
| `sdb_cod_tema` | varia por UF | Codigo do tema RL CAR |
| `sdb_nom_tema` | varia por UF | Nome do tema RL CAR |
| `sdb_ind_status` | varia por UF | Indicador de status |
| `sdb_des_condic` | varia por UF | Descricao da condicao do cadastro |

Campos presentes no schema sem dominio:

- demais campos definidos em `input_schema.json`

## Relacoes

Relacoes de consistencia configuradas em `relations.json`:

- configuradas por UF em `rules/car_reserva_legal/<theme_folder>/relations.json`

Regra de aplicacao:

- Quando houver divergencia entre campos relacionados, a relacao configurada
  deve prevalecer para normalizar o campo de destino.

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

- `sdb_cod_tema`: `validate_shapefile_attribute`
- `sdb_nom_tema`: `validate_shapefile_attribute`
- `sdb_ind_status`: `validate_shapefile_attribute`
- `sdb_des_condic`: `car_reserva_legal_transform_des_condic`

Postprocess configurado:

- `enforce_car_state_bounds`


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
output\<theme_folder>\pol_pcd_<theme_folder>_20260301.gpkg
```

Outros arquivos de dados persistidos:

- nenhum

XML esperado no bronze e no silver:

```text
md_pcd_<theme_folder>_20260301.xml
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
pol_pcd_<theme_folder>_20260301.gpkg
md_pcd_<theme_folder>_20260301.xml
```

Observacoes:

- A saida deve respeitar o recorte regional da UF por `enforce_car_state_bounds`.
- Se nao houver `style.json`, nao ha SLD para publicacao.

## Prefect

Deployment:

```text
Data Treatment/CAR - Uso Restrito
```

Comando para servir o deployment:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py ur-car-treatment
```

Comando para disparar pelo Prefect:

```powershell
.\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/CAR - Uso Restrito"
```

Parametros fixos do deployment:

```json
{}
```

Agenda:

- agenda compartilhada com o deployment CAR

## Geracao De Rules

Comando ou processo para regenerar rules:

```powershell
nao aplicavel
```

Arquivos atualizados pelo processo:

- nao aplicavel

## Download

- Status na ingest para baixar: `Download`
- Dataset key: `car_reserva_legal`
- Conector/script registrado: `car_public_api`
- Deve tratar automaticamente apos baixar: sim
- Observacao para bases sem download automatico: nao aplicavel; o estado/UF e inferido pelo sufixo do `theme_folder`, por exemplo `rl_car_ac` -> `AC`.

## Versionamento

- `treatment`: trata/padroniza/valida a base e pode criar nova versao quando houver novo bruto.
- A versao nao vem da ingest; ela e calculada pela existencia de arquivos em `bronze_data`.
- Campos obrigatorios para caminho: `access_constraints`, `category_acronym`, `theme_folder`, `citation`, `date`.
- Modulo responsavel: `core.versioning`.

## Criterios De Aceite

- [ ] Cada perfil estadual roda isoladamente.
- [ ] O arquivo principal `.gpkg` e gerado com o nome esperado.
- [ ] O arquivo principal abre no QGIS.
- [ ] A validacao estrutural usa `input_schema.json`.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] As funcoes opcionais configuradas aparecem no log.
- [ ] `enforce_car_state_bounds` fica explicito em `pipeline.json`.
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
