import argparse
import glob
from pathlib import Path

from core.rules.generation.localidades import (
    generate_localidades_domains,
    generate_localidades_relations,
)
from core.rules.engine import invalidate_rule_profile_cache


DEFAULT_DOMAINS_SOURCE = r"C:\Temp\Reposit*\explorer\teste.xlsx"
DEFAULT_RELATIONS_SOURCE = (
    r"L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data\temp"
    r"\localidade\Localidades_Brasil_gpkg\BR_localidades_2022.gpkg"
)
DEFAULT_RULES_DIR = Path("rules/localidades/localidades")
DEFAULT_PROFILE_NAME = "localidades/localidades"


def main():
    parser = argparse.ArgumentParser(
        description="Regenera domains.json e relations.json da base localidades."
    )
    parser.add_argument("--domains-source", default=DEFAULT_DOMAINS_SOURCE)
    parser.add_argument("--relations-source", default=DEFAULT_RELATIONS_SOURCE)
    parser.add_argument("--rules-dir", default=str(DEFAULT_RULES_DIR))
    parser.add_argument("--profile", default=DEFAULT_PROFILE_NAME)
    args = parser.parse_args()

    rules_dir = Path(args.rules_dir)
    domain_summary = generate_localidades_domains(
        resolve_source_path(args.domains_source),
        rules_dir / "domains.json",
    )
    print("domains.json atualizado")
    for field, counts in domain_summary.items():
        print(
            f"  {field}: accepted_values={counts['accepted_values']} "
            f"aliases={counts['aliases']}"
        )
    invalidate_rule_profile_cache(args.profile)

    relation_summary = generate_localidades_relations(
        resolve_source_path(args.relations_source),
        rules_dir / "relations.json",
        args.profile,
    )
    print("relations.json atualizado")
    for relation, count in relation_summary["relations"].items():
        ambiguous_count = relation_summary["ambiguous"].get(relation, 0)
        print(f"  {relation}: relations={count} ambiguous={ambiguous_count}")


def resolve_source_path(value):
    if "*" not in str(value):
        return value
    matches = [Path(match) for match in glob.glob(str(value))]
    if not matches:
        raise FileNotFoundError(f"Nenhum arquivo encontrado para: {value}")
    return matches[0]


if __name__ == "__main__":
    main()
