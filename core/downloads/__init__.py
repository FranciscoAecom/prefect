from core.downloads.catalog import DOWNLOAD_TARGETS, DownloadTarget, get_download_target


def __getattr__(name):
    if name == "data_download_flow":
        from core.flow.downloads import data_download_flow

        return data_download_flow
    raise AttributeError(name)


__all__ = [
    "DOWNLOAD_TARGETS",
    "DownloadTarget",
    "data_download_flow",
    "get_download_target",
]
