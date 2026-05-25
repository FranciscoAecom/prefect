import re


def geoserver_layer_title(layer_name):
    title_builders = (
        app_car_layer_title,
        sa_car_layer_title,
        ur_car_layer_title,
        autos_infracao_layer_title,
        imb_lulc_layer_title,
    )
    for builder in title_builders:
        title = builder(layer_name)
        if title:
            return title
    return ""


def state_name_from_layer(layer_name):
    state_names = {
        "ac": "Acre",
        "al": "Alagoas",
        "am": "Amazonas",
        "ap": "Amap\u00e1",
        "ba": "Bahia",
        "ce": "Cear\u00e1",
        "df": "Distrito Federal",
        "es": "Esp\u00edrito Santo",
        "go": "Goi\u00e1s",
        "ma": "Maranh\u00e3o",
        "mg": "Minas Gerais",
        "ms": "Mato Grosso do Sul",
        "mt": "Mato Grosso",
        "pa": "Par\u00e1",
        "pb": "Para\u00edba",
        "pe": "Pernambuco",
        "pi": "Piau\u00ed",
        "pr": "Paran\u00e1",
        "rj": "Rio de Janeiro",
        "rn": "Rio Grande do Norte",
        "ro": "Rond\u00f4nia",
        "rr": "Roraima",
        "rs": "Rio Grande do Sul",
        "sc": "Santa Catarina",
        "se": "Sergipe",
        "sp": "S\u00e3o Paulo",
        "to": "Tocantins",
    }
    parts = str(layer_name).split("_")
    if len(parts) >= 2 and len(parts[-2]) == 2 and parts[-1].isdigit():
        return state_names.get(parts[-2].lower(), "")
    return ""


def app_car_layer_title(layer_name):
    if not str(layer_name).startswith("pol_pcd_app_car_"):
        return ""
    state_name = state_name_from_layer(layer_name)
    if not state_name:
        return ""
    return f"\u00c1rea de Preserva\u00e7\u00e3o Permanente - Im\u00f3veis {state_name}"


def sa_car_layer_title(layer_name):
    if not str(layer_name).startswith("pol_pcd_sa_car_"):
        return ""
    state_name = state_name_from_layer(layer_name)
    return f"Servid\u00e3o Administrativa - Im\u00f3veis {state_name}" if state_name else ""


def ur_car_layer_title(layer_name):
    if not str(layer_name).startswith("pol_pcd_ur_car_"):
        return ""
    state_name = state_name_from_layer(layer_name)
    return f"Uso Restrito - Im\u00f3veis {state_name}" if state_name else ""


def autos_infracao_layer_title(layer_name):
    layer_name = str(layer_name)
    if layer_name.startswith("pnt_pcd_enov_bbox_brasil_"):
        return "Autos de Infra\u00e7\u00e3o - BBox Brasil"
    if layer_name.startswith("pnt_pcd_enov_"):
        return "Autos de Infra\u00e7\u00e3o"
    return ""


def imb_lulc_layer_title(layer_name):
    match = re.match(r"^rst_imb_lulc_(\d{4})(\d*)$", str(layer_name))
    if not match:
        return ""
    year, suffix = match.groups()
    collection_match = re.match(r"^\d{3}", suffix or "")
    if collection_match:
        collection = int(collection_match.group(0))
        return f"Uso e cobertura da terra de {year} - Cole\u00e7\u00e3o {collection}"
    return f"Uso e cobertura da terra de {year}"


__all__ = [
    "app_car_layer_title",
    "autos_infracao_layer_title",
    "geoserver_layer_title",
    "imb_lulc_layer_title",
    "sa_car_layer_title",
    "state_name_from_layer",
    "ur_car_layer_title",
]
