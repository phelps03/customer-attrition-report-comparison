#!/usr/bin/env python3
"""Build the public aggregate data.json from a private FieldRoutes
"All Time Customer List" CSV export.

Input CSV columns: Customer ID, Last Name, First Name, Customer Status,
Initial Service, Subscription.

Output is aggregate-only: [cohortDate, activeFlag, count] rows.
No customer-level data is written.
"""
import argparse, collections, csv, datetime, json, sys

def parse_date(s):
    s = (s or '').strip()
    for f in ('%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s, f).date()
        except ValueError:
            pass
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('out_path')
    ap.add_argument('--generated-at', required=True,
                    help='Export snapshot time, ISO 8601 (e.g. 2026-09-22T13:00:00-06:00)')
    a = ap.parse_args()

    rows = bad_id = bad_date = status_conflicts = 0
    cohort, status = {}, {}
    with open(a.csv_path, newline='', encoding='utf-8-sig') as f:
        for rec in csv.DictReader(f):
            rows += 1
            cid = (rec.get('Customer ID') or '').strip()
            if not cid:
                bad_id += 1
                continue
            d = parse_date(rec.get('Initial Service'))
            if not d:
                bad_date += 1
                continue
            st = (rec.get('Customer Status') or '').strip().lower()
            if cid not in cohort or d < cohort[cid]:
                cohort[cid] = d
            if cid in status and status[cid] != st:
                status_conflicts += 1
            status.setdefault(cid, st)

    agg = collections.Counter()
    active = frozen = other = 0
    for cid, dt in cohort.items():
        st = status.get(cid, '')
        if st == 'active':
            flag, active = 1, active + 1
        elif st == 'frozen':
            flag, frozen = 0, frozen + 1
        else:
            flag, other = 0, other + 1
        agg[(dt.isoformat(), flag)] += 1

    records = [[dt, flag, n] for (dt, flag), n in sorted(agg.items())]
    out = {
        'customerCount': len(cohort),
        'generatedAt': a.generated_at,
        'validation': {
            'reportRows': rows,
            'reportUniqueCustomers': len(cohort),
            'activeCustomers': active,
            'frozenCustomers': frozen,
            'otherStatusCustomers': other,
            'extraSubscriptionRows': rows - len(cohort) - bad_id - bad_date,
            'skippedBlankCustomerId': bad_id,
            'skippedBadInitialService': bad_date,
            'statusConflictsAcrossRows': status_conflicts,
            'cohortRule': 'Earliest Initial Service across all report rows per Customer ID',
            'statusRule': 'Customer Status from the report snapshot',
        },
        'records': records,
    }
    with open(a.out_path, 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    v = out['validation']
    print(f"rows={v['reportRows']} unique={v['reportUniqueCustomers']} "
          f"active={v['activeCustomers']} frozen={v['frozenCustomers']} other={v['otherStatusCustomers']}")
    print(f"skipped: blank_id={bad_id} bad_date={bad_date}; status_conflicts={status_conflicts}")
    print(f"cohort range: {records[0][0]} .. {records[-1][0]}; aggregate rows: {len(records)}")

if __name__ == '__main__':
    main()
