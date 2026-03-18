def validate_required_fields(record: dict, required_fields: list[str]) -> list[str]:
    return [field for field in required_fields if field not in record or record[field] in (None, "")]
