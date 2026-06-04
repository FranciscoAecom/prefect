import unittest

from projects.configs import (
    DEFAULT_PROJECT_CONFIG,
    canonical_project_name,
    get_project_config,
    resolve_project_config,
    resolve_project_name,
)


class ProjectConfigsTests(unittest.TestCase):
    def test_resolve_project_name_by_theme_prefix(self):
        self.assertEqual(
            resolve_project_name("app_car_ac"),
            "car_area_preservacao_permanente",
        )
        self.assertEqual(resolve_project_name("rl_car_sp"), "car_reserva_legal")
        self.assertEqual(resolve_project_name("estado"), "estado")
        self.assertEqual(resolve_project_name("auth_supn"), "autorizacao_para_supressao_vegetal")

    def test_resolve_project_name_falls_back_to_default(self):
        self.assertEqual(resolve_project_name("tema_desconhecido"), DEFAULT_PROJECT_CONFIG["project_name"])
        self.assertEqual(resolve_project_name(None), DEFAULT_PROJECT_CONFIG["project_name"])

    def test_resolve_project_config_returns_expected_template(self):
        config = resolve_project_config("rl_car_sp")
        self.assertEqual(config["project_name"], "car_reserva_legal")
        self.assertEqual(config["output_name_template"], "pol_pcd_{theme_folder}_{date_yyyymmdd}")

    def test_legacy_project_names_resolve_to_canonical_projects(self):
        self.assertEqual(canonical_project_name("app_car"), "car_area_preservacao_permanente")
        self.assertEqual(canonical_project_name("reserva_legal_car"), "car_reserva_legal")
        self.assertEqual(canonical_project_name("sa_car"), "car_servidao_administrativa")
        self.assertEqual(canonical_project_name("ur_car"), "car_uso_restrito")
        self.assertEqual(get_project_config("reserva_legal_car")["project_name"], "car_reserva_legal")

    def test_resolve_autos_infracao_project_config(self):
        config = resolve_project_config("autos_infracao")

        self.assertEqual(resolve_project_name("autos_infracao"), "autos_infracao")
        self.assertEqual(resolve_project_name("enov"), "autos_infracao")
        self.assertEqual(config["project_name"], "autos_infracao")
        self.assertEqual(config["theme_prefixes"], ("enov",))
        self.assertEqual(config["output_name_template"], "pnt_pcd_enov_{date_yyyymmdd}")

    def test_get_project_config_unknown_returns_default_copy(self):
        config = get_project_config("nao_existe")
        self.assertEqual(config["project_name"], "default")
        self.assertIsNone(config["reference_date"])

    def test_resolve_degradacao_amazonia_project_config(self):
        config = resolve_project_config("degradacao_amazonia")

        self.assertEqual(resolve_project_name("degradacao_amazonia"), "degradacao_amazonia")
        self.assertEqual(resolve_project_name("degradacao"), "degradacao_amazonia")
        self.assertEqual(config["project_name"], "degradacao_amazonia")
        self.assertEqual(config["theme_prefixes"], ("dfaab",))
        self.assertEqual(config["output_name_template"], "pol_dfaab_imb_{date_yyyymmdd}")

    def test_resolve_raster_project_config(self):
        config = resolve_project_config("raster_precipitacao")

        self.assertEqual(resolve_project_name("raster_precipitacao"), "raster")
        self.assertEqual(config["project_name"], "raster")
        self.assertEqual(config["output_name_template"], "{input_stem}_wgs84_lzw")
