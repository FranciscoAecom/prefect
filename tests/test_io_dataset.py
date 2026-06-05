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
    resolve_input_dataset_paths,
)
from core.io.dataset import _read_dataframe_with_fallback, write_output_gpkg


class InputDatasetResolverTest(unittest.TestCase):
    def test_rejects_non_vector_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "chuva.png"
            image_path.write_bytes(b"not-a-vector-dataset")

            with self.assertRaisesRegex(ValueError, "Caminho nao suportado"):
                resolve_input_dataset_paths(str(image_path))

    def test_resolves_only_vector_files_from_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shp = folder / "base.shp"
            gpkg = folder / "base.gpkg"
            image = folder / "chuva.png"
            for path in (shp, gpkg, image):
                path.write_bytes(b"placeholder")

            self.assertEqual(
                resolve_input_dataset_paths(str(folder)),
                [str(gpkg), str(shp)],
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
