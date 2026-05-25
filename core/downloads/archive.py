import zipfile
from pathlib import Path
from urllib.parse import urlsplit


def is_valid_zip(path):
    return zipfile.is_zipfile(path)


def validate_zip_download(path, url):
    if is_valid_zip(path):
        return
    sample = Path(path).read_text(encoding="utf-8", errors="replace")[:500].strip()
    message = "Download nao retornou um ZIP valido."
    if sample:
        message = f"{message} Inicio da resposta: {sample}"
    raise ValueError(f"{message} URL sem assinatura: {redact_signed_url(url)}")


def redact_signed_url(url):
    parsed = urlsplit(str(url))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


__all__ = ["is_valid_zip", "redact_signed_url", "validate_zip_download"]
