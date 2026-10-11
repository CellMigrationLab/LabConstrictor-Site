"""What an app's manifest leaves out. Missing facts never unlist an app: each one is a line in build/problems.md under "Warnings"
and, on the app page, a visible "Not stated"."""

from .config import RECOMMENDED, SCIENTIFIC_KINDS


def missing(manifest: dict, section: str, license_id: str | None) -> list[str]:
    """The recommended facts this manifest lacks, as short phrases for build/problems.md (nothing for apps kept apart as testing apps)."""
    if section == "testing":
        return []
    lacking = [field for field in RECOMMENDED if field not in manifest]
    if manifest["kind"] in SCIENTIFIC_KINDS:
        lacking += [field for field in ("inputs", "outputs") if field not in manifest]
    if license_id is None:
        lacking.append("license")
    return [f"no {field} in the manifest (the page says Not stated or leaves it out)" for field in lacking]
