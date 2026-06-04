import tempfile
import unittest
from pathlib import Path
import gc
from unittest.mock import patch

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely.geometry import Point

from core.ingest.dataset_resolver import (
    DATASET_KIND_RASTER,
    DATASET_KIND_VECTOR,
    dataset_kind_for_path,
    resolve_input_dataset_paths,
)
from core.io.dataset import _read_dataframe_with_fallback, write_output_gpkg


class InputDatasetResolverTest(unittest.TestCase):
    def test_accepts_raster_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            raster_path = Path(tmp) / "chuva.tif"
            raster_path.write_bytes(b"not-a-real-raster")

            self.assertEqual(resolve_input_dataset_paths(str(raster_path)), [str(raster_path)])
            self.assertEqual(dataset_kind_for_path(raster_path), DATASET_KIND_RASTER)
            self.assertEqual(dataset_kind_for_path("base.gpkg"), DATASET_KIND_VECTOR)

    def test_resolves_vector_and_raster_files_from_same_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shp = folder / "base.shp"
            gpkg = folder / "base.gpkg"
            tif = folder / "chuva.tif"
            for path in (shp, gpkg, tif):
                path.write_bytes(b"placeholder")

            self.assertEqual(
                resolve_input_dataset_paths(str(folder)),
                [str(gpkg), str(shp), str(tif)],
            )


class ReadInputDatasetTest(unittest.TestCase):
    @patch("core.io.dataset.pyogrio.read_dataframe")
    @patch("core.io.dataset.USE_ARROW_IO", True)
    def test_shapefile_uses_utf8_without_arrow(self, mock_read_dataframe):
        _read_dataframe_with_fallback("entrada.shp")

        mock_read_dataframe.assert_called_once_with(
            "entrada.shp",
            layer=None,
            encoding="UTF-8",
        )

    @patch("core.io.dataset.pyogrio.read_dataframe")
    @patch("core.io.dataset.USE_ARROW_IO", False)
    def test_shapefile_uses_utf8_when_arrow_setting_is_disabled(
        self,
        mock_read_dataframe,
    ):
        _read_dataframe_with_fallback("entrada.shp")

        mock_read_dataframe.assert_called_once_with(
            "entrada.shp",
            layer=None,
            encoding="UTF-8",
        )

    @patch("core.io.dataset.pyogrio.read_dataframe")
    @patch("core.io.dataset.USE_ARROW_IO", True)
    def test_shapefile_keeps_driver_encoding_when_cpg_exists(
        self,
        mock_read_dataframe,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            shapefile = Path(tmp) / "entrada.shp"
            shapefile.with_suffix(".cpg").write_text("CP1252", encoding="ascii")

            _read_dataframe_with_fallback(shapefile)

        mock_read_dataframe.assert_called_once_with(
            shapefile,
            layer=None,
        )


class WriteOutputGpkgTest(unittest.TestCase):
    def test_date_only_datetime_columns_are_written_as_gpkg_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "datas.gpkg"
            gdf = gpd.GeoDataFrame(
                {
                    "acm_data": [
                        pd.Timestamp("2026-05-21"),
                        pd.NaT,
                    ],
                    "acm_data_hora": [
                        pd.Timestamp("2026-05-21 10:30:00"),
                        pd.NaT,
                    ],
                },
                geometry=[Point(0, 0), Point(1, 1)],
                crs="EPSG:4326",
            )

            write_output_gpkg(gdf, output)

            info = pyogrio.read_info(output)
            field_types = dict(zip(info["fields"], info["ogr_types"]))

            self.assertEqual(field_types["acm_data"], "OFTDate")
            self.assertEqual(field_types["acm_data_hora"], "OFTDateTime")
            del info
            gc.collect()


if __name__ == "__main__":
    unittest.main()
