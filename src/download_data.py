"""Restore the Danish observations from the pinned Zenodo v1 record (provider MD5 verified)."""
from pathlib import Path
import hashlib, io, json, zipfile
import requests

def main():
    root=Path(__file__).resolve().parents[1];target=root/'data'/'denmark'
    target.mkdir(parents=True,exist_ok=True)
    response=requests.get('https://zenodo.org/api/records/15301164',timeout=90);response.raise_for_status();meta=response.json()
    if meta.get('doi')!='10.5281/zenodo.15301164':raise ValueError('Unexpected source DOI')
    (target/'zenodo_15301164.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    expected={'observations.zip':'md5:d4c0a1e0327142ff699625b28861639e','processed.zip':'md5:d819e64d7e4fe4b8cfd24ca522a9068c'}
    for f in meta['files']:
        if f['key'] not in expected:continue
        if f['checksum']!=expected[f['key']]:raise ValueError('Pinned archive checksum changed')
        path=target/f['key']
        if path.exists():blob=path.read_bytes()
        else:
            response=requests.get(f['links']['self'],timeout=120);response.raise_for_status();blob=response.content
        if 'md5:'+hashlib.md5(blob).hexdigest()!=expected[f['key']]:raise ValueError('Archive checksum mismatch')
        path.write_bytes(blob)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for name in z.namelist():
                if name.endswith('.csv'):(target/Path(name).name).write_bytes(z.read(name))
        print('Verified',f['key'])

if __name__=='__main__':main()
