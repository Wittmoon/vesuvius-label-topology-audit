"""Recheck three recorded scroll cases without modifying source labels."""

import argparse
import contextlib
import csv
import hashlib
import json
import math
from pathlib import Path
import time

from vesuvius.image_proc.run import label_topology_audit as lta


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    packet = Path(__file__).resolve().parents[1]
    with (packet / "data/kaggle_audit_all.csv").open() as stream:
        baseline = {row["crop"]: row for row in csv.DictReader(stream)}
    results = []
    for name in ["sample_00226", "sample_00340", "sample_00173"]:
        label = args.data_root / "labels" / f"{name}.tif"
        image = args.data_root / "images" / f"{name}.tif"
        output = args.out / name
        output.mkdir(parents=True, exist_ok=True)
        command = ["--label", str(label), "--out", str(output), "--hole-masks"]
        inputs = {str(label): sha256(label)}
        if args.plot:
            command += ["--image", str(image), "--plot"]
            inputs[str(image)] = sha256(image)
        if name == "sample_00340":
            after = args.data_root / "fix/2d_hole_fill/after" / f"{name}.tif"
            command += ["--after", str(after)]
            inputs[str(after)] = sha256(after)
        started = time.perf_counter()
        with (output / "run.log").open("w") as stream:
            with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                exit_code = lta.main(command)
        assert exit_code == 0, (name, exit_code)
        metrics = json.loads((output / f"{name}.json").read_text())
        changes = {}
        for key, value in lta.flat(metrics).items():
            previous = float(baseline[name][key])
            if not math.isclose(previous, value, rel_tol=1e-12, abs_tol=1e-12):
                changes[key] = [previous, value]
        assert all(key.startswith("thick_") for key in changes), (name, changes)
        delta = None
        if name == "sample_00340":
            delta = json.loads((output / f"{name}.delta.json").read_text())
            assert delta["b1_total_big"] == [13, 0], delta["b1_total_big"]
        results.append({
            "crop": name, "input_sha256": inputs, "cli_arguments": command,
            "exit_code": exit_code, "seconds": time.perf_counter() - started,
            "b1_total_big": metrics["b1_total_big"],
            "non_thickness_metrics_match_recorded_run": True,
            "changed_metrics": changes,
            "repair_b1_before_after": delta["b1_total_big"] if delta else None,
        })
        for source, digest in inputs.items():
            assert sha256(Path(source)) == digest, source
        print(json.dumps(results[-1]), flush=True)
    report = {
        "review_date": "2026-10-18", "cases": results,
        "scope": "Three real-data compatibility checks; not a full 892-crop rerun or physical validation.",
        "full_dataset_evidence_commit": "ace26f2fcc75fce9b2b9be069c57bc66f075c6fd",
        "input_files_unchanged": True,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
