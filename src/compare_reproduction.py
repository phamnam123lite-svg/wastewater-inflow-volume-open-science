"""Compare a rerun directory with a reference results directory (all registered CSV files)."""
import argparse,json
from pathlib import Path
from verify_results import compare

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--actual',type=Path,required=True)
    p.add_argument('--report',type=Path);args=p.parse_args();result=compare(args.reference,args.actual)
    if args.report:args.report.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
