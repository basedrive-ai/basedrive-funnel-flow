#!/usr/bin/env python3
"""Stage 2 patcher: the kit's patcher with the three changes decided on 12 Nov 2026.

    python3 patch_stage2.py FunnelDisplay.glyphs "FunnelDisplay[wght].ttf" OUT.glyphs [--round-end handover]

  decision 3  the m's cut is as wide as every other letter's: stroke / phi^2 (the kit reads the m's own, wider notch)
  decision 4  the ordfeminine gets the rule with its own stroke (the kit skips it as a reduced copy)
  decision 7  the round end's two cubics meet at its top, and E, the handle before it and the far wall's first
              handle are rounded together so the three lie on one line (the kit splits the round end at half its
              sweep and rounds every point on its own). --round-end handover keeps the kit's construction.

Everything else is the kit's: wedge_rule.wedge_numbers and cubic_arc for the geometry, patch_glyphs_source for
finding the wedge in the source and writing the node lists as text. No boolean or path-merging operations.
"""
import io, math, os, sys
KIT = '/home/claude/kit/basedrive-wedge-handover-kit'
sys.path.insert(0, KIT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wedge_rule as wr
import patch_glyphs_source as P
import variants as VV

_kit_wedge_cubic = wr.wedge_cubic

def wedge_cubic_top(w, rule):
    m = wr.wedge_numbers(w, rule)
    S, B, N, y0, T = w['S'], w['B'], w['N'], w['y0'], w['T']
    Rc, Rj, r = m['Rc'], m['Rj'], m['r']
    E, C, P4 = m['E'], m['C'], m['P4']
    centre = (m['cx'], m['cy'])
    j1, j2, j_end = wr.cubic_arc((S - Rj, T + Rj), Rj, 0.0, -math.pi / 2)
    c1, c2, c_end = wr.cubic_arc((N - Rc, y0 + Rc), Rc, -math.pi / 2, 0.0)
    a1, a2, a_end = wr.cubic_arc(centre, r, math.pi, math.pi / 2)          # near wall to the top
    b1, b2, b_end = wr.cubic_arc(centre, r, math.pi / 2, m['al'])          # top to E
    w1 = (E[0] + 2 * (C[0] - E[0]) / 3, E[1] + 2 * (C[1] - E[1]) / 3)      # far wall = the quadratic E, C, P4 raised to a cubic
    w2 = (P4[0] + 2 * (C[0] - P4[0]) / 3, P4[1] + 2 * (C[1] - P4[1]) / 3)
    R = lambda v: int(math.floor(v + 0.5))
    # the top node and its two handles share one y: exactly horizontal after rounding
    top = (R(a_end[0]), R(a_end[1])); a2 = (R(a2[0]), top[1]); b1 = (R(b1[0]), top[1])
    # E, the handle before it and the handle after it, rounded together onto one line.
    # None moves more than about a unit from where the geometry puts it.
    best = None
    for ex in (math.floor(E[0]), math.ceil(E[0])):
        for ey in (math.floor(E[1]), math.ceil(E[1])):
            dE = math.hypot(ex - E[0], ey - E[1])
            for wx in range(R(w1[0]) - 1, R(w1[0]) + 2):
                for wy in range(R(w1[1]) - 1, R(w1[1]) + 2):
                    dw = math.hypot(wx - w1[0], wy - w1[1])
                    if dw > 1.0: continue
                    ux, uy = wx - ex, wy - ey
                    for hx in range(math.floor(b2[0]) - 1, math.ceil(b2[0]) + 2):
                        for hy in range(math.floor(b2[1]) - 1, math.ceil(b2[1]) + 2):
                            dh = math.hypot(hx - b2[0], hy - b2[1])
                            if dh > 1.25 or (hx, hy) == (ex, ey): continue
                            vx, vy = ex - hx, ey - hy
                            if vx * ux + vy * uy <= 0: continue
                            ang = abs(math.degrees(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)))
                            cost = (round(ang, 1), dE + dh + dw)
                            if best is None or cost < best[0]: best = (cost, (ex, ey), (hx, hy), (wx, wy))
    Er, b2r, w1r = best[1], best[2], best[3]
    segs = [('line', None, (S, T + Rj), True),
            ('curve', (j1, j2), (S - Rj, T), True),
            ('line', None, (B, T), False),
            ('line', None, (B, y0), False),
            ('line', None, (N - Rc, y0), True),
            ('curve', (c1, c2), (N, y0 + Rc), True),
            ('line', None, (N, m['cy']), True),
            ('curve', (a1, a2), top, True),
            ('curve', (b1, b2r), Er, True),
            ('curve', (w1r, w2), (P4[0], P4[1]), True)]
    return segs, m

def rule_for_glyph(name, wedge, base_rule, font):
    """the rule's numbers for one glyph at one master"""
    if name == 'ordfeminine':
        return VV.ord_rule(font)                                   # decision 4: same shares of its own stroke
    r = dict(base_rule)
    if name == 'm':
        r['wider'] = r['corner'] - (wedge['Q'] - wedge['N'])       # decision 3: cut width = stroke / phi^2, as on every other letter
    return r

def patch(source_path, vf_path, out_path):
    import glyphsLib
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    vf = TTFont(vf_path)
    axis = vf['fvar'].axes[0]
    heavy = instancer.instantiateVariableFont(TTFont(vf_path), {axis.axisTag: axis.maxValue})
    buf = io.BytesIO(); heavy.save(buf); buf.seek(0); heavy = TTFont(buf)
    compiled = [(vf, wr.wedges_in_font(vf), wr.rule_for_font(vf)), (heavy, wr.wedges_in_font(heavy), wr.rule_for_font(heavy))]
    names = wr.full_size(compiled[0][1]) + ['ordfeminine']
    src = glyphsLib.GSFont(source_path)
    masters = sorted(src.masters, key=lambda mm: mm.axes[0])
    if len(masters) != 2: raise SystemExit('expected two masters in the source, found %d' % len(masters))
    lines = open(source_path, encoding='utf-8').read().split('\n')
    code = {'line': 'l', 'curve': 'c', 'offcurve': 'o', 'qcurve': 'q'}
    done = []
    for name in names:
        glyph = src.glyphs[name]
        if glyph is None: raise SystemExit('%s: not in the source' % name)
        for master, (font, wedges, base) in zip(masters, compiled):
            layer = glyph.layers[master.id]
            hits = []
            for pi, path in enumerate(layer.paths):
                ws = P.find_in_source([(nd.position.x, nd.position.y, nd.type) for nd in path.nodes])
                if ws: hits.append((pi, ws))
            if len(hits) != 1: raise SystemExit('%s, master %s: expected one wedge, found %d' % (name, master.name, len(hits)))
            pi, ws = hits[0]
            wv = wedges[name][1]
            if any(ws[k] != wv[k] for k in P.FRAME_KEYS) or tuple(ws['P0']) != tuple(wv['P0']) or tuple(ws['P4']) != tuple(wv['P4']):
                raise SystemExit('%s, master %s: the source and the compiled font do not show the same wedge' % (name, master.name))
            g0 = lines.index('glyphname = %s;' % name)
            g1 = next((j for j in range(g0 + 1, len(lines)) if lines[j].startswith('glyphname = ')), len(lines))
            ids = [j for j in range(g0, g1) if lines[j] in ('layerId = "%s";' % master.id, 'layerId = %s;' % master.id)]
            if len(ids) != 1: raise SystemExit('%s, master %s: layer not found in the text' % (name, master.name))
            sh = next(j for j in range(ids[0], g1) if lines[j] == 'shapes = (')
            starts = [j for j in range(sh, g1) if lines[j] == 'nodes = (']
            a = starts[pi] + 1
            b = next(j for j in range(a, g1) if lines[j] == ');')
            old = []
            for ln in lines[a:b]:
                mt = P.NODE.match(ln)
                if not mt or mt.group(4): raise SystemExit('%s, master %s: a node line this script does not understand: %s' % (name, master.name, ln))
                num = lambda t: float(t) if '.' in t else int(t)
                old.append((num(mt.group(1)), num(mt.group(2)), mt.group(3)))
            want = [(nd.position.x, nd.position.y, code[nd.type] + ('s' if nd.smooth else '')) for nd in P.path_nodes(layer, pi)]
            if [(float(x), float(y), t) for x, y, t in old] != [(float(x), float(y), t) for x, y, t in want]:
                raise SystemExit('%s, master %s: the text found is not the path that was measured' % (name, master.name))
            rule = rule_for_glyph(name, wv, base, font)
            new, m = P.new_nodes(old, ws, wv, rule)
            if not m['buildable']: raise SystemExit('%s, master %s: the rule is not buildable here' % (name, master.name))
            text = ['(%s,%s,%s)' % q for q in new]
            lines[a:b] = [t + ',' for t in text[:-1]] + [text[-1]]
            done.append((name, master.name, len(old), len(new), m, rule))
    with open(out_path, 'w', encoding='utf-8', newline='') as fh:
        fh.write('\n'.join(lines))
    return done

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    handover_round_end = '--round-end' in sys.argv and sys.argv[sys.argv.index('--round-end') + 1] == 'handover'
    if handover_round_end: args = [a for a in args if a != 'handover']
    wr.wedge_cubic = _kit_wedge_cubic if handover_round_end else wedge_cubic_top       # patch_glyphs_source.new_nodes calls wr.wedge_cubic
    rows = patch(args[0], args[1], args[2])
    print('round end: %s' % ('as the handover writes it' if handover_round_end else 'node at the top, E rounded on the tangent'))
    print('glyph        master   nodes before -> after   own stroke  font notch   cut            corner  join   neck')
    for name, master, n0, n1, m, rule in rows:
        print('%-12s %-8s %3d -> %-3d              %5.0f       %d x %-5d  %5.1f x %-5g  %5.1f  %5.1f  %6.1f' % (
            name, master, n0, n1, rule['stroke'], m['notch_w'], m['notch_d'], m['width'], m['depth'], m['Rc'], m['Rj'], m['neck']))
    print('%d paths rewritten in %s' % (len(rows), args[2]))
