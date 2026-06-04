# Raster Processing

O tratamento raster fica centralizado em:

- `core/raster/`: logica modular de analise, decisao de dtype, reprojecao, compressao e overviews.
- `core/processing/dispatcher.py`: escolhe processamento vetorial ou raster por extensao/tipo resolvido.

## Execucao

Raster entra pelo mesmo `Data Pipeline` usado para SHP/GPKG. Preencha a planilha
ingest com `status` elegivel e `path_shapefile_temp` apontando para `.tif` ou
`.tiff`.

Parametros principais:

- `path_shapefile_temp`: raster de entrada.
- `source_epsg` ou `raster_source_epsg`: obrigatorio quando o raster nao possui CRS no metadado.
- `dst_epsg`: padrao `4326`.
- `raster_nodata_mode`: `auto`, `none` ou `custom`.
- `raster_custom_nodata` ou `custom_nodata`: valor usado quando o modo e `custom`.
- `raster_resampling_mode`: `auto`, `near`, `bilinear` ou `cubic`.

## GDAL

O GDAL e obrigatorio para executar o tratamento raster. O import de `osgeo/gdal`
e lazy apenas para manter o restante do repositorio importavel e testavel em
ambientes que ainda nao tenham GDAL instalado.

Quem for processar apenas `.shp` e `.gpkg` nao precisa instalar GDAL. Quem for
processar `.tif` ou `.tiff` precisa executar o pipeline em um ambiente com
`osgeo/gdal` disponivel.

O extra `raster` declara os bindings Python:

```powershell
uv pip install -e ".[raster]"
```

Como GDAL depende de biblioteca nativa, a versao do pacote Python precisa ser
compativel com a versao nativa instalada. Quando usar OSGeo4W, conda-forge ou
outra distribuicao com GDAL proprio, valide a versao nativa antes de instalar os
bindings. A documentacao oficial do pacote GDAL recomenda casar o binding com a
versao de `gdal-config --version`, por exemplo `gdal[numpy]=="$(gdal-config
--version).*"` em ambientes Unix-like.

No Windows, a rota mais estavel tende a ser executar esse processamento em um
ambiente isolado para raster, como conda-forge ou OSGeo4W Shell, em vez de
compilar GDAL via `pip`.

Exemplo com Miniforge/conda-forge:

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" create -n prefect-gdal -c conda-forge python=3.14 gdal geopandas pandas numpy pyarrow pyproj shapely openpyxl prefect pyogrio -y
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m pip install -e .
```

Validacao:

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -c "from osgeo import gdal; print(gdal.VersionInfo('--version'))"
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m unittest tests.test_raster_gdal_integration
```

## Execucao com Prefect e GDAL

Quando a fila tiver raster, execute o pipeline pelo mesmo ambiente onde o GDAL
foi validado. Evite `uv run python main.py` para raster se o `osgeo` foi
instalado apenas no ambiente conda, porque `uv run` usa o `.venv` padrao do
projeto.

Com o servidor Prefect ja aberto:

```powershell
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python -m prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
& "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat" run -n prefect-gdal python main.py
```

Atalho:

```powershell
.\scripts\run_pipeline_gdal.ps1 -CheckOnly
.\scripts\run_pipeline_gdal.ps1
```

## Integracao com a ingest

O raster pode usar a mesma planilha ingest e os mesmos status operacionais:

- `Waiting Update`
- `Reprocessing`
- `Download` para a etapa de download, quando houver conector configurado

Para processamento, informe `theme_folder`, `status` e o caminho do arquivo em
`path_shapefile_temp`, seguindo o mesmo padrao ja usado para SHP e GPKG.

O tipo de tratamento e definido pela extensao do arquivo:

- `.shp` e `.gpkg`: tratamento vetorial.
- `.tif` e `.tiff`: tratamento raster com GDAL.

Colunas opcionais para raster:

- `raster_source_epsg` ou `source_epsg`: usado quando o raster nao possui CRS no metadado.
- `raster_nodata_mode`: `auto`, `none` ou `custom`.
- `raster_custom_nodata` ou `custom_nodata`: valor NoData quando o modo e `custom`.
- `raster_resampling_mode`: `auto`, `near`, `bilinear` ou `cubic`.

Registros raster entram no mesmo `Data Pipeline`, mas sao despachados para o
processador raster em vez do processador vetorial. Rules vetoriais nao sao
exigidas para raster nesta primeira integracao.

## Saidas bronze e silver

O raster segue a mesma organizacao operacional de pastas do pipeline vetorial:

- bronze: copia do dado bruto `.tif/.tiff` em `bronze_dir`.
- silver: raster tratado com GDAL em `output_dir`/silver, usando o padrao de
  nome final do projeto raster.

Nesta integracao, o XML/SLD automatico continua restrito aos produtos
vetoriais. Para raster, o pipeline garante a preservacao do bruto no bronze e a
entrega do GeoTIFF tratado no silver.
