def parse_cors_origins(v: str | list[str]) -> list[str]:
    if isinstance(v, str):
        return [o.strip() for o in v.split(",") if o.strip()]
    return v
