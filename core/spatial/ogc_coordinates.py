import math

from shapely.geometry import (
    GeometryCollection,
    LinearRing,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

from core.spatial.crs import is_geographic_crs, is_within_geographic_bounds
from core.spatial.ogc_results import add_error, new_validation_result


def validate_coordinate_ranges_for_crs(geom, crs, result, label=None):
    if geom is None:
        return

    try:
        if geom.is_empty:
            return
    except Exception:
        return

    current_label = label or geom.geom_type

    if isinstance(geom, (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)):
        validate_collection_coordinate_ranges(geom, crs, result)
        return

    if not is_geographic_crs(crs):
        return

    try:
        bounds = geom.bounds
    except Exception:
        add_error(
            result,
            f"{current_label}: nao foi possivel obter bounds para validar compatibilidade com o CRS {crs}.",
        )
        return

    if is_within_geographic_bounds(bounds):
        return

    minx, miny, maxx, maxy = bounds
    add_error(
        result,
        (
            f"{current_label}: bounds incompativeis com o CRS geografico {crs} "
            f"(minx={minx}, miny={miny}, maxx={maxx}, maxy={maxy})."
        ),
    )


def validate_collection_coordinate_ranges(geom, crs, result):
    for index, item in enumerate(geom.geoms, 1):
        validate_coordinate_ranges_for_crs(
            item,
            crs,
            result,
            label=f"{geom.geom_type}[{index}]",
        )


def is_finite_number(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def validate_coordinate_tuple(coord, label, result):
    if coord is None:
        add_error(result, f"{label}: coordenada nula.")
        return

    if len(coord) < 2:
        add_error(result, f"{label}: coordenada com dimensao insuficiente.")
        return

    for axis_index, axis_value in enumerate(coord):
        if axis_value is None:
            add_error(result, f"{label}: eixo {axis_index} com valor nulo.")
            continue
        if not is_finite_number(axis_value):
            add_error(result, f"{label}: eixo {axis_index} com valor invalido ({axis_value}).")


def validate_linestring_coords(coords, label, result, minimum_points=2, must_be_closed=False):
    if len(coords) < minimum_points:
        add_error(result, f"{label}: quantidade insuficiente de pontos ({len(coords)}).")

    for coord in coords:
        validate_coordinate_tuple(coord, label, result)

    distinct_points = {tuple(coord[:2]) for coord in coords if coord is not None and len(coord) >= 2}
    if len(distinct_points) < 2:
        add_error(result, f"{label}: precisa de pelo menos 2 pontos distintos.")

    if must_be_closed and coords and coords[0] != coords[-1]:
        add_error(result, f"{label}: anel nao esta fechado.")


def validate_polygon_coords(polygon, label, result):
    validate_linestring_coords(
        list(polygon.exterior.coords),
        f"{label} - anel externo",
        result,
        minimum_points=4,
        must_be_closed=True,
    )
    for ring_index, interior in enumerate(polygon.interiors, 1):
        validate_linestring_coords(
            list(interior.coords),
            f"{label} - buraco {ring_index}",
            result,
            minimum_points=4,
            must_be_closed=True,
        )


def validar_coordenadas(geom, crs=None):
    return validate_coordinates(geom, crs=crs)


def validate_coordinates(geom, crs=None):
    result = new_validation_result(geom)

    if geom is None:
        add_error(result, "Geometria nula.")
        return result
    if geom.is_empty:
        add_error(result, "Geometria vazia.")
        return result
    if isinstance(geom, Point):
        validate_coordinate_tuple(geom.coords[0], "Point", result)
        validate_coordinate_ranges_for_crs(geom, crs, result)
        return result
    if isinstance(geom, (LineString, LinearRing)):
        validate_linestring_coords(
            list(geom.coords),
            geom.geom_type,
            result,
            minimum_points=4 if isinstance(geom, LinearRing) else 2,
            must_be_closed=isinstance(geom, LinearRing),
        )
        validate_coordinate_ranges_for_crs(geom, crs, result)
        return result
    if isinstance(geom, Polygon):
        validate_polygon_coords(geom, "Polygon", result)
        validate_coordinate_ranges_for_crs(geom, crs, result)
        return result
    if isinstance(geom, (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)):
        if len(geom.geoms) == 0:
            add_error(result, f"{geom.geom_type} sem geometrias.")
        for index, item in enumerate(geom.geoms, 1):
            child_result = validate_coordinates(item, crs=crs)
            for error in child_result["erros"]:
                add_error(result, f"{geom.geom_type}[{index}]: {error}")
        return result

    add_error(result, f"Nao foi possivel validar coordenadas para {geom.geom_type}.")
    return result


__all__ = [
    "is_finite_number",
    "validar_coordenadas",
    "validate_collection_coordinate_ranges",
    "validate_coordinate_ranges_for_crs",
    "validate_coordinate_tuple",
    "validate_coordinates",
    "validate_linestring_coords",
    "validate_polygon_coords",
]
