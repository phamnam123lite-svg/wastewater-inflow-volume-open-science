"""Regression tests against false reproduction and overwritten references."""
import json, tempfile, unittest
from pathlib import Path
import pandas as pd
import run_analysis as a
import external_site as e
from verify_results import compare
import reproduce

class IntegrityTests(unittest.TestCase):
    def test_self_comparison_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):compare(d,d)
    def test_reference_output_protected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'reference_manifest.json').write_text('{}')
            for fn in [a.run,e.run]:
                with self.assertRaises(ValueError):fn(root)
    def test_complete_manifest_required(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)/'ref';o=Path(d)/'actual';r.mkdir();o.mkdir()
            (r/'reference_manifest.json').write_text(json.dumps({'required_csv_files':['a.csv','b.csv']}))
            for p in [r/'a.csv',r/'b.csv',o/'a.csv']:pd.DataFrame({'x':[1]}).to_csv(p,index=False)
            with self.assertRaises(FileNotFoundError):compare(r,o)
    def test_source_checksums(self):self.assertEqual(len(reproduce.input_check()),3)
    def test_existing_rerun_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):reproduce.main(Path(d))

if __name__=='__main__':unittest.main()
