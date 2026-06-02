from collections import Counter

import geopandas as gpd
import pandas as pd
from shapely import get_srid
from shapely.geometry import (
    GeometryCollection,
    MultiPolygon,
    Polygon,
)
from shapely.geometry.base import BaseGeometry
from shapely.ops import orient
from shapely.validation import explain_validity, make_valid

from core.spatial.crs import (
    geometry_series_matches_crs_coordinate_range,
)
from core.spatial.ogc_coordinates import (
    is_finite_number,
    validar_coordenadas,
    validate_collection_coordinate_ranges,
    validate_coordinate_ranges_for_crs,
    validate_coordinate_tuple,
    validate_coordinates,
    validate_linestring_coords,
    validate_polygon_coords,
)
from core.spatial.ogc_results import GEOMETRY_TYPES, add_error, new_validation_result
from core.spatial.repair import INTERNAL_SAFE_REPAIR_FLAG


def can_skip_detailed_ogc_check(gdf, crs_esperado=None, srid_esperado=None, normalizar=False):
    if normalizar or srid_esperado is not None or crs_esperado is not None:
        return False

    geometry = gdf.geometry
    if geometry is None:
        return False

    if geometry.isna().any() or geometry.is_empty.any():
        return False

    geom_types = set(geometry.geom_type.unique())
    if not geom_types.issubset(GEOMETRY_TYPES):
        return False

    coordinate_range_mask = geometry_series_matches_crs_coordinate_range(geometry, gdf.crs)
    if not bool(coordinate_range_mask.all()):
        return False

    return bool(geometry.is_valid.all())


def get_invalid_ogc_records(gdf, crs_esperado=None, srid_esperado=None, normalizar=False):
    if can_skip_detailed_ogc_check(
        gdf,
        crs_esperado=crs_esperado,
        srid_esperado=srid_esperado,
        normalizar=normalizar,
    ):
        return empty_invalid_ogc_gdf(gdf), 0, {}

    invalid_indices = []
    invalid_reasons = []
    error_counter = Counter()
    safe_repair_null_mask = safe_repair_null_geometry_mask(gdf)

    for idx, geom in gdf.geometry.items():
        reason_text, errors = validate_ogc_record_geometry(
            geom,
            gdf.crs,
            safe_repair_null_mask.loc[idx],
            srid_esperado=srid_esperado,
            crs_esperado=crs_esperado,
            normalizar=normalizar,
        )
        if not reason_text:
            continue

        invalid_indices.append(idx)
        invalid_reasons.append(reason_text)
        error_counter.update(errors)

    if not invalid_indices:
        return empty_invalid_ogc_gdf(gdf), 0, {}

    invalid_gdf = gdf.loc[invalid_indices].copy()
    invalid_gdf["ogc_motivo"] = invalid_reasons
    return invalid_gdf, len(invalid_gdf), dict(error_counter.most_common())


def safe_repair_null_geometry_mask(gdf):
    repair_flag_column = INTERNAL_SAFE_REPAIR_FLAG
    if repair_flag_column not in gdf.columns:
        return pd.Series(False, index=gdf.index)
    return gdf[repair_flag_column].fillna(False).astype(bool)


def empty_invalid_ogc_gdf(gdf):
    return gpd.GeoDataFrame(
        columns=list(gdf.columns) + ["ogc_motivo"],
        geometry="geometry",
        crs=gdf.crs,
    )


def validate_ogc_record_geometry(
    geom,
    crs,
    safe_repair_null,
    srid_esperado=None,
    crs_esperado=None,
    normalizar=False,
):
    if safe_repair_null:
        reason_text = "Geometria ficou nula apos tentativa de reparo seguro."
        return reason_text, [reason_text]

    resultado = validate_geometry(
        geom,
        crs=crs,
        expected_srid=srid_esperado,
        expected_crs=crs_esperado,
        normalize=normalizar,
    )
    if resultado["valido"]:
        return "", []
    return " | ".join(resultado["erros"]), resultado["erros"]


def validar_tipo(geom):
    result = new_validation_result(geom)

    if geom is None:
        add_error(result, "Geometria nula.")
        return result

    if not isinstance(geom, BaseGeometry):
        add_error(result, "Objeto informado nao e uma geometria Shapely.")
        return result

    if geom.geom_type not in GEOMETRY_TYPES:
        add_error(result, f"Tipo geometrico nao suportado: {geom.geom_type}.")

    return result


def validar_regras_topologicas(geom):
    return validate_topological_rules(geom)


def validate_topological_rules(geom):
    result = new_validation_result(geom)

    if geom is None:
        add_error(result, "Geometria nula.")
        return result

    if geom.is_empty:
        add_error(result, "Geometria vazia.")
        return result

    if not geom.is_valid:
        reason = explain_validity(geom)
        add_error(result, f"Geometria invalida segundo OGC: {reason}.")

    if isinstance(geom, Polygon):
        exterior_coords = list(geom.exterior.coords)
        if exterior_coords and exterior_coords[0] != exterior_coords[-1]:
            add_error(result, "Polygon: anel externo nao esta fechado.")

        for ring_index, interior in enumerate(geom.interiors, 1):
            interior_coords = list(interior.coords)
            if interior_coords and interior_coords[0] != interior_coords[-1]:
                add_error(result, f"Polygon: buraco {ring_index} nao esta fechado.")

    elif isinstance(geom, MultiPolygon):
        for index, polygon in enumerate(geom.geoms, 1):
            child_result = validar_regras_topologicas(polygon)
            for error in child_result["erros"]:
                add_error(result, f"MultiPolygon[{index}]: {error}")

    elif isinstance(geom, GeometryCollection):
        for index, item in enumerate(geom.geoms, 1):
            child_result = validar_regras_topologicas(item)
            for error in child_result["erros"]:
                add_error(result, f"GeometryCollection[{index}]: {error}")

    return result


def validar_srid_ou_crs(geom, crs=None, srid_esperado=None, crs_esperado=None):
    return validate_srid_or_crs(
        geom,
        crs=crs,
        expected_srid=srid_esperado,
        expected_crs=crs_esperado,
    )


def validate_srid_or_crs(geom, crs=None, expected_srid=None, expected_crs=None):
    result = new_validation_result(geom)

    if geom is None:
        add_error(result, "Geometria nula.")
        return result

    srid_atual = None
    try:
        srid_atual = get_srid(geom)
    except Exception:
        srid_atual = None

    if expected_srid is not None:
        if srid_atual in (None, 0):
            add_error(result, f"SRID ausente. Esperado: {expected_srid}.")
        elif srid_atual != expected_srid:
            add_error(
                result,
                f"SRID incompativel. Atual: {srid_atual}. Esperado: {expected_srid}."
            )

    if expected_crs is not None:
        if crs is None:
            add_error(result, f"CRS ausente. Esperado: {expected_crs}.")
        elif str(crs) != str(expected_crs):
            add_error(
                result,
                f"CRS incompativel. Atual: {crs}. Esperado: {expected_crs}."
            )

    return result


def normalizar_geometria(geom):
    return normalize_geometry(geom)


def normalize_geometry(geom):
    result = new_validation_result(geom)

    if geom is None:
        add_error(result, "Geometria nula.")
        return result

    normalized = geom

    try:
        if not normalized.is_valid:
            normalized = make_valid(normalized)
            result["normalizada"] = True
    except Exception as exc:
        add_error(result, f"Erro ao corrigir geometria com make_valid: {exc}")
        result["geometria"] = geom
        return result

    try:
        if isinstance(normalized, Polygon):
            normalized = orient(normalized, sign=1.0)
            result["normalizada"] = True
        elif isinstance(normalized, MultiPolygon):
            normalized = MultiPolygon([orient(poly, sign=1.0) for poly in normalized.geoms])
            result["normalizada"] = True
    except Exception as exc:
        result["avisos"].append(f"Nao foi possivel orientar aneis: {exc}")

    result["geometria"] = normalized
    return result


def validar_geometria(geom, crs=None, srid_esperado=None, crs_esperado=None, normalizar=False):
    return validate_geometry(
        geom,
        crs=crs,
        expected_srid=srid_esperado,
        expected_crs=crs_esperado,
        normalize=normalizar,
    )


def validate_geometry(
    geom,
    crs=None,
    expected_srid=None,
    expected_crs=None,
    normalize=False,
):
    resultado = new_validation_result(geom)
    geometria_avaliada = geom

    if normalize:
        normalizacao = normalize_geometry(geometria_avaliada)
        resultado["avisos"].extend(normalizacao["avisos"])
        resultado["erros"].extend(normalizacao["erros"])
        resultado["normalizada"] = normalizacao["normalizada"]
        geometria_avaliada = normalizacao["geometria"]
        resultado["geometria"] = geometria_avaliada

    validacoes = [
        validar_tipo(geometria_avaliada),
        validate_coordinates(geometria_avaliada, crs=crs),
        validate_topological_rules(geometria_avaliada),
        validate_srid_or_crs(
            geometria_avaliada,
            crs=crs,
            expected_srid=expected_srid,
            expected_crs=expected_crs,
        ),
    ]

    for parcial in validacoes:
        resultado["erros"].extend(parcial["erros"])
        resultado["avisos"].extend(parcial["avisos"])

    if resultado["erros"]:
        resultado["valido"] = False

    return resultado


def gerar_relatorio_erros(resultado):
    if not resultado:
        return "Resultado de validacao ausente."

    linhas = [
        f"Geometria: {resultado.get('tipo') or 'desconhecida'}",
        f"Valida: {'sim' if resultado.get('valido') else 'nao'}",
        f"Normalizada: {'sim' if resultado.get('normalizada') else 'nao'}",
    ]

    erros = resultado.get("erros", [])
    avisos = resultado.get("avisos", [])

    if erros:
        linhas.append("Erros:")
        for erro in erros:
            linhas.append(f"- {erro}")
    else:
        linhas.append("Erros: nenhum")

    if avisos:
        linhas.append("Avisos:")
        for aviso in avisos:
            linhas.append(f"- {aviso}")

    return "\n".join(linhas)


__all__ = [
    "GEOMETRY_TYPES",
    "add_error",
    "can_skip_detailed_ogc_check",
    "empty_invalid_ogc_gdf",
    "gerar_relatorio_erros",
    "get_invalid_ogc_records",
    "is_finite_number",
    "new_validation_result",
    "normalizar_geometria",
    "normalize_geometry",
    "safe_repair_null_geometry_mask",
    "validar_coordenadas",
    "validar_geometria",
    "validar_regras_topologicas",
    "validar_srid_ou_crs",
    "validar_tipo",
    "validate_coordinate_ranges_for_crs",
    "validate_coordinate_tuple",
    "validate_collection_coordinate_ranges",
    "validate_coordinates",
    "validate_geometry",
    "validate_linestring_coords",
    "validate_ogc_record_geometry",
    "validate_polygon_coords",
    "validate_srid_or_crs",
    "validate_topological_rules",
]
