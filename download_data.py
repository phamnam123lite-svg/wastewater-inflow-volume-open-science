"""Download immutable Zenodo v1 archives; verify provider MD5 and save provenance."""
from pathlib import Path
import requests,hashlib,json,io,zipfile
P=Path(__file__).resolve().parent
(P/'data').mkdir(exist_ok=True);(P/'sources').mkdir(exist_ok=True)
u='https://zenodo.org/api/records/15301164'
r=requests.get(u,timeout=90);r.raise_for_status();meta=r.json()
assert meta['doi']=='10.5281/zenodo.15301164'
(P/'sources/zenodo_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
for f in meta['files']:
    if f['key'] not in ['observations.zip','processed.zip']:continue
    out=P/'data'/f['key']
    b=out.read_bytes() if out.exists() else requests.get(f['links']['self'],timeout=120).content
    assert 'md5:'+hashlib.md5(b).hexdigest()==f['checksum'],f['key']+' checksum mismatch'
    out.write_bytes(b)
    with zipfile.ZipFile(io.BytesIO(b)) as archive:
        for name in archive.namelist():
            if name.endswith('.csv'):
                (P/'data'/Path(name).name).write_bytes(archive.read(name))
    print('Verified',f['key'])
