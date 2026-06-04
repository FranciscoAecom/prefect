# Contrato Generico De Regras Modulares

Cada perfil em `rules/` deve ficar em uma pasta com cinco arquivos
obrigatorios. Quando a base precisar de SLD, o perfil tambem deve conter
`style.json`:

```text
rules/<projeto>/<perfil>/
  profile.json
  input_schema.json
  domains.json
  relations.json
  treatment.json
  style.json
```

Use `rules/_template/` como ponto de partida para uma nova base. Regras de
negocio especificas devem ser descritas na spec da base em `docs/sdd/specs/`.

## profile.json

Metadados do perfil.

```json
{
  "profile_name": "rl_car_ac",
  "project_name": "car_reserva_legal",
  "theme_folder": "rl_car_ac",
  "description": "Regras para Reserva Legal do CAR AC."
}
```

Campos obrigatorios:

- `profile_name`: nome do perfil.
- `project_name`: projeto responsavel pelo perfil.
- `theme_folder`: deve bater com o nome final da pasta do perfil.

`theme_folder` e a chave operacional da ingest/base, por exemplo `rl_car_ac`.
`project_name` e a familia interna de regras, por exemplo `car_reserva_legal`.
Os nomes antigos de projeto (`app_car`, `reserva_legal_car`, `sa_car`,
`ur_car`) existem apenas como aliases de compatibilidade; novos perfis devem
usar os nomes canonicos `car_*`.

## input_schema.json

Define o contrato tabular da entrada. Ele e usado em duas etapas:

- validacao estrutural logo apos a leitura do arquivo, conferindo campos
  obrigatorios e colunas extras;
- validacao/conversao de tipos antes do processamento principal.

A validacao estrutural ignora campos gerados depois do tratamento, como
`acm_*`, alem de `fid` e `geometry`.

```json
{
  "columns": {
    "sdb_cod_tema": {
      "dtype": "string",
      "required": true,
      "nullable": false
    }
  },
  "require_geometry": true,
  "allow_extra_columns": true
}
```

Tipos aceitos em `dtype`:

- `string`, `str`, `text`
- `number`, `numeric`
- `float`, `double`
- `integer`, `int`
- `datetime`, `date`
- `boolean`, `bool`

Observacoes:

- As colunas sao validadas depois da normalizacao para `sdb_*`.
- Quando o tipo lido nao bate com `dtype`, o pipeline tenta converter a coluna automaticamente e registra a conversao no log.
- Se a conversao gerar novos nulos em uma coluna com `nullable: false`, o processamento para com erro.
- Use `required: false` para colunas que podem nao existir na entrada.
- Use `nullable: false` quando a coluna nao pode conter valores nulos.
- Para campos de data, use `dtype: "date"` quando o contrato esperado for data.
- Se o campo ja vier tipado como data, `validate_date_fields` mantem o `sdb_*`
  sem criar `acm_*`.
- Se o campo vier como texto e o schema esperar `date`, `validate_date_fields`
  preserva o `sdb_*` original e cria `acm_*` com a data normalizada.

## domains.json

Define dominios aceitos e aliases por coluna.

```json
{
  "fields": {
    "sdb_cod_tema": {
      "accepted_values": [
        "ARL_AVERBADA"
      ],
      "aliases": {
        "ARL AVERBADA": "ARL_AVERBADA"
      }
    }
  }
}
```

`accepted_values` deve ser uma lista de strings. `aliases` deve mapear valores alternativos para um valor canonico existente em `accepted_values`.

## relations.json

Define consistencia entre campos.

```json
{
  "relations": {
    "cod_tema_to_nom_tema": {
      "ARL_AVERBADA": "Reserva Legal Averbada"
    }
  }
}
```

O nome da relacao segue o padrao `<origem>_to_<destino>`. O pipeline resolve esses tokens para colunas como `sdb_cod_tema` e `sdb_nom_tema`.

## treatment.json

Define funcoes configuraveis do perfil.

```json
{
  "postprocess_functions": [
    "enforce_car_state_bounds"
  ],
  "output_adjustments": {
    "relocate_outside_brazil_bounds_to_centroid": false
  },
  "auto_functions": {
    "sdb_cod_tema": [
      "validate_shapefile_attribute"
    ]
  }
}
```

- `auto_functions`: funcoes por atributo. Cada chave e uma coluna e cada valor e a lista de funcoes que roda nessa coluna.
- `postprocess_functions`: funcoes que rodam depois do processamento principal e alteram o GeoDataFrame final.
- `output_adjustments`: ajustes aplicados somente ao arquivo de dados persistido.

Funcoes de atributo podem ser nomes curtos registrados em `projects/registry.py` ou nomes qualificados como `pacote.modulo.funcao`.

Funcoes de pos-processamento disponiveis no core:

- `enforce_car_state_bounds`: valida/recorta geometrias CAR pelo bbox regional da UF inferida.
- `enrich_with_municipality_intersection`: intersecta os pontos com a base de municipios e cria `acm_cod_munici`, `acm_municipio` e `acm_uf`.

Opcoes de `output_adjustments`:

- `relocate_outside_brazil_bounds_to_centroid`: quando `true`, mantem todos os
  registros no arquivo de dados e move geometrias fora do limite Brasil / zona
  costeira para um ponto unico dentro do limite brasileiro.

Remova `postprocess_functions` quando a base nao deve usar essa etapa.

As chaves operacionais aceitas em `treatment.json` sao centralizadas em
`core/rules/contracts.py`. Ao criar uma nova opcao, registre a chave no contrato
e adicione validacao explicita.

## style.json

Define configuracoes de estilo do perfil. Hoje o componente usado e `sld`,
gerado somente para arquivos `.gpkg` persistidos na etapa `silver_data`.

```json
{
  "sld": {
    "version": "1.1.0",
    "rule_name": "Single symbol",
    "point": {
      "well_known_name": "circle",
      "fill": "#1654ad",
      "stroke": "#232323",
      "stroke_width": "0.5",
      "size": "7"
    },
    "layers": {
      "pnt_pcd_enov_20260514": {
        "point": {
          "fill": "#ef8e03"
        }
      },
    }
  }
}
```

O `treatment.json` nao deve conter `sld`. Configuracoes visuais ficam em
`style.json`; configuracoes de execucao ficam em `treatment.json`. Use `layers`
quando uma saida especifica precisar sobrescrever o estilo padrao do perfil.

## Fluxo De Persistencia

O perfil nao deve alterar a ordem padrao do pipeline:

1. Ler arquivo no `temp`.
2. Copiar o bruto para `bronze_data`, sem alterar dados nem nome do arquivo.
3. Criar o XML do bronze.
4. Salvar o XML do bronze na pasta do bronze.
5. Executar os tratamentos.
6. Salvar o dado tratado no `silver_data`.
7. Criar e salvar o XML do silver.
8. Criar e salvar o SLD do silver, quando houver `style.json`.

Os XMLs usam prefixo `md_` e preservam o restante do nome logico da saida.
O SLD e criado somente no `silver_data`; o bronze preserva apenas o dado bruto
e o XML de metadados.

## Validacao

O carregador valida cada componente separadamente e depois consolida tudo em memoria no formato usado pelo pipeline:

```json
{
  "profile_name": "...",
  "project_name": "...",
  "theme_folder": "...",
  "input_schema": {},
  "fields": {},
  "relations": {},
  "auto_functions": {},
  "postprocess_functions": [],
  "sld": {}
}
```

Para verificar os perfis:

```powershell
py -3.14 -m unittest tests.test_rule_profiles_integration
```

