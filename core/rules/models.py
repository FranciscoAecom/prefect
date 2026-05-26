from dataclasses import dataclass, field

from core.rules.contracts import PIPELINE_COMPONENT_KEYS, PROFILE_DATA_KEYS


@dataclass(frozen=True)
class InputColumnRule:
    dtype: str = "string"
    required: bool = True
    nullable: bool = True

    @classmethod
    def from_json(cls, raw_rule):
        if isinstance(raw_rule, str):
            return cls(dtype=raw_rule)
        return cls(
            dtype=raw_rule.get("dtype", "string"),
            required=raw_rule.get("required", True),
            nullable=raw_rule.get("nullable", True),
        )

    def to_json(self):
        return {
            "dtype": self.dtype,
            "required": self.required,
            "nullable": self.nullable,
        }


@dataclass(frozen=True)
class InputSchemaModel:
    columns: dict[str, InputColumnRule] = field(default_factory=dict)
    require_geometry: bool = True
    allow_extra_columns: bool = True

    @classmethod
    def from_json(cls, data):
        data = data or {}
        return cls(
            columns={
                column: InputColumnRule.from_json(rule)
                for column, rule in data.get("columns", {}).items()
            },
            require_geometry=data.get("require_geometry", True),
            allow_extra_columns=data.get("allow_extra_columns", True),
        )

    def to_json(self):
        return {
            "columns": {
                column: rule.to_json()
                for column, rule in self.columns.items()
            },
            "require_geometry": self.require_geometry,
            "allow_extra_columns": self.allow_extra_columns,
        }


@dataclass(frozen=True)
class DomainFieldModel:
    accepted_values: list[str] = field(default_factory=list)
    aliases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data):
        data = data or {}
        return cls(
            accepted_values=list(data.get("accepted_values", []) or []),
            aliases=dict(data.get("aliases", {}) or {}),
        )

    def to_json(self):
        return {
            "accepted_values": list(self.accepted_values),
            "aliases": dict(self.aliases),
        }


@dataclass(frozen=True)
class RuleProfileModel:
    metadata: dict = field(default_factory=dict)
    input_schema: InputSchemaModel = field(default_factory=InputSchemaModel)
    fields: dict[str, DomainFieldModel] = field(default_factory=dict)
    relations: dict[str, dict[str, str]] = field(default_factory=dict)
    auto_functions: dict[str, list[str]] = field(default_factory=dict)
    postprocess_functions: list[str] = field(default_factory=list)
    primary_output: dict = field(default_factory=dict)
    quality_outputs: dict = field(default_factory=dict)
    secondary_outputs: list[str] = field(default_factory=list)
    sld: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, profile):
        profile = dict(profile or {})
        metadata = {
            key: value
            for key, value in profile.items()
            if key not in PROFILE_DATA_KEYS
        }
        return cls(
            metadata=metadata,
            input_schema=InputSchemaModel.from_json(profile.get("input_schema", {})),
            fields={
                column: DomainFieldModel.from_json(raw_field)
                for column, raw_field in (profile.get("fields", {}) or {}).items()
            },
            relations={
                name: dict(mapping)
                for name, mapping in (profile.get("relations", {}) or {}).items()
            },
            auto_functions={
                column: list(functions)
                for column, functions in (profile.get("auto_functions", {}) or {}).items()
            },
            postprocess_functions=list(profile.get("postprocess_functions", []) or []),
            primary_output=dict(profile.get("primary_output", {}) or {}),
            quality_outputs=dict(profile.get("quality_outputs", {}) or {}),
            secondary_outputs=list(profile.get("secondary_outputs", []) or []),
            sld=dict(profile.get("sld", {}) or {}),
        )

    @classmethod
    def from_components(cls, profile, input_schema, domains, relations, pipeline, style=None):
        data = dict(profile or {})
        if input_schema:
            data["input_schema"] = input_schema
        data["fields"] = (domains or {}).get("fields", domains or {})
        data["relations"] = (relations or {}).get("relations", relations or {})
        data["auto_functions"] = (pipeline or {}).get("auto_functions", pipeline or {})
        data["postprocess_functions"] = (pipeline or {}).get("postprocess_functions", [])
        data["primary_output"] = (pipeline or {}).get("primary_output", {})
        data["quality_outputs"] = (pipeline or {}).get("quality_outputs", {})
        data["secondary_outputs"] = (pipeline or {}).get("secondary_outputs", [])
        data["sld"] = (style or {}).get("sld", style or {})
        return cls.from_dict(data)

    def to_dict(self, include_empty_input_schema=True):
        data = dict(self.metadata)
        input_schema_data = self.input_schema.to_json()
        if include_empty_input_schema or input_schema_data["columns"]:
            data["input_schema"] = input_schema_data
        data["fields"] = {
            column: field_rule.to_json()
            for column, field_rule in self.fields.items()
        }
        data["relations"] = {
            name: dict(mapping)
            for name, mapping in self.relations.items()
        }
        data["auto_functions"] = {
            column: list(functions)
            for column, functions in self.auto_functions.items()
        }
        data["postprocess_functions"] = list(self.postprocess_functions)
        if self.primary_output:
            data["primary_output"] = dict(self.primary_output)
        if self.quality_outputs:
            data["quality_outputs"] = dict(self.quality_outputs)
        data["secondary_outputs"] = list(self.secondary_outputs)
        if self.sld:
            data["sld"] = dict(self.sld)
        return data

    def to_components(self):
        pipeline = {
            "auto_functions": {
                column: list(functions)
                for column, functions in self.auto_functions.items()
            },
            "postprocess_functions": list(self.postprocess_functions),
            "primary_output": dict(self.primary_output),
            "quality_outputs": dict(self.quality_outputs),
            "secondary_outputs": list(self.secondary_outputs),
        }
        pipeline = {
            key: value
            for key, value in pipeline.items()
            if key in PIPELINE_COMPONENT_KEYS
        }
        return (
            dict(self.metadata),
            self.input_schema.to_json(),
            {
                "fields": {
                    column: field_rule.to_json()
                    for column, field_rule in self.fields.items()
                }
            },
            {
                "relations": {
                    name: dict(mapping)
                    for name, mapping in self.relations.items()
                }
            },
            pipeline,
            {"sld": dict(self.sld)} if self.sld else {},
        )
