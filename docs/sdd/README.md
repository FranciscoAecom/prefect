# Spec-Driven Development do Projeto

Neste projeto, SDD significa registrar a regra da base antes de implementar ou
alterar codigo. A especificacao vira o contrato entre ingest, regras, pipeline,
saida, testes e agendamento.

## Quando Criar Uma Spec

Crie ou atualize uma spec quando houver:

- nova base, novo `theme_folder` ou novo projeto;
- novo campo `acm_*`;
- novo dominio ou alias em `domains.json`;
- nova funcao obrigatoria, opcional, postprocess ou ajuste de saida principal;
- mudanca de caminho de entrada, nome de saida ou criterio de aceite;
- novo deployment, agenda ou forma de execucao no Prefect.
- nova regra de download automatico.

## Fluxo SDD

1. Especificar a base em `docs/sdd/specs/<slug>.md`, seguindo
   `docs/sdd/spec-template.md`.
2. Revisar entradas, dominios, datas, funcoes obrigatorias e opcionais.
3. Implementar somente o necessario em `rules/`, `projects/`, `core/` e
   `scripts/`.
4. Adicionar ou ajustar testes que provem os criterios de aceite da spec.
5. Rodar validacao local.
6. Atualizar o status da spec.

## Arquivos De Regras Esperados

Cada spec deve apontar para:

- `projects/configs.py`;
- `rules/<projeto>/<theme_folder>/profile.json`;
- `rules/<projeto>/<theme_folder>/input_schema.json`;
- `rules/<projeto>/<theme_folder>/domains.json`;
- `rules/<projeto>/<theme_folder>/pipeline.json`;
- `rules/<projeto>/<theme_folder>/relations.json`;
- `rules/<projeto>/<theme_folder>/style.json`, quando a base gerar SLD.

## Funcoes Sempre Esperadas

As funcoes obrigatorias rodam para todas as bases:

- `clean_whitespace`;
- `reproject_shapefile`;
- `force_geometry_2d`;
- `add_sequential_id`;
- `calculate_area_hectares`;
- `calculate_perimeter_km`;
- `add_centroid_coordinates`.

Funcoes opcionais precisam estar explicitas no perfil, normalmente em
`pipeline.json`, para ficar claro o que roda em cada base.

O `pipeline.json` tambem pode declarar ajustes da saida principal em
`primary_output`. As bases devem gerar somente a saida principal; ajustes como
reposicionar pontos fora do limite Brasil / zona costeira devem ser expressos em
`primary_output`.

Novas chaves de perfil devem ser registradas no contrato tecnico em
`core/rules/contracts.py`, validadas em `core/rules/validation.py` e descritas
em `readme/rules.md`.

Configuracoes visuais, como `sld`, devem ficar em `style.json`. O SLD e gerado
somente para arquivos da etapa `silver_data`; o bronze preserva o dado bruto e
o XML de metadados.

## Download Pela Ingest

O flow `Data Download` usa `status = Download` na aba `datas` para selecionar
bases a baixar automaticamente. Apos o download e extracao, ele dispara o
`Data Pipeline` apenas para o `theme_folder` baixado.

Nem toda base tem download automatico. Para entrar na fila de download, o
`theme_folder` precisa resolver para um dataset em `core/downloads/catalog.py` e
um conector implementado em `core/downloads/connectors/`. Bases sem conector
devem ser tratadas manualmente com `status = Waiting Update` quando o arquivo ja
estiver disponivel.

O download deve gravar o arquivo baixado dentro da camada `temp`, na versao
calculada para a ingestao. O ZIP fica em `_downloads/<dataset_key>/<theme_folder>`
e a extracao fica em `raw`, sempre abaixo do diretorio `temp` planejado.

## Publicacao GeoServer / GeoNetwork

A publicacao e uma etapa separada da geracao da camada `silver_data`. A pasta
publicada deve conter exatamente um conjunto:

- um arquivo de dados (`.gpkg`, `.rst` ou `.tif`);
- um arquivo `.sld`;
- um XML de metadados correspondente.

Se a pasta tiver mais de um arquivo de dados publicavel, a publicacao deve ser
ignorada e o log deve orientar a separar os conjuntos em pastas diferentes ou
publicar uma pasta por vez. Cada pasta de publicacao deve representar um unico
conjunto publicavel.

O SLD e criado apenas na etapa `silver_data`. O XML importado no GeoNetwork deve
preservar o dicionario de dados e receber o link do dicionario publicado quando
o GeoServer retornar os tipos dos atributos.

## Status Da Ingest

A coluna `status` e a unica coluna de controle operacional da ingest:

- `Download`: baixa a base, salva bruto e dispara tratamento.
- `Waiting Update`: trata uma base ja disponivel e pode criar nova versao.
- `Reprocessing`: retrata uma versao existente sem criar nova versao.

Nao criar uma coluna separada para modo de processamento.

## Versionamento Temp/Bronze/Silver

O modulo `core.versioning` centraliza a montagem dos caminhos das camadas
`temp`, `bronze_data` e `silver_data`.

Base fixa:

```text
L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data
```

Estrutura:

```text
<base>\<etapa>\<access_constraints>\<category_acronym>\<theme_folder>\<citation>\<date>\<version>
```

Regras:

- `date` e normalizado para `YYYYMMDD`.
- A versao nao vem da ingest: ela e calculada pela existencia de arquivos em
  `bronze_data`, iniciando em `00`.
- `Download` e `Waiting Update` usam a proxima versao disponivel quando a
  versao atual ja contem `.shp` ou `.gpkg` em `bronze_data`.
- `Reprocessing` reutiliza a ultima versao existente e nao cria uma nova versao.
- A versao decidida deve ser a mesma para `temp`, `bronze_data` e `silver_data`.

## Verificacoes Obrigatorias De Qualidade

Alem das funcoes obrigatorias de transformacao, a persistencia da saida executa
verificacoes obrigatorias de qualidade quando habilitadas em `settings.py`:

- `check_attribute_duplicates`;
- `check_geometric_duplicates`;
- `check_ogc_invalid_geometries`.

Essas verificacoes aparecem no log como
`Verificacoes obrigatorias de qualidade executadas` e podem gerar relatorios de
duplicados por atributos, duplicados geometricos e geometrias invalidas OGC.
Por padrao, o projeto mantem apenas o log e os totais. A exportacao fisica
desses relatorios depende de `EXPORT_OUTPUT_QUALITY_REPORT_FILES = True`.

## Template

Use `docs/sdd/spec-template.md` para criar a proxima especificacao. Todas as
specs devem manter a mesma ordem de secoes, mesmo quando uma secao for marcada
como `nao aplicavel` ou `nao configurado`.

As especificacoes existentes ficam listadas em `docs/sdd/specs/README.md`.
