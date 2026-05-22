from dataclasses import dataclass


@dataclass
class IngestRecord:
    sheet_row: int
    record_id: object
    theme: str
    theme_folder: str
    status: str
    source_path: str
    input_path: str
    rule_profile: str
    access_constraints: str = ""
    category_acronym: str = ""
    citation: str = ""
    date: str = ""
    output_dir: str = ""
    bronze_dir: str = ""
    temp_dir: str = ""
    id_geonetwork: str = ""
    abstract: str = ""
    use_constraints: str = ""
    data_classification: str = ""
    data_activity_classification: str = ""
    topic_category_code: str = ""
    spatial_representation_type_code: str = ""
    maintenance_frequency_code: str = ""
    maintenance_frequency_aecom: str = ""
    responsible_party: str = ""
    beginposition: str = ""
    endposition: str = ""
    source: str = ""
    reference_system: str = ""
    data_dictionary: str = ""
    metadata: str = ""
    methodologie: str = ""
    others: str = ""
    date_stamp: str = ""
    project: str = ""
    characterstring: str = ""


@dataclass
class IngestIssue:
    sheet_row: int
    record_id: object
    theme_folder: str
    status: str
    source_path: str
    reason: str


__all__ = ["IngestIssue", "IngestRecord"]
