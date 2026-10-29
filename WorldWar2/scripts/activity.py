"""Activity status of a unit on a date (pilot, October 2026; see docs/activity_status_design.md).

Usage: python scripts/activity.py UNIT_ID YYYY-MM-DD

Reads the activity columns of the claim files (activity_status, activity_basis, activity_span) and answers:
  - a span opened by a `start` row and closed by an `end` row of the same value (both days included) -> that value, status certain;
  - a span opened by a `start` row and closed implicitly by a later `start` row of another value -> that value up to the day before, status
    certain, end inferred;
  - after an open `start` with no later activity row -> that value, status possible, for at most OPEN_HORIZON_DAYS (30) days; then no answer;
  - a `point` row -> that value on its date only (it takes precedence over a span on that day);
  - otherwise no answer (blank activity is not 'idle').
The confidence of an answer is the lowest confidence of the rows that bound it; if either row has activity_basis inferred, the confidence is
capped at 0.3 and the support is 'inferred'.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

INFERRED_CAP = 0.3
OPEN_HORIZON_DAYS = 30   # an open span is carried forward as 'possible' for at most this many days after its start row


def load():
    """{unit_id: [claim dict with an activity, sorted by date then claim_id]}"""
    out = {}
    for p in common.claim_files():
        _h, rows = common.read_dicts(p)
        for r in rows:
            if r.get('activity_status'):
                out.setdefault(r['unit_id'], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: (r['date'], r['claim_id']))
    return out


def _conf(rows):
    c = min(float(r['confidence']) for r in rows)
    if any(r['activity_basis'] == 'inferred' for r in rows):
        return min(c, INFERRED_CAP), 'inferred'
    return c, 'stated'


def activity_at(unit, date, index=None):
    """dict(activity, status certain|possible, support stated|inferred, confidence, from_claim, to_claim, why) or None."""
    rows = (index if index is not None else load()).get(unit, [])
    for r in rows:
        if r['activity_span'] == 'point' and r['date'] == date:
            c, s = _conf([r])
            return dict(activity=r['activity_status'], status='certain', support=s, confidence=c, from_claim=r['claim_id'], to_claim=r['claim_id'],
                        why='observed on this date (%s)' % r['claim_id'])
    spans = [r for r in rows if r['activity_span'] in ('start', 'end')]
    last = None
    for r in spans:
        if r['date'] <= date:
            last = r
    if last is None:
        return None
    if last['activity_span'] == 'end':
        if last['date'] == date:
            starts = [r for r in spans if r['activity_span'] == 'start' and r['activity_status'] == last['activity_status'] and r['date'] <= date]
            c, s = _conf([starts[-1], last] if starts else [last])
            return dict(activity=last['activity_status'], status='certain', support=s, confidence=c, from_claim=starts[-1]['claim_id'] if starts else '',
                        to_claim=last['claim_id'], why='last day of the span (%s)' % last['claim_id'])
        return None
    later = [r for r in spans if r['date'] > date]
    if later:
        nxt = later[0]
        if nxt['activity_span'] == 'end' and nxt['activity_status'] == last['activity_status']:
            c, s = _conf([last, nxt])
            return dict(activity=last['activity_status'], status='certain', support=s, confidence=c, from_claim=last['claim_id'], to_claim=nxt['claim_id'],
                        why='inside the span %s to %s' % (last['claim_id'], nxt['claim_id']))
        if nxt['activity_span'] == 'start':
            end = (datetime.date.fromisoformat(nxt['date']) - datetime.timedelta(days=1)).isoformat()
            c, _s = _conf([last])
            return dict(activity=last['activity_status'], status='certain', support='inferred', confidence=min(c, INFERRED_CAP), from_claim=last['claim_id'],
                        to_claim=nxt['claim_id'], why='span %s ended implicitly by the %s start of %s (end inferred %s)' % (last['claim_id'], nxt['activity_status'], nxt['claim_id'], end))
    if (datetime.date.fromisoformat(date) - datetime.date.fromisoformat(last['date'])).days > OPEN_HORIZON_DAYS:
        return None
    c, s = _conf([last])
    return dict(activity=last['activity_status'], status='possible', support=s, confidence=c, from_claim=last['claim_id'], to_claim='',
                why='open span from %s (%s), no later activity row' % (last['claim_id'], last['date']))


def describe(a):
    return '%s (%s, %s, confidence %.1f): %s' % (a['activity'], a['status'], a['support'], a['confidence'], a['why'])


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    a = activity_at(argv[0], argv[1])
    if not a:
        print('no activity recorded for %s on %s' % tuple(argv))
        return 1
    print('%s on %s: activity %s' % (argv[0], argv[1], describe(a)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
