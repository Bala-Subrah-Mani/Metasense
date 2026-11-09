"""RM-08 step 1: deterministic paper selection and input manifest (PROTOCOL.md section 3).

Usage:  python research/rm08_pilot/scripts/select_papers.py --sources <dir-with-clones> --out <pdf-dir>

<dir-with-clones> must contain blob-less clones of:
  mlresearch_v202, mlresearch_v206, mlresearch_v195  (https://github.com/mlresearch/vNNN)
  openjournals_joss-papers                          (https://github.com/openjournals/joss-papers)
The script checks out only the selected files, copies the PDFs (and JATS for JOSS) to <pdf-dir>,
and writes research/rm08_pilot/inputs/manifest.csv with provenance and SHA-256.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
import shutil
import subprocess
from pathlib import Path

SEED = 699
HERE = Path(__file__).resolve().parents[1]
STRATA = [  # (stratum, repo dir, n, role, venue, license note)
    ("E1", "mlresearch_v202", 5, "empirical two-column", "ICML 2023 (PMLR 202)", "Open access via PMLR; author copyright; local analysis only, not redistributed"),
    ("E2", "mlresearch_v206", 3, "empirical two-column", "AISTATS 2023 (PMLR 206)", "Open access via PMLR; author copyright; local analysis only, not redistributed"),
    ("T", "mlresearch_v195", 2, "negative control (theory)", "COLT 2023 (PMLR 195)", "Open access via PMLR; author copyright; local analysis only, not redistributed"),
    ("S", "openjournals_joss-papers", 2, "unconventional control (software paper)", "JOSS", "CC BY 4.0"),
]


def git(repo: Path, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def candidates(repo: Path, stratum: str) -> list[str]:
    files = git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    if stratum == "S":
        jats = {f.split("/")[0] for f in files if f.endswith(".jats")}
        out = []
        for f in files:
            m = re.fullmatch(r"(joss\.0(5\d{3}))/10\.21105\.joss\.0\d{4}\.pdf", f)
            if m and m.group(1) in jats:
                out.append(f)
        return sorted(out)
    # PMLR main papers: <id>/<id>.pdf ; supplementary files have other names
    return sorted(f for f in files if re.fullmatch(r"([a-z0-9]+)/\1\.pdf", f))


def pmlr_meta(repo: Path, paper_id: str) -> dict:
    post = next(f for f in git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
                if f.startswith("_posts/") and f.endswith(f"-{paper_id}.md"))
    text = git(repo, "show", f"HEAD:{post}")
    title = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", text, re.M).group(1)
    pdf = re.search(r"^pdf:\s*(\S+)", text, re.M)
    return {"title": title, "official_url": pdf.group(1) if pdf else ""}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src, out = Path(a.sources), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for stratum, repo_name, n, role, venue, lic in STRATA:
        repo = src / repo_name
        cands = candidates(repo, stratum)
        picked = random.Random(SEED).sample(cands, n)
        commit = git(repo, "rev-parse", "HEAD").strip()
        for path in picked:
            extra = [path.replace(".pdf", ".jats")] if stratum == "S" else []
            git(repo, "checkout", "HEAD", "--", path, *extra)
            doc_id = f"{stratum}-{Path(path).stem.replace('10.21105.', '')}"
            dst = out / f"{doc_id}.pdf"
            shutil.copyfile(repo / path, dst)
            for e in extra:
                shutil.copyfile(repo / e, out / f"{doc_id}.jats")
            if stratum == "S":
                jats = (repo / extra[0]).read_text(encoding="utf-8", errors="replace")
                t = re.search(r"<article-title>(.*?)</article-title>", jats, re.S)
                meta = {"title": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", t.group(1))).strip() if t else "",
                        "official_url": f"https://doi.org/10.21105/{Path(path).stem.split('10.21105.')[-1]}"}
            else:
                meta = pmlr_meta(repo, Path(path).stem)
            rows.append({
                "doc_id": doc_id, "stratum": stratum, "role": role, "venue": venue, "title": meta["title"],
                "source_repo": f"https://github.com/{repo_name.replace('_', '/', 1)}", "source_commit": commit,
                "source_path": path, "official_url": meta["official_url"], "license": lic,
                "bytes": dst.stat().st_size, "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                "candidates_in_stratum": len(cands), "seed": SEED,
            })
            print(f"{doc_id:22} {meta['title'][:70]}")
    mf = HERE / "inputs" / "manifest.csv"
    mf.parent.mkdir(exist_ok=True)
    with mf.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"manifest: {mf}  ({len(rows)} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
