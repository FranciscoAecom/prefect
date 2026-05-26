import argparse

from core.rules.generation.style import generate_categorized_style_from_domain


def main():
    parser = argparse.ArgumentParser(
        description="Gera style.json categorizado a partir de domains.json e uma tabela de paleta."
    )
    parser.add_argument("--rules-dir", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--palette", required=True)
    parser.add_argument("--output")
    parser.add_argument("--geometry", default="point", choices=["point", "line", "polygon"])
    parser.add_argument("--usage-column", default="uso_localidades")
    parser.add_argument("--default-color-value")
    parser.add_argument("--rule-name")
    args = parser.parse_args()

    style = generate_categorized_style_from_domain(
        rules_dir=args.rules_dir,
        field_name=args.field,
        palette_path=args.palette,
        output_path=args.output,
        geometry_kind=args.geometry,
        usage_column=args.usage_column,
        default_color_value=args.default_color_value,
        rule_name=args.rule_name,
    )
    rules = style["sld"]["rules"]
    output = args.output or f"{args.rules_dir}/style.json"
    print(f"style.json atualizado: {output}")
    print(f"  campo: {args.field}")
    print(f"  regras: {len(rules)}")


if __name__ == "__main__":
    main()
