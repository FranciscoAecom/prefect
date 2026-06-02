GEOMETRY_TYPES = {
    "Point",
    "LineString",
    "LinearRing",
    "Polygon",
    "MultiPoint",
    "MultiLineString",
    "MultiPolygon",
    "GeometryCollection",
}


def new_validation_result(geom):
    return {
        "valido": True,
        "tipo": getattr(geom, "geom_type", None),
        "erros": [],
        "avisos": [],
        "normalizada": False,
        "geometria": geom,
    }


def add_error(result, message):
    result["valido"] = False
    result["erros"].append(message)


__all__ = ["GEOMETRY_TYPES", "add_error", "new_validation_result"]
