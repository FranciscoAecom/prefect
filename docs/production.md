# Operacao em Producao

Este guia concentra os comandos de operacao diaria do projeto.

## Ambiente

Use o ambiente `uv` do projeto. O projeto nao depende de Conda, GDAL ou OSGeo4W.

```powershell
cd "C:\Temp\Repositorios\prefect"
uv sync
```

Em caminhos Windows com acento, prefira chamar o Prefect via Python:

```powershell
.\.venv\Scripts\python.exe -m prefect --version
```

## Subir Prefect Local

O script operacional inicia o servidor, configura a API local e serve os tres
deployments oficiais:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting
```

Para resetar o banco local do Prefect e recriar tudo do zero:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting -ResetDatabase
```

Painel:

```text
http://127.0.0.1:4200
```

## Flows Oficiais

O painel deve mostrar somente:

```text
Data Download
Data Treatment
Data Publish
```

Deployments esperados:

```text
Data Download/Download de Dados
Data Treatment/Treatment Agendado pela Ingest
Data Publish/Publish GeoServer GeoNetwork
```

## Flags da Ingest

A coluna `status` aceita:

```text
download
treatment
publish
```

As flags podem ser combinadas:

```text
download-treatment
treatment-publish
download-treatment-publish
```

Agendamento one-shot:

```text
schedule 2026-06-05 18:49
```

Quando alterar ou inserir linhas `schedule YYYY-MM-DD HH:MM` na planilha
ingest, rode novamente o script operacional para recriar o deployment e carregar
os novos agendamentos no Prefect:

```powershell
cd "C:\Temp\Repositorios\prefect"
.\scripts\start_prefect_local.ps1 -StopExisting
```

Para recriar tudo com banco zerado:

```powershell
.\scripts\start_prefect_local.ps1 -StopExisting -ResetDatabase
```

O schedule fica cadastrado no deployment em `Schedules`. Datas muito distantes
podem nao aparecer imediatamente na lista de flow runs agendados, porque o
Prefect materializa runs futuros apenas dentro da janela do scheduler.

## Execucao Manual

Rodar tratamento local:

```powershell
cd "C:\Temp\Repositorios\prefect"
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
uv run python main.py
```

Confirmar que o servidor Prefect esta ativo:

```powershell
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
.\.venv\Scripts\python.exe -m prefect flow ls
```

Rodar uma base especifica pelo deployment:

```powershell
'{"theme_folders":["ur_car_pi"]}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Treatment/Treatment Agendado pela Ingest" --params -
```

Listar flows e deployments:

```powershell
$env:PREFECT_API_URL="http://127.0.0.1:4200/api"
.\.venv\Scripts\python.exe -m prefect flow ls
.\.venv\Scripts\python.exe -m prefect deployment ls
```

## Publicacao

Credenciais devem vir de variaveis de ambiente ou parametros do run:

```powershell
$env:PUBLISH_GEOSERVER_USERNAME="usuario"
$env:PUBLISH_GEOSERVER_PASSWORD="senha"
$env:PUBLISH_GEONETWORK_USERNAME="usuario"
$env:PUBLISH_GEONETWORK_PASSWORD="senha"
```

Teste sem publicar:

```powershell
'{"folder":"<silver-folder>","environment":"qas","workspace":"gold","dry_run":true}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Publish/Publish GeoServer GeoNetwork" --params -
```

Publicacao real:

```powershell
'{"folder":"<silver-folder>","environment":"qas","workspace":"gold","dry_run":false}' | .\.venv\Scripts\python.exe -m prefect deployment run "Data Publish/Publish GeoServer GeoNetwork" --params -
```

## Validacao Antes de Produzir

```powershell
uv run python -m compileall core scripts tests
uv run python -m unittest discover -s tests
```

Resultado esperado:

```text
OK
```

## Artefatos Locais

Arquivos locais ignorados pelo Git:

```text
.prefect-local/
.prefect-logs/
.workflow-locks/
```
