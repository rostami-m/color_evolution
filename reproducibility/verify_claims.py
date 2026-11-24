"""Verify indexed claim values against the published numerical bundle."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def matches_subset(expected, actual):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and matches_subset(value, actual[key])
            for key, value in expected.items()
        )
    return expected == actual


def main():
    claims = json.loads((ROOT / "reproducibility/claims.json").read_text())["claims"]
    mapping = json.loads((ROOT / "reproducibility/claims_source_map.json").read_text())["map"]
    failures = []
    for claim in claims:
        actual = json.loads((ROOT / mapping[claim["source_file"]]).read_text())
        for part in claim["json_pointer"].strip("/").split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            actual = actual[int(part)] if isinstance(actual, list) else actual[part]
        expected = claim["value"]
        if claim["status"] == "derived_from_indexed_results":
            indices = expected["comparison_indices"]
            significant = [
                i for i in indices
                if actual[i]["summary"]["mean"] > 0 and actual[i]["q_BH"] < 0.05
            ]
            ok = (
                expected["n_architectures"] == len(indices)
                and expected["positive_BH_significant"] == len(significant)
                and expected["significant_indices"] == significant
            )
        else:
            ok = matches_subset(expected, actual)
        if not ok:
            failures.append(claim["id"])
    print(json.dumps({"claims_checked": len(claims), "failures": failures}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
