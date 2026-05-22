from urllib.parse import quote


def join_url_path(base_url, *segments):
    url = str(base_url).rstrip("/")
    for segment in segments:
        url += "/" + quote(str(segment).strip("/"), safe=":")
    return url


def geoserver_data_upload_url(geoserver, workspace, data_endpoint, store, data_type):
    return (
        join_url_path(
            geoserver,
            "rest",
            "workspaces",
            workspace,
            data_endpoint,
            store,
            f"file.{data_type}",
        )
        + "?configure=all"
    )


def geoserver_layer_resource_url(
    geoserver,
    workspace,
    data_endpoint,
    store,
    layer_resource,
    layer,
):
    return join_url_path(
        geoserver,
        "rest",
        "workspaces",
        workspace,
        data_endpoint,
        store,
        layer_resource,
        layer,
    )


def geoserver_style_collection_url(geoserver, workspace, style):
    return (
        join_url_path(geoserver, "rest", "workspaces", workspace, "styles")
        + f"?name={quote(style)}&raw=true"
    )


def geoserver_style_url(geoserver, workspace, style):
    return (
        join_url_path(geoserver, "rest", "workspaces", workspace, "styles", style)
        + "?raw=true"
    )


def geoserver_layer_url(geoserver, workspace, layer):
    return join_url_path(geoserver, "rest", "layers", f"{workspace}:{layer}")


def geoserver_layer_json_url(geoserver, workspace, layer):
    return geoserver_layer_url(geoserver, workspace, layer) + ".json"


def geoserver_feature_type_url(geoserver, workspace, store, layer):
    return (
        join_url_path(
            geoserver,
            "rest",
            "workspaces",
            workspace,
            "datastores",
            store,
            "featuretypes",
            layer,
        )
        + ".json"
    )


def geonetwork_me_url(catalog):
    return join_url_path(catalog, "srv", "api", "me")


def geonetwork_records_import_query(catalog_group, catalog_category):
    return "&".join(
        [
            "metadataType=METADATA",
            "uuidProcessing=OVERWRITE",
            f"group={quote(str(catalog_group))}",
            f"category={quote(str(catalog_category))}",
            "rejectIfInvalid=false",
            "publishToAll=true",
            "transformWith=_none_",
            "schema=iso19139",
            "allowEditGroupMembers=true",
        ]
    )


def geonetwork_records_import_urls(catalog, catalog_group, catalog_category):
    query = geonetwork_records_import_query(catalog_group, catalog_category)
    api_records = join_url_path(catalog, "srv", "api", "records")
    por_api_records = join_url_path(catalog, "srv", "por", "api", "records")
    return [
        f"{api_records}?{query}",
        f"{api_records}/?{query}",
        f"{por_api_records}?{query}",
        f"{por_api_records}/?{query}",
    ]


def geonetwork_legacy_import_urls(catalog):
    return [
        join_url_path(catalog, "srv", "por", "metadata.insert"),
        join_url_path(catalog, "srv", "por", "xml.metadata.insert"),
        join_url_path(catalog, "srv", "api", "0.1", "records"),
    ]
