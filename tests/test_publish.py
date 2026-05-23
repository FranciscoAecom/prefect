import tempfile
import unittest
from pathlib import Path

from core.publish.metadata import (
    discover_publish_items,
    metadata_stem_for_data_stem,
    metadata_title,
)
from core.publish.geoserver import add_windows_schannel_ssl_option
from core.publish.sld import prepare_sld_for_upload
from core.publish.urls import (
    geonetwork_records_import_urls,
    geoserver_data_upload_url,
)


class PublishTests(unittest.TestCase):
    def test_metadata_stem_uses_md_prefix(self):
        self.assertEqual(
            metadata_stem_for_data_stem("pnt_pcd_enov_bbox_brasil_20260514"),
            "md_pcd_enov_bbox_brasil_20260514",
        )

    def test_discover_publish_items_matches_multiple_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self._write_triplet(folder, "pnt_pcd_enov_20260514")
            self._write_triplet(folder, "pnt_pcd_enov_bbox_brasil_20260514")

            items = discover_publish_items(folder)

            self.assertEqual(
                [item.layer for item in items],
                [
                    "pnt_pcd_enov_20260514",
                    "pnt_pcd_enov_bbox_brasil_20260514",
                ],
            )
            self.assertEqual(items[0].xml_path.name, "md_pcd_enov_20260514.xml")
            self.assertEqual(
                items[1].xml_path.name,
                "md_pcd_enov_bbox_brasil_20260514.xml",
            )

    def test_metadata_title_reads_iso_title(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "md_test.xml"
            xml_path.write_text(self._metadata_xml("Titulo Teste"), encoding="utf-8")

            self.assertEqual(metadata_title(xml_path), "Titulo Teste")

    def test_prepare_sld_for_upload_sets_layer_and_style_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sld_path = Path(temp_dir) / "pnt_teste.sld"
            sld_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.1.0" xmlns:se="http://www.opengis.net/se">
  <NamedLayer>
    <se:Name>old_layer</se:Name>
    <UserStyle>
      <se:Name>old_style</se:Name>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
""",
                encoding="utf-8",
            )

            upload_path = prepare_sld_for_upload(sld_path, "new_style", "new_layer")

            text = upload_path.read_text(encoding="utf-8")
            self.assertIn("new_layer", text)
            self.assertIn("new_style", text)

    def test_urls_match_expected_geoserver_and_geonetwork_shapes(self):
        self.assertEqual(
            geoserver_data_upload_url(
                "https://gis/geoserver",
                "gold",
                "datastores",
                "store1",
                "gpkg",
            ),
            "https://gis/geoserver/rest/workspaces/gold/datastores/store1/file.gpkg?configure=all",
        )
        self.assertIn(
            "https://catalog/srv/api/records?metadataType=METADATA",
            geonetwork_records_import_urls("https://catalog", "2", "3")[0],
        )

    def test_adds_ssl_no_revoke_for_https_curl_on_windows_schannel(self):
        arguments = add_windows_schannel_ssl_option(
            ["--request", "GET", "https://gisqas.iocasta.com.br/geoserver"]
        )

        self.assertEqual(arguments[0], "--ssl-no-revoke")

    def _write_triplet(self, folder, data_stem):
        (folder / f"{data_stem}.gpkg").write_bytes(b"gpkg")
        (folder / f"{data_stem}.sld").write_text(
            "<StyledLayerDescriptor />",
            encoding="utf-8",
        )
        (folder / f"{metadata_stem_for_data_stem(data_stem)}.xml").write_text(
            self._metadata_xml(data_stem),
            encoding="utf-8",
        )

    def _metadata_xml(self, title):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco">
  <gmd:identificationInfo>
    <gmd:MD_DataIdentification>
      <gmd:citation>
        <gmd:CI_Citation>
          <gmd:title>
            <gco:CharacterString>{title}</gco:CharacterString>
          </gmd:title>
        </gmd:CI_Citation>
      </gmd:citation>
    </gmd:MD_DataIdentification>
  </gmd:identificationInfo>
</gmd:MD_Metadata>
"""


if __name__ == "__main__":
    unittest.main()
