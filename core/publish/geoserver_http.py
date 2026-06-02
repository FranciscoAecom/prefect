import base64
import subprocess

from core.utils import log


def basic_auth(username, password):
    token = f"{username}:{password}".encode("ascii")
    return base64.b64encode(token).decode("ascii")


def run_curl(arguments, dry_run=False, capture=False):
    arguments = add_windows_schannel_ssl_option(arguments)
    log("curl.exe " + " ".join(mask_sensitive_arguments(arguments)))
    if dry_run:
        log("DRY-RUN: curl.exe nao executado.")
        return ""
    result = subprocess.run(
        ["curl.exe", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(f"curl.exe falhou com exit code {result.returncode}: {output}")
    return result.stdout if capture else ""


def run_curl_with_stdin(arguments, stdin_text, dry_run=False):
    arguments = add_windows_schannel_ssl_option(arguments)
    log("curl.exe " + " ".join(mask_sensitive_arguments(arguments)))
    if dry_run:
        log("DRY-RUN: curl.exe nao executado.")
        return
    result = subprocess.run(
        ["curl.exe", *arguments],
        input=str(stdin_text).encode("utf-8"),
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        output = (result.stdout or b"") + (result.stderr or b"")
        output = output.decode("utf-8", errors="replace")
        raise RuntimeError(f"curl.exe falhou com exit code {result.returncode}: {output}")


def mask_sensitive_arguments(arguments):
    masked = []
    skip_next = False
    for index, argument in enumerate(arguments):
        if skip_next:
            skip_next = False
            continue
        if argument == "--header" and index + 1 < len(arguments):
            next_arg = arguments[index + 1]
            if next_arg.startswith(("Authorization: Basic ", "X-XSRF-TOKEN: ")):
                header_name = next_arg.split(":", 1)[0]
                masked.extend(["--header", f"{header_name}: ***"])
                skip_next = True
                continue
        masked.append(str(argument))
    return masked


def add_windows_schannel_ssl_option(arguments):
    if "--ssl-no-revoke" in arguments:
        return arguments
    if not any(str(argument).lower().startswith("https://") for argument in arguments):
        return arguments
    return ["--ssl-no-revoke", *arguments]


__all__ = [
    "add_windows_schannel_ssl_option",
    "basic_auth",
    "mask_sensitive_arguments",
    "run_curl",
    "run_curl_with_stdin",
]
