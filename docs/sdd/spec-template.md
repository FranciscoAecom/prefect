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
- Status esperado na ingest:
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

## Campos E Dominios

Listar apenas campos que precisam de regra explicita.

| Campo de entrada | Campo ACM | Tipo | Regra | Observacao |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Datas

| Campo | Formato esperado | Regra |
| --- | --- | --- |
|  |  |  |

Campos tratados por `validate_date_fields` devem sair no GeoPackage como
`DATE`, sem componente de horario, exceto quando a regra da base exigir
explicitamente `DateTime`.

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
- Relatorios esperados:
- Campos `acm_*` obrigatorios:

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
