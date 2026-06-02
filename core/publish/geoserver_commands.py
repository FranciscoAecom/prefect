import core.publish.urls as urls


def curl_base_command(retry_delay="5"):
    return [
        "--fail-with-body",
        "--show-error",
        "--location",
        "--retry",
        "3",
        "--retry-delay",
        retry_delay,
        "--connect-timeout",
        "60",
        "--max-time",
        "0",
    ]


def data_upload_command(item, config, auth):
    return [
        *curl_base_command(retry_delay="10"),
        "--request",
        "PUT",
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        f"Content-Type: {item.data_content_type}",
        "--upload-file",
        str(item.data_path),
        urls.geoserver_data_upload_url(
            config.geoserver,
            config.workspace,
            item.data_endpoint,
            item.store,
            item.data_type,
        ),
    ]


def layer_title_command(item, config, auth):
    return [
        *curl_base_command(),
        "--request",
        "PUT",
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        "Content-Type: application/xml; charset=UTF-8",
        "--data-binary",
        "@-",
        urls.geoserver_layer_resource_url(
            config.geoserver,
            config.workspace,
            item.data_endpoint,
            item.store,
            item.layer_resource,
            item.layer,
        ),
    ]


def style_create_command(item, config, auth, upload_sld, content_type):
    return [
        *curl_base_command(),
        "--request",
        "POST",
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        f"Content-Type: {content_type}",
        "--data-binary",
        f"@{upload_sld}",
        urls.geoserver_style_collection_url(config.geoserver, config.workspace, item.style),
    ]


def style_update_command(item, config, auth, upload_sld, content_type):
    return [
        *curl_base_command(),
        "--request",
        "PUT",
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        f"Content-Type: {content_type}",
        "--data-binary",
        f"@{upload_sld}",
        urls.geoserver_style_url(config.geoserver, config.workspace, item.style),
    ]


def default_style_command(item, config, auth):
    return [
        *curl_base_command(),
        "--request",
        "PUT",
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        "Content-Type: application/json",
        "--data-binary",
        "@-",
        urls.geoserver_layer_url(config.geoserver, config.workspace, item.layer),
    ]


def feature_type_command(item, config, auth):
    return [
        *curl_base_command(),
        "--header",
        f"Authorization: Basic {auth}",
        "--header",
        "Accept: application/json",
        urls.geoserver_feature_type_url(config.geoserver, config.workspace, item.store, item.layer),
    ]


__all__ = [
    "curl_base_command",
    "data_upload_command",
    "default_style_command",
    "feature_type_command",
    "layer_title_command",
    "style_create_command",
    "style_update_command",
]
