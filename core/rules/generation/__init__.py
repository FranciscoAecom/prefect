from core.rules.generation.localidades import (
    LOCALIDADES_DOMAIN_COLUMNS,
    LOCALIDADES_RELATION_PAIRS,
    generate_localidades_domains,
    generate_localidades_relations,
)
from core.rules.generation.style import (
    build_categorized_sld_style,
    generate_categorized_style_from_domain,
)

__all__ = [
    "LOCALIDADES_DOMAIN_COLUMNS",
    "LOCALIDADES_RELATION_PAIRS",
    "build_categorized_sld_style",
    "generate_categorized_style_from_domain",
    "generate_localidades_domains",
    "generate_localidades_relations",
]
