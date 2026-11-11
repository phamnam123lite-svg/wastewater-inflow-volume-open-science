"""Independent re-computation of the results.

Written separately from the analysis code (no module from src/ is imported). Everything is rebuilt
from the raw observation files and the saved forecasts, following the definitions in the manuscript:

  1. data audit of both raw files (counts, gaps, duplicates, daylight-saving handling, ranges)
  2. hourly alignment, screening and the 12-hour integrated target V(t,h) = sum Q(t+k), k = 1..h
  3. baselines (persistence, previous-24-hour mean, previous-day profile)
  4. eligibility rules, temporal splits, high-volume thresholds and target means
  5. point metrics for every scenario, model and group (MAE, RMSE, R2, bias, underprediction)
  6. split-residual 90% intervals (pooled, wet/dry, rolling 30 d) rebuilt from calibration residuals,
     with coverage, width, interval score and upper exceedance
  7. episodes, leave-one-episode-out and non-overlapping phase coverage
  8. paired MAE differences and an independent circular block bootstrap
  9. the same steps for the German site (15-minute data aggregated to hours)
 10. forecast-conditioned high-volume coverage

Run from the repository root (reproduce.py runs it on the rerun outputs):
    python src/independent_check.py --denmark results/denmark --germany results/germany --report check.json
"""
import argparse, json, math
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--denmark', type=Path, default=ROOT / 'results' / 'denmark')
ap.add_argument('--germany', type=Path, default=ROOT / 'results' / 'germany')
ap.add_argument('--report', type=Path, default=ROOT / 'verification' / 'independent_check.json')
args = ap.parse_args(); RD, RG, OUT = args.denmark, args.germany, args.report
H1 = pd.Timedelta(hours=1)
report = {'checks': [], 'data_audit': {}, 'extra': {}}

def check(name, reported, value, tol):
    """Record a comparison of a reported/reference value with the independent value."""
    diff = None if value is None or reported is None else float(abs(float(reported) - float(value)))
    status = 'PASS' if diff is not None and diff <= tol else 'FAIL'
    report['checks'].append(dict(check=name, reported=reported, recomputed=value, abs_diff=diff, tol=tol, status=status))
    return status

def maxdiff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape: return float('inf')
    both = ~(np.isnan(a) & np.isnan(b))
    if (np.isnan(a) ^ np.isnan(b)).any(): return float('inf')
    return float(np.nanmax(np.abs(a[both] - b[both]))) if both.any() else 0.0

# ----------------------------------------------------------------------------- 1. Danish raw data
raw = pd.read_csv(ROOT / 'data/denmark/wwtp.csv', sep=';')
met = pd.read_csv(ROOT / 'data/denmark/dmi.csv')
cph = ZoneInfo('Europe/Copenhagen')
local = pd.to_datetime(raw['datetime'])
utc, kinds = [], []
for ts in local:
    naive = ts.to_pydatetime()
    a, b = naive.replace(tzinfo=cph, fold=0), naive.replace(tzinfo=cph, fold=1)
    roundtrip = a.astimezone(timezone.utc).astimezone(cph).replace(tzinfo=None)
    if roundtrip != naive: kinds.append('nonexistent'); utc.append(pd.NaT)
    elif a.utcoffset() != b.utcoffset(): kinds.append('ambiguous'); utc.append(pd.NaT)
    else: kinds.append('ok'); utc.append(pd.Timestamp(a.astimezone(timezone.utc)).tz_localize(None))
kinds = pd.Series(kinds)
flow_raw = pd.Series(raw['flow'].to_numpy(), index=pd.DatetimeIndex(utc))
dropped = local[kinds != 'ok']
flow_raw = flow_raw[flow_raw.index.notna()]
met['time'] = pd.to_datetime(met['time']); met = met.set_index('time')
grid = pd.date_range(min(met.index.min(), flow_raw.index.min()), max(met.index.max(), flow_raw.index.max()), freq='h')
d = met.reindex(grid)
d['flow_raw'] = flow_raw.reindex(grid)
q = d['flow_raw'].to_numpy()
low = q < 2
flat = np.zeros(len(q), bool)
for i in range(5, len(q)):
    w = q[i - 5:i + 1]
    if np.isfinite(w).all() and w.max() - w.min() < 5: flat[i] = True
d['flow'] = np.where(low | flat, np.nan, q)
hum = d['mean_relative_hum']
report['data_audit']['denmark'] = dict(
    flow_rows=len(raw), flow_duplicate_local_timestamps=int(local.duplicated().sum()),
    dst_dropped={str(t): k for t, k in zip(dropped, kinds[kinds != 'ok'])},
    flow_negative=int((raw['flow'] < 0).sum()), flow_zero=int((raw['flow'] == 0).sum()),
    flow_min=float(raw['flow'].min()), flow_median=float(raw['flow'].median()),
    flow_p99=float(raw['flow'].quantile(.99)), flow_max=float(raw['flow'].max()),
    flow_max_time_local=str(local[raw['flow'].idxmax()]),
    met_rows=len(met), met_regular_hourly=bool((met.index.to_series().diff().dropna() == H1).all()),
    met_duplicates=int(met.index.duplicated().sum()), grid_rows=len(grid), grid_start=str(grid[0]), grid_end=str(grid[-1]),
    missing_flow_raw=int(np.isnan(q).sum()), low_flags=int(low.sum()), flat_flags=int(flat.sum()),
    missing_flow_screened=int(d['flow'].isna().sum()),
    humidity_outside_0_100=int((~hum.between(0, 100) & hum.notna()).sum()),
    missing_by_column={c: int(met[c].isna().sum()) for c in met.columns},
    precip_negative=int((met['acc_precip'] < 0).sum()), precip_max=float(met['acc_precip'].max()),
    pressure_range=[float(met['mean_pressure'].min()), float(met['mean_pressure'].max())],
    temp_range=[float(met['mean_temp'].min()), float(met['mean_temp'].max())],
    radiation_negative=int((met['mean_radiation'] < 0).sum()))
da = report['data_audit']['denmark']
check('DK raw flow records (2.2)', 9868, da['flow_rows'], 0)
check('DK aligned grid positions (2.2)', 11257, da['grid_rows'], 0)
check('DK DST timestamps removed (2.2)', 1, len(da['dst_dropped']), 0)
check('DK low flags (2.2)', 6, da['low_flags'], 0)
check('DK flat-window flags (2.2)', 18, da['flat_flags'], 0)
check('DK missing flow before screening (2.2)', 1390, da['missing_flow_raw'], 0)
check('DK missing flow after screening (2.2)', 1414, da['missing_flow_screened'], 0)
ref_clean = pd.read_csv(RD / 'cleaned_hourly.csv', index_col=0, parse_dates=True)
check('DK cleaned hourly flow vs reference (max abs diff)', 0, maxdiff(ref_clean['flow'], d['flow']), 1e-9)

# ----------------------------------------------------------------------------- 2-4. Danish targets, baselines, splits
def target(Q, h):
    m = np.full(len(Q), np.nan)
    for i in range(len(Q) - h):
        w = Q[i + 1:i + h + 1]
        if np.isfinite(w).all(): m[i] = w.sum()
    return m

def baselines(Q, h):
    n = len(Q); pers = h * Q; mean24 = np.full(n, np.nan); seas = np.full(n, np.nan)
    for i in range(n):
        if i >= 23:
            w = Q[i - 23:i + 1]
            if np.isfinite(w).all(): mean24[i] = h * w.mean()
        lo, hi = i + 1 - 24, i + h - 24
        if lo >= 0 and hi < n:
            w = Q[lo:hi + 1]
            if np.isfinite(w).all(): seas[i] = w.sum()
    return pers, mean24, seas

Q = d['flow'].to_numpy(); P = d['acc_precip'].to_numpy(); idx = d.index
rain6 = pd.Series(P).rolling(6).sum().to_numpy()
def future_rain_complete(h):
    ok = np.zeros(len(P), bool)
    for i in range(len(P) - h): ok[i] = np.isfinite(P[i + 1:i + h + 1]).all()
    return ok

N = len(idx); b1, b2, end = idx[int(.6 * N)], idx[int(.8 * N)], idx[-1] + H1
scen = {f'primary_{h}h': (h, b1, b2, end) for h in (12, 6, 24)}
for s in ['2024-08-15', '2024-10-15', '2024-12-15']:
    t0 = pd.Timestamp(s); scen['origin_' + s] = (12, t0 - pd.Timedelta(days=45), t0, t0 + pd.Timedelta(days=60))
ref_splits = pd.read_csv(RD / 'splits.csv')
ref_metrics = pd.read_csv(RD / 'metrics.csv'); ref_int = pd.read_csv(RD / 'intervals.csv')
DK = {}
for name, (h, c1, c2, c3) in scen.items():
    y = target(Q, h); pers, mean24, seas = baselines(Q, h)
    valid = np.isfinite(y) & np.isfinite(pers) & np.isfinite(mean24) & np.isfinite(seas) & np.isfinite(rain6) & future_rain_complete(h)
    tend = idx + pd.Timedelta(hours=h)
    masks = {'train': valid & (tend < c1), 'calibration': valid & (idx >= c1) & (tend < c2), 'test': valid & (idx >= c2) & (tend < c3)}
    thr = float(pd.Series(y[masks['train']]).quantile(.9))
    rs = ref_splits[ref_splits.scenario == name].set_index('split')
    for part, m in masks.items():
        check(f'DK {name} {part} n', int(rs.loc[part, 'n']), int(m.sum()), 0)
        check(f'DK {name} {part} mean target (m3)', float(rs.loc[part, 'target_mean']), float(y[m].mean()), 1e-6)
    check(f'DK {name} high threshold (m3)', float(rs.loc['test', 'high_threshold_m3']), thr, 1e-6)
    for part, fname in [('test', f'predictions_{name}.csv'), ('calibration', f'calibration_{name}.csv')]:
        f = pd.read_csv(RD / fname, index_col=0, parse_dates=True)
        sel = pd.Series(np.arange(N), index=idx).loc[f.index].to_numpy()
        check(f'DK {name} {part} targets vs saved (max abs diff)', 0, maxdiff(f['observed'], y[sel]), 1e-6)
        for col, arr in [('persistence', pers), ('mean24', mean24), ('seasonal24', seas)]:
            check(f'DK {name} {part} {col} vs saved (max abs diff)', 0, maxdiff(f[col], arr[sel]), 1e-6)
        check(f'DK {name} {part} wet flags vs saved', 0, int((f['wet'].to_numpy() != (rain6[sel] > 0)).sum()), 0)
        check(f'DK {name} {part} high flags vs saved', 0, int((f['high'].to_numpy() != (y[sel] > thr)).sum()), 0)
    DK[name] = dict(h=h, thr=thr)

# ----------------------------------------------------------------------------- 5-6. metrics and intervals (generic)
def point_metrics(y, p):
    e = p - y
    return dict(n=len(y), MAE_m3=np.abs(e).mean(), RMSE_m3=math.sqrt((e ** 2).mean()),
                R2=1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum(), bias_m3=e.mean(), mean_underprediction_m3=np.maximum(-e, 0).mean())

def kth_radius(res):
    res = np.sort(np.asarray(res, float)); k = math.ceil((len(res) + 1) * 0.9)
    return math.inf if k > len(res) else res[k - 1]

def intervals(cal, test, model, h, method):
    r_cal = np.abs(cal['observed'] - cal[model]).to_numpy(); base = kth_radius(r_cal)
    radius = np.full(len(test), base)
    if method == 'wet_dry':
        for state in (False, True):
            s = r_cal[cal['wet'].to_numpy() == state]
            if len(s) >= 30: radius[test['wet'].to_numpy() == state] = kth_radius(s)
    if method == 'rolling30d':
        both = pd.concat([cal, test]); mat = (both.index + pd.Timedelta(hours=h)).to_numpy()
        res = np.abs(both['observed'] - both[model]).to_numpy()
        for j, t in enumerate(test.index.to_numpy()):
            ok = (mat <= t) & (mat > t - np.timedelta64(30, 'D'))
            if ok.sum() >= 30: radius[j] = kth_radius(res[ok])
    p = test[model].to_numpy()
    return np.maximum(0, p - radius), p + radius

def interval_stats(y, lo, hi):
    miss_lo, miss_hi = np.maximum(lo - y, 0), np.maximum(y - hi, 0)
    return dict(coverage=((y >= lo) & (y <= hi)).mean(), width_m3=(hi - lo).mean(),
                interval_score_m3=(hi - lo + 20 * miss_lo + 20 * miss_hi).mean(), upper_exceedance=(y > hi).mean())

def audit_site(site, preds, cals, ref_m, ref_i, bounds_files, scen_key, h_of):
    worst = dict(metrics=0.0, bounds=0.0, interval_stats=0.0); n_m = n_i = 0
    for key in preds:
        test, cal = preds[key], cals[key]; h = h_of(key)
        models = [c for c in test.columns if c not in ('observed', 'wet', 'high')]
        groups = {'all': np.ones(len(test), bool), 'wet': test['wet'].to_numpy(), 'dry': ~test['wet'].to_numpy(), 'high': test['high'].to_numpy()}
        y = test['observed'].to_numpy()
        rm = ref_m if scen_key is None else ref_m[ref_m[scen_key] == key]
        for mdl in models:
            for g, m in groups.items():
                if m.sum() == 0: continue
                mine = point_metrics(y[m], test[mdl].to_numpy()[m]); row = rm[(rm.model == mdl) & (rm.group == g)]
                if len(row) != 1: continue
                for k, v in mine.items():
                    worst['metrics'] = max(worst['metrics'], abs(float(row[k].iloc[0]) - v)); n_m += 1
        b = pd.read_csv(bounds_files[key], parse_dates=[0]); b = b.set_index(b.columns[0])
        ri = ref_i if scen_key is None else ref_i[ref_i[scen_key] == key]
        for (mdl, method), part in b.groupby(['model', 'method']):
            lo, hi = intervals(cal, test, mdl, h, method)
            part = part.loc[test.index]
            worst['bounds'] = max(worst['bounds'], maxdiff(part['lower'], lo), maxdiff(part['upper'], hi))
            for g, m in groups.items():
                row = ri[(ri.model == mdl) & (ri.method == method) & (ri.group == g)]
                if len(row) != 1 or m.sum() == 0: continue
                for k, v in interval_stats(y[m], lo[m], hi[m]).items():
                    worst['interval_stats'] = max(worst['interval_stats'], abs(float(row[k].iloc[0]) - v)); n_i += 1
    check(f'{site} point metrics vs reference ({n_m} values, max abs diff)', 0, worst['metrics'], 1e-6)
    check(f'{site} interval bounds rebuilt from calibration residuals (max abs diff, m3)', 0, worst['bounds'], 1e-6)
    check(f'{site} interval statistics vs reference ({n_i} values, max abs diff)', 0, worst['interval_stats'], 1e-6)

dk_pred = {k: pd.read_csv(RD / f'predictions_{k}.csv', index_col=0, parse_dates=True) for k in scen}
dk_cal = {k: pd.read_csv(RD / f'calibration_{k}.csv', index_col=0, parse_dates=True) for k in scen}
audit_site('DK', dk_pred, dk_cal, ref_metrics, ref_int, {k: RD / f'bounds_{k}.csv' for k in scen}, 'scenario', lambda k: scen[k][0])

# ----------------------------------------------------------------------------- 7. episodes, LOEO, phases
def runs(index, flags):
    out, cur = [], []
    for t, f in zip(index, flags):
        if f and cur and t - cur[-1] == H1: cur.append(t)
        elif f: cur = [t]; out.append(cur)
        else: cur = []
    return out

def episode_checks(site, test, b, model, ref_ep, ref_loeo, ref_phase, origin):
    lo = b[(b.model == model) & (b.method == 'pooled')].loc[test.index]
    cover = ((test['observed'] >= lo['lower']) & (test['observed'] <= lo['upper'])).to_numpy()
    eps = runs(test.index, test['high'].to_numpy())
    pos = {t: i for i, t in enumerate(test.index)}
    sizes = [len(e) for e in eps]; covs = [cover[[pos[t] for t in e]].mean() for e in eps]
    check(f'{site} {model} episode count', len(ref_ep), len(eps), 0)
    check(f'{site} {model} episode sizes (sum abs diff)', 0, float(np.abs(np.array(sizes) - ref_ep['n'].to_numpy()).sum()), 0)
    check(f'{site} {model} episode coverage (max abs diff)', 0, float(np.abs(np.array(covs) - ref_ep['coverage'].to_numpy()).max()), 1e-12)
    if ref_loeo is not None:
        high = test['high'].to_numpy(); loeo = []
        for e in eps:
            keep = high.copy(); keep[[pos[t] for t in e]] = False; loeo.append(cover[keep].mean())
        check(f'{site} {model} leave-one-episode-out coverage (max abs diff)', 0, float(np.abs(np.array(loeo) - ref_loeo['coverage'].to_numpy()).max()), 1e-12)
    # phase = whole hours since the start of the site's hourly grid, modulo 12 (manuscript Section 2.6)
    ph = ((test.index - origin) // H1).to_numpy() % 12; hc = []
    for p in range(12):
        m = (ph == p); mh = m & test['high'].to_numpy()
        hc.append(cover[mh].mean() if mh.any() else np.nan)
    check(f'{site} {model} phase high-volume coverage (max abs diff)', 0, maxdiff(ref_phase['high_coverage'].to_numpy(), np.array(hc)), 1e-12)
    return sizes, covs

t12 = dk_pred['primary_12h']; b12 = pd.read_csv(RD / 'bounds_primary_12h.csv', parse_dates=[0]).set_index('issue_time_utc')
ep, loeo, phase = pd.read_csv(RD / 'episodes.csv'), pd.read_csv(RD / 'leave_one_episode_out.csv'), pd.read_csv(RD / 'nonoverlap.csv')
for mdl in ['mean24', 'hgb_history', 'fixed_history']:
    f = lambda t: t[(t.scenario == 'primary_12h') & (t.model == mdl)]
    sizes, _ = episode_checks('DK', t12, b12, mdl, f(ep), f(loeo), f(phase), grid[0])
report['extra']['dk_episode_sizes'] = sizes

# ----------------------------------------------------------------------------- 8. paired differences and bootstrap
def circular_block_bootstrap(diff, index, B, nboot=2000, seed=12345):
    """Fixed-length circular blocks that wrap within each run of consecutive hours; starts sampled uniformly."""
    t = pd.DatetimeIndex(index).as_unit('ns'); n = len(diff)
    run_id = np.r_[0, np.cumsum(np.diff(t.asi8) != 3600 * 10 ** 9)]
    starts_of = {r: np.flatnonzero(run_id == r) for r in np.unique(run_id)}
    blocksum = np.empty(n); partial = {}
    for r, ix in starts_of.items():
        L = len(ix); vals = diff[ix]
        for j in range(L):
            blocksum[ix[j]] = vals[(j + np.arange(B)) % L].sum()
    full, rem = divmod(n, B); rng = np.random.default_rng(seed)
    rem_sum = np.empty(n)
    for r, ix in starts_of.items():
        L = len(ix); vals = diff[ix]
        for j in range(L): rem_sum[ix[j]] = vals[(j + np.arange(rem)) % L].sum() if rem else 0.0
    out = blocksum[rng.integers(n, size=(nboot, full))].sum(axis=1) + (rem_sum[rng.integers(n, size=nboot)] if rem else 0)
    out = out / n
    return float(np.quantile(out, .025)), float(np.quantile(out, .975))

ref_boot = pd.read_csv(RD / 'bootstrap.csv'); boot_rows = []
for _, r in ref_boot[ref_boot.scenario == 'primary_12h'].iterrows():
    a, bm = r['comparison'].split(' minus ')
    diff = np.abs(t12[a] - t12['observed']).to_numpy() - np.abs(t12[bm] - t12['observed']).to_numpy()
    check(f"DK paired MAE difference {r['comparison']} (B={r['block_hours']})", r['MAE_difference'], diff.mean(), 1e-9)
    lo, hi = circular_block_bootstrap(diff, t12.index, int(r['block_hours']))
    boot_rows.append(dict(comparison=r['comparison'], block=int(r['block_hours']), ref_low=r['sensitivity_low'], ref_high=r['sensitivity_high'],
                          independent_low=lo, independent_high=hi, same_sign_conclusion=bool((r['sensitivity_low'] > 0) == (lo > 0) and (r['sensitivity_high'] < 0) == (hi < 0))))
report['extra']['dk_bootstrap_independent'] = boot_rows
check('DK bootstrap: independent ranges give the same excludes-zero conclusions', len(boot_rows), sum(x['same_sign_conclusion'] for x in boot_rows), 0)

# ----------------------------------------------------------------------------- 9. German site
g = pd.read_csv(ROOT / 'data/germany/wtp_network_rain.csv', sep=';')
g['Timestamp'] = pd.to_datetime(g['Timestamp']); gi = g.set_index('Timestamp')
report['data_audit']['germany'] = dict(
    rows=len(g), regular_15min=bool((gi.index.to_series().diff().dropna() == pd.Timedelta(minutes=15)).all()),
    duplicates=int(gi.index.duplicated().sum()), start=str(gi.index[0]), end=str(gi.index[-1]),
    missing={c: int(gi[c].isna().sum()) for c in gi.columns},
    negative_inflow=int((gi['wtp_inflow [l/s]'] < 0).sum()), negative_rain=int((gi['rain_rate [mm/min]'] < 0).sum()),
    inflow_l_s=[float(gi['wtp_inflow [l/s]'].min()), float(gi['wtp_inflow [l/s]'].median()), float(gi['wtp_inflow [l/s]'].max())],
    rain_mm_min_max=float(gi['rain_rate [mm/min]'].max()))
ga = report['data_audit']['germany']
check('DE quarter-hour records (2.7)', 105120, ga['rows'], 0)
check('DE missing inflow values (2.7)', 3, ga['missing']['wtp_inflow [l/s]'], 0)
check('DE missing rain values (2.7)', 3, ga['missing']['rain_rate [mm/min]'], 0)
# hour ending t: four samples in (t-1h, t]; mean L/s x 3.6 -> m3/h; sum mm/min x 15 min -> mm
hours = pd.date_range(gi.index[0].ceil('h'), gi.index[-1].ceil('h'), freq='h')
fl = gi['wtp_inflow [l/s]'].to_numpy(); rr = gi['rain_rate [mm/min]'].to_numpy(); pos = {t: i for i, t in enumerate(gi.index)}
Fh, Rh = np.full(len(hours), np.nan), np.full(len(hours), np.nan)
for k, t in enumerate(hours):
    ii = [pos.get(t - pd.Timedelta(minutes=m)) for m in (45, 30, 15, 0)]
    if None in ii: continue
    f4, r4 = fl[ii], rr[ii]
    if np.isfinite(f4).all() and (f4 >= 0).all(): Fh[k] = f4.mean() * 3.6
    if np.isfinite(r4).all() and (r4 >= 0).all(): Rh[k] = r4.sum() * 15
ref_h = pd.read_csv(RG / 'external_hourly.csv', index_col=0, parse_dates=True)
check('DE hourly flow aggregation vs reference (max abs diff, m3/h)', 0, maxdiff(ref_h['flow'], pd.Series(Fh, hours).reindex(ref_h.index)), 1e-9)
check('DE hourly rain aggregation vs reference (max abs diff, mm)', 0, maxdiff(ref_h['acc_precip'], pd.Series(Rh, hours).reindex(ref_h.index)), 1e-9)
QG, PG = Fh, Rh; yG = target(QG, 12); persG, meanG, seasG = baselines(QG, 12)
r6G = pd.Series(PG).rolling(6).sum().to_numpy()
okG = np.zeros(len(PG), bool)
for i in range(len(PG) - 12): okG[i] = np.isfinite(PG[i + 1:i + 13]).all()
validG = np.isfinite(yG) & np.isfinite(persG) & np.isfinite(meanG) & np.isfinite(seasG) & np.isfinite(r6G) & okG
tendG = hours + pd.Timedelta(hours=12)
mG = {'train': validG & (tendG < pd.Timestamp('2019-01-01')),
      'calibration': validG & (hours >= pd.Timestamp('2019-01-01')) & (tendG < pd.Timestamp('2019-04-01')),
      'test': validG & (hours >= pd.Timestamp('2019-04-01')) & (tendG < pd.Timestamp('2020-01-01'))}
rsG = pd.read_csv(RG / 'external_splits.csv').set_index('split')
for part, m in mG.items():
    check(f'DE {part} n', int(rsG.loc[part, 'n']), int(m.sum()), 0)
    check(f'DE {part} mean target (m3)', float(rsG.loc[part, 'mean_target']), float(yG[m].mean()), 1e-6)
thrG = float(pd.Series(yG[mG['train']]).quantile(.9))
check('DE high threshold (m3)', json.loads((RG / 'external_source_audit.json').read_text())['high_threshold_m3'], thrG, 1e-6)
gp = pd.read_csv(RG / 'external_predictions.csv', index_col=0, parse_dates=True)
gc = pd.read_csv(RG / 'external_calibration.csv', index_col=0, parse_dates=True)
for part, f in [('test', gp), ('calibration', gc)]:
    sel = pd.Series(np.arange(len(hours)), index=hours).loc[f.index].to_numpy()
    check(f'DE {part} targets vs saved (max abs diff)', 0, maxdiff(f['observed'], yG[sel]), 1e-6)
    for col, arr in [('persistence', persG), ('mean24', meanG), ('seasonal24', seasG)]:
        check(f'DE {part} {col} vs saved (max abs diff)', 0, maxdiff(f[col], arr[sel]), 1e-6)
audit_site('DE', {'x': gp}, {'x': gc}, pd.read_csv(RG / 'external_metrics.csv'), pd.read_csv(RG / 'external_intervals.csv'),
           {'x': RG / 'external_bounds.csv'}, None, lambda k: 12)
bG = pd.read_csv(RG / 'external_bounds.csv', parse_dates=[0]).set_index('provider_issue_time')
epG, phG = pd.read_csv(RG / 'external_episodes.csv'), pd.read_csv(RG / 'external_nonoverlap.csv')
for mdl in ['mean24', 'hgb_rain']:
    sizesG, _ = episode_checks('DE', gp, bG, mdl, epG[epG.model == mdl], None, phG[phG.model == mdl], hours[0])
check('DE high-volume windows', 700, int(gp['high'].sum()), 0)

# ----------------------------------------------------------------------------- 10. forecast-conditioned coverage
for site, test, bnd, thr_, models, fname in [
        ('DK', t12, b12, DK['primary_12h']['thr'], ['mean24', 'hgb_history', 'hgb_oracle'], RD / 'forecast_high_coverage.csv'),
        ('DE', gp, bG, thrG, ['mean24', 'hgb_rain', 'hgb_oracle'], RG / 'external_forecast_high_coverage.csv')]:
    ref = pd.read_csv(fname).set_index(['model', 'method']); worst = 0.0; y = test['observed'].to_numpy()
    for mdl in models:
        fh = test[mdl].to_numpy() > thr_
        for meth in ['pooled', 'wet_dry', 'rolling30d']:
            x = bnd[(bnd.model == mdl) & (bnd.method == meth)].loc[test.index]
            cov = ((y >= x['lower'].to_numpy()) & (y <= x['upper'].to_numpy()))[fh].mean()
            worst = max(worst, abs(cov - ref.loc[(mdl, meth), 'coverage_forecast_high']), abs(int(fh.sum()) - ref.loc[(mdl, meth), 'n_forecast_high']))
    check(f'{site} forecast-conditioned high-volume coverage (max abs diff)', 0, float(worst), 1e-12)

# ----------------------------------------------------------------------------- synthetic diagnostic: Monte Carlo SE
syn = pd.read_csv(RD / 'SYNTHETIC_bootstrap_diagnostic.csv')
for _, r in syn.iterrows():
    check(f"Synthetic AR(1) rho={r['SYNTHETIC_rho']} MC standard error", r['monte_carlo_standard_error'],
          math.sqrt(r['coverage'] * (1 - r['coverage']) / r['monte_carlo']), 1e-12)

report['summary'] = dict(checks=len(report['checks']), passed=sum(c['status'] == 'PASS' for c in report['checks']),
                         failed=[c['check'] for c in report['checks'] if c['status'] != 'PASS'])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print(json.dumps(report['summary'], indent=2))
if report['summary']['failed']: raise SystemExit('Independent check failed: ' + '; '.join(report['summary']['failed']))
