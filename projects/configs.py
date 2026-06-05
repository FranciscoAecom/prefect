from functools import lru_cache


DEFAULT_PROJECT_CONFIG = {
    "project_name": "default",
    "theme_prefixes": (),
    "output_name_template": "{input_stem}_validado",
    "reference_date": None,
}


PROJECT_CONFIGS = {
    "car_area_preservacao_permanente": {
        "project_name": "car_area_preservacao_permanente",
        "display_name": "Areas de Preservacao Permanentes (APP) nos imoveis rurais",
        "theme_prefixes": ("app_car_",),
        "output_name_template": "pol_pcd_{theme_folder}_{date_yyyymmdd}",
        "reference_date": "20260301",
    },
    "estado": {
        "project_name": "estado",
        "display_name": "Limites das unidades da federacao do Brasil",
        "theme_prefixes": ("estado",),
        "output_name_template": "pol_loc_sta_{date_yyyymmdd}",
        "reference_date": "20241215",
    },
    "localidades": {
        "project_name": "localidades",
        "display_name": "Localidades do Brasil",
        "theme_prefixes": ("loc",),
        "output_name_template": "pnt_loc_loc_br_{date_yyyymmdd}",
        "reference_date": "20251119",
    },
    "setor_censitario": {
        "project_name": "setor_censitario",
        "display_name": "Setores censitarios do Brasil",
        "theme_prefixes": ("setor_censitario",),
        "output_name_template": "pol_loc_cse_{date_yyyymmdd}",
        "reference_date": "20241114",
    },
    "car_reserva_legal": {
        "project_name": "car_reserva_legal",
        "display_name": "Reserva Legal (RL) nos imoveis rurais",
        "theme_prefixes": ("rl_car_",),
        "output_name_template": "pol_pcd_{theme_folder}_{date_yyyymmdd}",
        "reference_date": "20260301",
    },
    "car_servidao_administrativa": {
        "project_name": "car_servidao_administrativa",
        "display_name": "CAR de Servidao Administrativa",
        "theme_prefixes": ("sa_car_",),
        "output_name_template": "pol_pcd_{theme_folder}_{date_yyyymmdd}",
        "reference_date": "20260301",
    },
    "car_uso_restrito": {
        "project_name": "car_uso_restrito",
        "display_name": "Area de Uso Restrito nos imoveis rurais",
        "theme_prefixes": ("ur_car_",),
        "output_name_template": "pol_pcd_{theme_folder}_{date_yyyymmdd}",
        "reference_date": "20260514",
    },
    "autorizacao_para_supressao_vegetal": {
        "project_name": "autorizacao_para_supressao_vegetal",
        "display_name": "Autorizacao para Supressao Vegetal",
        "theme_prefixes": ("auth_supn",),
        "output_name_template": "pol_env_auth_supn_{date_yyyymmdd}",
        "reference_date": "20250701",
    },
    "autos_infracao": {
        "project_name": "autos_infracao",
        "display_name": "Autos de infracao ambiental",
        "theme_prefixes": ("enov",),
        "output_name_template": "pnt_pcd_enov_{date_yyyymmdd}",
        "reference_date": "20260514",
    },
    "degradacao_amazonia": {
        "project_name": "degradacao_amazonia",
        "display_name": "Degradacao da Amazonia",
        "theme_prefixes": ("dfaab",),
        "output_name_template": "pol_dfaab_imb_{date_yyyymmdd}",
        "reference_date": None,
    },
}


LEGACY_PROJECT_ALIASES = {
    "app_car": "car_area_preservacao_permanente",
    "reserva_legal_car": "car_reserva_legal",
    "sa_car": "car_servidao_administrativa",
    "ur_car": "car_uso_restrito",
    "degradacao": "degradacao_amazonia",
}


def canonical_project_name(project_name=None):
    project_name_text = str(project_name or "").strip().lower()
    return LEGACY_PROJECT_ALIASES.get(project_name_text, project_name_text)


@lru_cache(maxsize=None)
def get_project_config(project_name=None):
    canonical_name = canonical_project_name(project_name)
    if canonical_name and canonical_name in PROJECT_CONFIGS:
        config = dict(DEFAULT_PROJECT_CONFIG)
        config.update(PROJECT_CONFIGS[canonical_name])
        return config
    return dict(DEFAULT_PROJECT_CONFIG)


def resolve_project_name(theme_folder):
    theme_folder_text = str(theme_folder or "").strip().lower()
    theme_folder_text = canonical_project_name(theme_folder_text)
    if theme_folder_text in PROJECT_CONFIGS:
        return theme_folder_text
    for project_name, config in PROJECT_CONFIGS.items():
        for prefix in config.get("theme_prefixes", ()):
            if theme_folder_text.startswith(str(prefix).lower()):
                return project_name
    return DEFAULT_PROJECT_CONFIG["project_name"]


def resolve_project_config(theme_folder):
    project_name = resolve_project_name(theme_folder)
    return get_project_config(project_name)
