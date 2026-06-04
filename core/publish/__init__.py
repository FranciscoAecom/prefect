from core.publish.config import PublishConfig, PublishCredentials, PublishOptions
from core.publish.metadata import discover_publish_items


def __getattr__(name):
    if name == "data_publish_flow":
        from core.flow.publish import data_publish_flow

        return data_publish_flow
    if name == "data_pipeline_publish_flow":
        from core.flow.pipeline_publish import data_pipeline_publish_flow

        return data_pipeline_publish_flow
    raise AttributeError(name)

__all__ = [
    "PublishConfig",
    "PublishCredentials",
    "PublishOptions",
    "data_publish_flow",
    "data_pipeline_publish_flow",
    "discover_publish_items",
]
