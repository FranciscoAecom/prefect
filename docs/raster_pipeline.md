# Raster Pipeline

O tratamento raster fica centralizado em:

- `core/flow/raster.py`: flow Prefect `Raster Pipeline`.
- `core/tasks/raster.py`: task Prefect `Otimizar raster GDAL`.
- `core/raster/`: logica modular de analise, decisao de dtype, reprojecao, compressao e overviews.

## Execucao direta

```powershell
.\.venv\Scripts\python.exe -c "from core.flow.raster import raster_pipeline_flow; raster_pipeline_flow.fn(input_raster='entrada.tif', output_raster='saida.tif', source_epsg=4674)"
```

Parametros principais:

- `input_raster`: raster de entrada.
- `output_raster`: GeoTIFF de saida. Quando omitido, usa `<nome>_wgs84_lzw.tif`.
- `source_epsg`: obrigatorio quando o raster nao possui CRS no metadado.
- `dst_epsg`: padrao `4326`.
- `nodata_mode`: `auto`, `none` ou `custom`.
- `custom_nodata`: valor usado quando `nodata_mode='custom'`.
- `resampling_mode`: `auto`, `near`, `bilinear` ou `cubic`.

## GDAL

O GDAL e obrigatorio para executar o tratamento raster. O import de `osgeo/gdal`
e lazy apenas para manter o restante do repositorio importavel e testavel em
ambientes que ainda nao tenham GDAL instalado.

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

No Windows, a rota mais estavel tende a ser executar esse flow em um ambiente
isolado para raster, como OSGeo4W Shell ou conda-forge, em vez de misturar GDAL
no mesmo ambiente usado para todo o pipeline vetorial.

## Proxima integracao

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
