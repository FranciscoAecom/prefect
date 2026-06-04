import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from core.raster.processing import build_raster_request, process_raster_request


def _import_gdal_or_skip(testcase):
    try:
        from osgeo import gdal, osr
    except ImportError:
        testcase.skipTest("GDAL/osgeo nao esta instalado neste ambiente")
    gdal.UseExceptions()
    return gdal, osr


class RasterGdalIntegrationTests(unittest.TestCase):
    def test_processes_small_geotiff_when_gdal_is_available(self):
        gdal, osr = _import_gdal_or_skip(self)

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "entrada.tif"
            output_path = Path(temp_dir) / "saida.tif"
            driver = gdal.GetDriverByName("GTiff")
            dataset = driver.Create(str(input_path), 16, 16, 1, gdal.GDT_UInt16)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            dataset.SetProjection(srs.ExportToWkt())
            dataset.SetGeoTransform((0, 1, 0, 0, 0, -1))
            band = dataset.GetRasterBand(1)
            band.SetNoDataValue(0)
            band.WriteArray(np.arange(256, dtype=np.uint16).reshape(16, 16))
            dataset.FlushCache()
            dataset = None

            request = build_raster_request(
                input_raster=input_path,
                output_raster=output_path,
            )
            result = process_raster_request(request)

            self.assertTrue(output_path.exists())
            self.assertEqual(result.output_dtype, "uint8")
            self.assertEqual(result.dst_epsg, 4326)
            self.assertEqual(result.output_raster, str(output_path.resolve()))


if __name__ == "__main__":
    unittest.main()
