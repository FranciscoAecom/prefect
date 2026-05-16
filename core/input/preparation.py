from core.io.dataset import read_input_dataset
from core.ingest.dictionary import validate_theme_and_attributes
from core.transforms.attribute_transforms import clean_whitespace, normalize_columns
from core.utils import log


LEGACY_COLUMN_ALIASES = {
    "sdb_des_condic": "sdb_desc_condic",
    "acm_des_condic": "acm_desc_condic",
}


def log_dataset_overview(gdf):
    from core.processing.summary import log_dataset_overview as _log_dataset_overview

    return _log_dataset_overview(gdf)


def log_queue_summary(summary, issues):
    from core.queue.summary import log_queue_summary as _log_queue_summary

    return _log_queue_summary(summary, issues)


def log_dictionary_validation(record, input_attributes):
    result = validate_theme_and_attributes(record.theme, input_attributes)

    if not result["theme_found"]:
        log(
            f"Theme sem correspondencia na aba dictionaries: '{record.theme}'. "
            "Validacao estrutural nao executada."
        )
        return

    if not result["missing_attributes"] and not result["extra_attributes"]:
        log(
            f"Validacao dictionaries OK para theme '{result['dictionary_theme']}'. "
            "Estrutura do arquivo compativel com original_attribute_name."
        )
        return

    log(
        f"Divergencias estruturais encontradas para theme '{result['dictionary_theme']}'."
    )
    if result["missing_attributes"]:
        log(f"  Campos ausentes no arquivo: {', '.join(result['missing_attributes'])}")
    if result["extra_attributes"]:
        log(f"  Campos excedentes no arquivo: {', '.join(result['extra_attributes'])}")


def load_and_prepare_input(record):
    gdf = read_input_dataset(record.input_path)
    input_attributes = list(gdf.columns)
    log_dictionary_validation(record, input_attributes)

    gdf = normalize_columns(gdf)
    gdf = apply_legacy_column_aliases(gdf)
    gdf = clean_whitespace(gdf)
    return gdf


def apply_legacy_column_aliases(gdf):
    rename_map = {
        old_column: new_column
        for old_column, new_column in LEGACY_COLUMN_ALIASES.items()
        if old_column in gdf.columns and new_column not in gdf.columns
    }
    if rename_map:
        gdf = gdf.rename(columns=rename_map)
        log(
            "Aliases legados aplicados: "
            + ", ".join(f"{old}->{new}" for old, new in sorted(rename_map.items()))
        )
    return gdf
