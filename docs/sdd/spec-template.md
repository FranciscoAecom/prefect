# Spec: <projeto>/<theme_folder>

Status: Draft
Responsavel: <nome>
Data: <AAAA-MM-DD>

## Objetivo

Descrever o que esta base representa e qual resultado o pipeline deve entregar.

## Entrada

- Theme folder:
- Projeto:
- Linha(s) da ingest:
- Status esperado na ingest: `Download`, `Waiting Update` ou `Reprocessing`
- Caminho de entrada:
- Formato:
- Geometria esperada:
- CRS esperado ou desconhecido:

## Configuracao Do Projeto

- `projects/configs.py`:
- `display_name`:
- `theme_prefixes`:
- `output_name_template`:
- `reference_date`:

## Regras Do Perfil

- `profile.json`:
- `input_schema.json`:
- `domains.json`:
- `relations.json`:
- `pipeline.json`:

O `input_schema.json` deve ser a fonte da validacao estrutural de entrada:
campos obrigatorios, tipos esperados e permissao de colunas extras. Campos
gerados depois do tratamento (`acm_*`), `fid` e `geometry` nao entram nessa
conferencia estrutural.

## Campos E Dominios

Listar apenas campos que precisam de regra explicita.

| Campo de entrada | Campo ACM | Tipo | Regra | Observacao |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Datas

| Campo | Formato esperado | Regra |
| --- | --- | --- |
|  |  |  |

Campos tratados por `validate_date_fields` seguem o `input_schema.json`:

- se o campo ja vier tipado como data, manter o `sdb_*` sem criar `acm_*`;
- se o schema esperar `date`, mas o campo vier como texto, preservar o `sdb_*`
  original e criar `acm_*` com a data normalizada;
- datas normalizadas devem sair como `DATE`, sem componente de horario, exceto
  quando a regra da base exigir explicitamente `DateTime`.

## Funcoes Do Pipeline

Obrigatorias:

- `clean_whitespace`;
- `reproject_shapefile`;
- `force_geometry_2d`;
- `add_sequential_id`;
- `calculate_area_hectares`;
- `calculate_perimeter_km`;
- `add_centroid_coordinates`.

Opcionais por atributo:

- 

Postprocess:

- 

Saidas secundarias:

- 

Verificacoes obrigatorias de qualidade:

- `check_attribute_duplicates`;
- `check_geometric_duplicates`;
- `check_ogc_invalid_geometries`.

## Saidas Esperadas

- Arquivo principal:
- Arquivos secundarios:
- XML bronze:
- XML silver:
- Relatorios esperados:
- Campos `acm_*` obrigatorios:

Ordem obrigatoria do fluxo:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.

Os XMLs usam prefixo `md_` e mantem o restante do nome logico da saida.

## Prefect

- Deployment:
- Parametros:
- Agenda:
- Comando de serve:
- Comando de execucao manual:

## Download

- Status na ingest para baixar: `Download`
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

- [ ] A base roda sem erro.
- [ ] O arquivo principal abre no QGIS.
- [ ] As funcoes obrigatorias aparecem no log.
- [ ] As funcoes opcionais configuradas aparecem no log.
- [ ] As verificacoes obrigatorias de qualidade aparecem no log.
- [ ] Os campos obrigatorios existem na saida.
- [ ] As saidas secundarias configuradas sao geradas.
- [ ] Testes automatizados relevantes passam.

## Validacao

Comandos:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Evidencias:

- 
