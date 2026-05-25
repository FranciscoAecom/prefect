import shutil
import ssl
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


USER_AGENT = "data-pipeline-prefect/1.0"


def read_text_url(url, timeout=120):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout, context=insecure_ssl_context()) as response:
        return response.read().decode("utf-8")


def download_url(url, destination, validator=None):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False,
        dir=destination.parent,
        suffix=".part",
    ) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.close()
        if shutil.which("curl.exe"):
            download_with_curl(url, temp_path)
        else:
            download_with_urllib(url, temp_path)

    try:
        if validator:
            validator(temp_path, url)
        temp_path.replace(destination)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def download_with_urllib(url, destination):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=3600, context=insecure_ssl_context()) as response:
        with Path(destination).open("wb") as output:
            shutil.copyfileobj(response, output)


def download_with_curl(url, destination):
    arguments = [
        "curl.exe",
        "--insecure",
        "--ssl-no-revoke",
        "--fail-with-body",
        "--show-error",
        "--location",
        "--retry",
        "3",
        "--retry-delay",
        "10",
        "--connect-timeout",
        "60",
        "--max-time",
        "0",
        "--output",
        str(destination),
        url,
    ]
    result = subprocess.run(
        arguments,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = "\n".join(
            part.strip()
            for part in (result.stdout, result.stderr)
            if part and part.strip()
        )
        raise RuntimeError(f"curl.exe falhou ao baixar arquivo: {output}")


def insecure_ssl_context():
    return ssl._create_unverified_context()


__all__ = [
    "download_url",
    "download_with_curl",
    "download_with_urllib",
    "insecure_ssl_context",
    "read_text_url",
]
