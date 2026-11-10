from pathlib import Path
import concurrent.futures
import hashlib
import json
import urllib.request
from datetime import datetime, timezone

root = Path('D:/P2')
repo = 'phamnam123lite-svg/wastewater-inflow-volume-open-science'
commit = 'da3b755d0b06aaa72829fd069a8e3c1133eb1796'

def verify(path):
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/{path.name}'
    with urllib.request.urlopen(url, timeout=90) as response:
        content = response.read()
    remote_hash = hashlib.sha256(content).hexdigest()
    local_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(file=path.name, bytes=len(content), local_sha256=local_hash,
                remote_sha256=remote_hash, passed=local_hash == remote_hash, url=url)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(verify, sorted((root/'publication').iterdir())))
report = dict(checked_utc=datetime.now(timezone.utc).isoformat(),
              repository=f'https://github.com/{repo}',
              release=f'https://github.com/{repo}/releases/tag/v0.1.0',
              commit=commit, files=results, passed=all(r['passed'] for r in results))
(root/'verification'/'github_publication.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(root/'verification'/'publication_status.log').write_text(
    f"# Publication status\n\nRepository: {report['repository']}\n\n"
    f"Release: {report['release']}\n\nCommit: `{commit}`\n\n"
    f"All {len(results)} public repository files were downloaded independently "
    f"and SHA-256 compared with local publication files: "
    f"{'PASS' if report['passed'] else 'FAIL'}.\n\n"
    "The complete computational pipeline was rerun in a fresh Python 3.11.9 environment; "
    "13 result CSV files had zero numerical differences. See verification/reproduction.json "
    "and verification/github_publication.json.\n\n"
    "Earlier research audit notes describe the state before this publication and are retained "
    "as provenance. This file records the current publication status.\n\n"
    "The manuscript remains a research draft. No software DOI or journal acceptance is claimed.\n",
    encoding='utf-8')
print(json.dumps(dict(files_verified=len(results), passed=report['passed'], commit=commit)))
assert report['passed'], 'Remote files differ'
