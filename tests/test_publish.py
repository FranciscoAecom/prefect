import tempfile
import unittest
import json
from pathlib import Path

from core.publish.metadata import (
    MultiplePublishItemsError,
    add_data_dictionary_link,
    data_dictionary_field_type,
    discover_publish_items,
    geoserver_layer_title,
    metadata_xml_with_data_dictionary_link,
    metadata_stem_for_data_stem,
    metadata_title,
    set_data_dictionary_field_types,
)
from core.publish.geoserver import add_windows_schannel_ssl_option, convert_geoserver_binding
from core.publish.sld import prepare_sld_for_upload
from core.publish.sld import sld_content_type
from core.publish.urls import (
    geonetwork_records_import_urls,
    geoserver_data_upload_url,
)


class PublishTests(unittest.TestCase):
    def test_metadata_stem_uses_md_prefix(self):
        self.assertEqual(
            metadata_stem_for_data_stem("pnt_pcd_enov_20260514"),
            "md_pcd_enov_20260514",
        )

    def test_discover_publish_items_rejects_multiple_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self._write_triplet(folder, "pnt_pcd_enov_20260514")
            self._write_triplet(folder, "pnt_pcd_enov_extra_20260514")

            with self.assertRaises(MultiplePublishItemsError):
                discover_publish_items(folder)

    def test_discover_publish_items_accepts_single_output_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self._write_triplet(folder, "pnt_pcd_enov_20260514")

            items = discover_publish_items(folder)

            self.assertEqual([item.layer for item in items], ["pnt_pcd_enov_20260514"])
            self.assertEqual(items[0].xml_path.name, "md_pcd_enov_20260514.xml")

    def test_discover_publish_items_uses_primary_manifest_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self._write_triplet(folder, "pnt_pcd_enov_20260514")
            self._write_manifest(
                folder,
                primary="pnt_pcd_enov_20260514",
                quality_reports={
                    "attribute_duplicates": str(folder / "duplicados.xlsx")
                },
            )

            items = discover_publish_items(folder)

            self.assertEqual(
                [item.layer for item in items],
                ["pnt_pcd_enov_20260514"],
            )
            self.assertEqual(
                [item.xml_path.name for item in items],
                ["md_pcd_enov_20260514.xml"],
            )

    def test_discover_publish_items_uses_single_manifest_output_overrides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self._write_triplet(folder, "pnt_pcd_enov_20260514")
            self._write_manifest(folder, primary="pnt_pcd_enov_20260514")

            items = discover_publish_items(
                folder,
                store="store_custom",
                layer="layer_custom",
                style="style_custom",
                layer_title="Titulo Custom",
            )

            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].store, "store_custom")
            self.assertEqual(items[0].layer, "layer_custom")
            self.assertEqual(items[0].style, "style_custom")
            self.assertEqual(items[0].layer_title, "Titulo Custom")

    def test_metadata_title_reads_iso_title(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "md_test.xml"
            xml_path.write_text(self._metadata_xml("Titulo Teste"), encoding="utf-8")

            self.assertEqual(metadata_title(xml_path), "Titulo Teste")

    def test_geoserver_layer_title_for_ur_car_uses_utf8_accents(self):
        self.assertEqual(
            geoserver_layer_title("pol_pcd_ur_car_ac_20260514"),
            "Uso Restrito - Imóveis Acre",
        )

    def test_add_data_dictionary_link_replaces_placeholder(self):
        content = "<distribution>Estrutura de 2 link associado</distribution>"

        updated, inserted = add_data_dictionary_link(
            content,
            "https://etl/get_geonetwork_data_dict?key=uuid-teste",
        )

        self.assertTrue(inserted)
        self.assertIn(
            "https://etl/get_geonetwork_data_dict?key=uuid-teste",
            updated,
        )

    def test_metadata_xml_with_data_dictionary_link_writes_temporary_xml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "md_test.xml"
            xml_path.write_text(
                self._metadata_xml(
                    "Titulo Teste",
                    uuid="uuid-teste",
                    distribution_url="Estrutura de 2 link associado",
                ),
                encoding="utf-8",
            )

            upload_path, temporary = metadata_xml_with_data_dictionary_link(
                xml_path,
                "https://etl/get_geonetwork_data_dict",
            )

            try:
                self.assertTrue(temporary)
                self.assertNotEqual(upload_path, xml_path)
                self.assertIn(
                    "https://etl/get_geonetwork_data_dict?key=uuid-teste",
                    upload_path.read_text(encoding="utf-8"),
                )
            finally:
                upload_path.unlink(missing_ok=True)

    def test_set_data_dictionary_field_types_matches_sdb_aliases(self):
        xml = """
<metadata>
  <data_dictionary>
    <field>
      <name>cod_tema</name>
      <description>Codigo</description>
    </field>
  </data_dictionary>
</metadata>
"""

        updated, count = set_data_dictionary_field_types(
            xml,
            {"sdb_cod_tema": "String"},
        )

        self.assertEqual(count, 1)
        self.assertIn("<type>String</type>", updated)

    def test_data_dictionary_field_type_uses_unique_suffix(self):
        self.assertEqual(
            data_dictionary_field_type("cod_tema", {"acm_cod_tema": "Integer64"}),
            "Integer64",
        )

    def test_convert_geoserver_binding_maps_common_types(self):
        self.assertEqual(convert_geoserver_binding("java.lang.String"), "String")
        self.assertEqual(convert_geoserver_binding("java.lang.Long"), "Integer64")
        self.assertEqual(convert_geoserver_binding("java.lang.Double"), "Real")
        self.assertEqual(convert_geoserver_binding("java.sql.Timestamp"), "Date")

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

    def test_sld_content_type_uses_se_mime_for_sld_11(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sld_path = Path(temp_dir) / "style.sld"
            sld_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.1.0" xmlns:se="http://www.opengis.net/se">
  <NamedLayer><se:Name>layer</se:Name></NamedLayer>
</StyledLayerDescriptor>
""",
                encoding="utf-8",
            )

            self.assertEqual(sld_content_type(sld_path), "application/vnd.ogc.se+xml")

    def test_sld_content_type_uses_sld_mime_for_sld_10(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sld_path = Path(temp_dir) / "style.sld"
            sld_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0">
  <NamedLayer><Name>layer</Name></NamedLayer>
</StyledLayerDescriptor>
""",
                encoding="utf-8",
            )

            self.assertEqual(sld_content_type(sld_path), "application/vnd.ogc.sld+xml")

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

    def _write_manifest(self, folder, primary, quality_reports=None):
        outputs = [primary]
        manifest = {
            "primary_output": {
                "path": str(folder / f"{primary}.gpkg"),
                "role": "primary",
                "label": "principal",
            },
            "xml_files": [
                str(folder / f"{metadata_stem_for_data_stem(data_stem)}.xml")
                for data_stem in outputs
            ],
            "sld_files": [
                str(folder / f"{data_stem}.sld")
                for data_stem in outputs
            ],
            "quality_reports": quality_reports or {},
        }
        (folder / f"{primary}_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _metadata_xml(self, title, uuid="", distribution_url=""):
        identifier = ""
        if uuid:
            identifier = f"""
  <gmd:fileIdentifier>
    <gco:CharacterString>{uuid}</gco:CharacterString>
  </gmd:fileIdentifier>"""
        distribution = ""
        if distribution_url:
            distribution = f"""
  <gmd:distributionInfo>
    <gmd:MD_Distribution>
      <gmd:transferOptions>
        <gmd:MD_DigitalTransferOptions>
          <gmd:onLine>
            <gmd:CI_OnlineResource>
              <gmd:linkage>
                <gmd:URL>{distribution_url}</gmd:URL>
              </gmd:linkage>
            </gmd:CI_OnlineResource>
          </gmd:onLine>
        </gmd:MD_DigitalTransferOptions>
      </gmd:transferOptions>
    </gmd:MD_Distribution>
  </gmd:distributionInfo>"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco">
{identifier}
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
{distribution}
</gmd:MD_Metadata>
"""


if __name__ == "__main__":
    unittest.main()
