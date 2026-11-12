#!/usr/bin/env python3
"""Hold the variable font's stored deltas in place for every point outside the redrawn part.
Stage 3: on n eng m u a the redrawn part is the wedge plus the landing and the one curve of the letter that starts there.

    pin_deltas_s3.py UNTOUCHED_VF PATCHED_VF PATCHED_VF_ALL_DELTAS_EXPLICIT OUT_VF glyph [glyph ...]

Why: a variable font does not store a delta for every point. The build leaves some out and the renderer infers
them from their neighbours ("IUP"). Which ones it leaves out depends on the whole contour, so redrawing the wedge
can change the choice for points far from it, and an inferred delta can differ from the stored one by up to half
a unit: enough to land a point one unit off at some in-between weights.

What this does, for the named glyphs only: every point outside the wedge gets back exactly what the untouched
build stores for it (the same whole-number delta, or the same "infer it"); the wedge's own points get their true
deltas, stored explicitly. It then checks that every inferred point outside the wedge resolves to exactly the
value it has in the untouched font. No outline in glyf is touched; no other glyph's deltas are touched.
PATCHED_VF_ALL_DELTAS_EXPLICIT is the same source built with fontmake --no-optimize-gvar: it supplies the true deltas."""
import sys
KIT = '/home/claude/kit/basedrive-wedge-handover-kit'
sys.path.insert(0, KIT); sys.path.insert(0, '/home/claude/scripts')
import wedge_rule as wr
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.iup import iup_delta

def parts(font, name):
    coords, ctrl = font['glyf']._getCoordinatesAndControls(name, font['hmtx'].metrics)
    tv = font['gvar'].variations[name]
    assert len(tv) == 1 and list(tv[0].axes.values()) == [(0.0, 1.0, 1.0)], name
    return [tuple(c) for c in coords], list(ctrl.endPts), list(ctrl.flags), tv[0]

import outside_points as OP

def main(p_orig, p_new, p_true, p_out, names):
    fo, fn, ft = TTFont(p_orig), TTFont(p_new), TTFont(p_true)
    total = dict(points=0, restored=0, made_explicit=0, wedge=0)
    for name in names:
        co, eo, flo, tvo = parts(fo, name); cn, en, fln, tvn = parts(fn, name); ct, et, flt, tvt = parts(ft, name)
        assert cn == ct and en == et and list(fln) == list(flt), '%s: the two patched builds do not share one default outline' % name
        true = list(tvt.coordinates); assert None not in true, name
        old = list(tvo.coordinates)
        pairs, left_out = OP.pairs_outside(fo, name, co, eo, flo, cn, en, fln)
        outside = set(b for a, b in pairs)
        new = [tuple(d) for d in true]                         # wedge points: true deltas, explicit
        for a, b in pairs:
            if old[a] is not None and tuple(old[a]) != tuple(true[b]):
                raise SystemExit('%s: point %d has stored delta %s in the untouched font but true delta %s in the patched one' % (name, a, old[a], true[b]))
            new[b] = None if old[a] is None else tuple(old[a])
        eff_old = iup_delta(old, co, eo) if None in old else old
        # every inferred point outside the wedge must resolve to the value it has in the untouched font
        for _round in range(8):
            eff_new = iup_delta(new, cn, en) if None in new else new
            off = [(a, b) for a, b in pairs if abs(eff_new[b][0] - eff_old[a][0]) > 1e-9 or abs(eff_new[b][1] - eff_old[a][1]) > 1e-9]
            if not off: break
            for a, b in off:                                   # its neighbours changed: store the nearest whole delta instead
                new[b] = (int(round(eff_old[a][0])), int(round(eff_old[a][1]))); total['made_explicit'] += 1
        eff_new = iup_delta(new, cn, en) if None in new else new
        worst = max(max(abs(eff_new[b][0] - eff_old[a][0]), abs(eff_new[b][1] - eff_old[a][1])) for a, b in pairs)
        # the wedge's own points: explicit true deltas
        assert all(new[i] is not None and tuple(new[i]) == tuple(true[i]) for i in range(len(new)) if i not in outside), name
        fn['gvar'].variations[name] = [TupleVariation(dict(tvn.axes), new)]
        total['points'] += len(pairs); total['restored'] += sum(1 for a, b in pairs if new[b] == (None if old[a] is None else tuple(old[a])))
        total['wedge'] += len(new) - len(pairs)
        stored_before = sum(1 for d in tvn.coordinates if d is not None); stored_after = sum(1 for d in new if d is not None)
        print('  %-12s %3d points outside, largest difference in resolved delta %.3g; redrawn points with true deltas %d%s; deltas stored %d -> %d' % (
            name, len(pairs), worst, len(new) - len(pairs), (' (the wedge, and the landing with the letter\'s next curve: %d original points)' % left_out) if left_out else '', stored_before, stored_after))
    fn.save(p_out)
    print('%d outside points on %d glyphs: %d carry exactly what the untouched font stores; %d had to be stored as the nearest whole delta' % (
        total['points'], len(names), total['restored'], total['made_explicit']))
    return total

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
