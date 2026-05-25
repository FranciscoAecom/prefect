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
    detail = classify_invalid_download_response(sample)
    if detail:
        message = f"{message} Diagnostico: {detail}."
    if sample:
        message = f"{message} Inicio da resposta: {sample}"
    raise ValueError(f"{message} URL sem assinatura: {redact_signed_url(url)}")


def classify_invalid_download_response(sample):
    text = str(sample or "").lower()
    if not text:
        return "arquivo vazio"
    if "<html" in text or "<!doctype html" in text:
        if "certificate error" in text:
            return "a fonte retornou uma pagina HTML de erro de certificado/proxy"
        if "login" in text:
            return "a fonte retornou uma pagina HTML de login/autenticacao"
        return "a fonte retornou HTML em vez de ZIP"
    if "accessdenied" in text or "access denied" in text:
        return "acesso negado pela fonte"
    if "expired" in text and "signature" in text:
        return "URL assinada expirada"
    return ""


def redact_signed_url(url):
    parsed = urlsplit(str(url))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


__all__ = [
    "classify_invalid_download_response",
    "is_valid_zip",
    "redact_signed_url",
    "validate_zip_download",
]
