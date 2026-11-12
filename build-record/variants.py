"""Alternative versions of the rule, for the decision exhibits only. Same construction as the kit's
wedge_rule.redraw_variable (route B: both masters redrawn inside the compiled variable font, explicit points,
no boolean operations), but the rule's numbers can be overridden per master and per glyph."""
import io, os, sys
sys.path.insert(0, '/home/claude/kit/basedrive-wedge-handover-kit')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wedge_rule as wr
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib import instancer

PHI = wr.PHI
VF = '/home/claude/upstream/Funnel/fonts/Funnel_Display/variable/FunnelDisplay[wght].ttf'

def ord_rule(font):
    """the rule run on the ordfeminine with its own stroke: same shares, cut level with its block's edge T.
    Its stroke is the width of its own stem: from the stem's outer edge S to the stem's inner vertical edge."""
    ci, w = wr.wedges_in_font(font)['ordfeminine']
    on = [(w['sx'] * x, y) for x, y, o in wr.glyph_contours(font['glyf']['ordfeminine'])[ci] if o]      # canonical x
    frame = (w['S'], w['B'], w['N'], w['Q'])
    cands = sorted(set(x for x, y in on if x > w['S'] and x not in frame and sum(1 for p in on if p[0] == x) >= 2))
    st = cands[0] - w['S']
    return dict(wider=st / PHI ** 2 - (w['Q'] - w['N']), deeper=float(w['T'] - w['H']), corner=st / PHI ** 2, join=st / PHI ** 3, stroke=float(st))

def build(light=None, heavy=None, glyph_rule=None, with_ord=False, path=VF):
    """light / heavy: f(base_rule) -> rule for that master. glyph_rule: f(master_index, name, wedge, rule) -> rule.
    Returns (variable TTFont, {name: (numbers light, numbers heavy)}, (rule light, rule heavy))."""
    vf = TTFont(path)
    axis = vf['fvar'].axes[0]
    hv = instancer.instantiateVariableFont(TTFont(path), {axis.axisTag: axis.maxValue})
    buf = io.BytesIO(); hv.save(buf); buf.seek(0); hv = TTFont(buf)
    ra, rb = wr.rule_for_font(vf), wr.rule_for_font(hv)
    if light: ra = light(dict(ra))
    if heavy: rb = heavy(dict(rb))
    wa_all, wb_all = wr.wedges_in_font(vf), wr.wedges_in_font(hv)
    names = wr.full_size(wa_all) + (['ordfeminine'] if with_ord else [])
    done = {}
    for name in names:
        old = vf['gvar'].variations[name]
        ci = wa_all[name][0]
        ca, cb = wr.glyph_contours(vf['glyf'][name]), wr.glyph_contours(hv['glyf'][name])
        r1, r2 = dict(ra), dict(rb)
        if name == 'ordfeminine': r1, r2 = ord_rule(vf), ord_rule(hv)
        if glyph_rule:
            r1 = glyph_rule(0, name, wa_all[name][1], r1); r2 = glyph_rule(1, name, wb_all[name][1], r2)
        ca[ci], w1, m1 = wr.apply_to_contour(ca[ci], r1, 1)
        cb[ci], w2, m2 = wr.apply_to_contour(cb[ci], r2, 1)
        if not (m1['buildable'] and m2['buildable']): raise ValueError('%s: not buildable' % name)
        pa, pb = [q for c in ca for q in c], [q for c in cb for q in c]
        assert [q[2] for q in pa] == [q[2] for q in pb]
        deltas = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(pa, pb)] + list(old[0].coordinates[-4:])
        vf['glyf'][name] = wr._glyph_from(ca)
        vf['gvar'].variations[name] = [TupleVariation(dict(old[0].axes), deltas)]
        done[name] = (m1, m2)
    buf = io.BytesIO(); vf.save(buf); buf.seek(0)
    return buf.getvalue(), done, (ra, rb)

def inst(data, wght):
    f = instancer.instantiateVariableFont(TTFont(io.BytesIO(data)), {'wght': wght})
    buf = io.BytesIO(); f.save(buf); buf.seek(0); return TTFont(buf)
