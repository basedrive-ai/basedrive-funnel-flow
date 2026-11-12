#!/usr/bin/env python3
"""Stage 3 patcher: the flip rules agreed on 12 Nov 2026. Every wedge is the b's wedge, flipped.

    python3 patch_stage3.py FunnelDisplay.glyphs "FunnelDisplay[wght].ttf" OUT.glyphs

  b              the master. Its wedge is drawn by the rule exactly as in stage 2 (patch_stage2.wedge_cubic_top):
                 block as the font draws it, corner, cut, round end, link to the landing point.
  d p q g        the b's nodes, mirrored onto the letter's own block.
  n eng m u a    the b's nodes, mirrored onto the letter's own block, landing included. For that the letter's
                 landing point (the node where the link meets the letter's own curve) slides sideways to where
                 the b's sits, measured from the block; its height stays the letter's own. The handle that
                 follows it slides by the same amount, so the letter's curve still leaves the landing level;
                 the far end of that curve and its handle do not move. On the a the join between stem and block
                 sits 4 units over, as the a's stem does in the original.
  r              Funnel's way: the b's nodes on the r's block, the round end 20 deeper (the r's own notch is
                 20 deeper in the original), the link leaving the round end in the b's direction and landing on
                 the r's own arm, which does not move.
  ordfeminine    as in stage 2: the rule with its own stroke.

The nodes are written as text into the node list of one path per glyph and master. No boolean or path-merging
operation; both masters get the same number and kind of nodes. Everything else is the kit's and stage 2's code."""
import io, math, os, sys
KIT = '/home/claude/kit/basedrive-wedge-handover-kit'
sys.path.insert(0, KIT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wedge_rule as wr
import patch_glyphs_source as P
import patch_stage2 as P2

COPY = ('d', 'p', 'q', 'g', 'n', 'eng', 'm', 'u', 'a')       # get the b's nodes
SLIDE = ('n', 'eng', 'm', 'u', 'a')                           # the only letters whose landing may slide
R = lambda v: int(round(v))

def on_grid(segs):
    """the b's wedge with every coordinate on the grid (the b sits unmirrored, so this is what the kit writes for it)"""
    g = lambda p: (R(p[0]), R(p[1]))
    return [(kind, None if handles is None else (g(handles[0]), g(handles[1])), g(end), smooth) for kind, handles, end, smooth in segs]

def copy_of_b(segs_b, wb, w):
    """the b's nodes moved onto another letter's block, in that letter's canonical frame. Returns (segs, dx)."""
    assert (w['N'] - w['B'], w['T'] - w['y0']) == (wb['N'] - wb['B'], wb['T'] - wb['y0']), 'block size differs from the b\'s'
    ox, oy = w['N'] - wb['N'], w['y0'] - wb['y0']
    ds = (w['S'] - w['N']) - (wb['S'] - wb['N'])                 # where the stem meets the block (0, or -4 on the a)
    dh = (w['P4'][1] - w['y0']) - (wb['P4'][1] - wb['y0'])       # the landing keeps the letter's own height
    dx = (wb['P4'][0] - wb['N']) - (w['P4'][0] - w['N'])         # how far the landing slides
    mv = lambda p, ex=0, ey=0: (p[0] + ox + ex, p[1] + oy + ey)
    out = []
    last = len(segs_b) - 1
    for k, (kind, handles, end, smooth) in enumerate(segs_b):
        if k == 0: out.append((kind, None, mv(end, ds), smooth))                                   # the stem line's new end
        elif k == 1: out.append((kind, (mv(handles[0], ds), mv(handles[1], ds)), mv(end, ds), smooth))  # the join
        elif k == last: out.append((kind, (mv(handles[0]), mv(handles[1], 0, dh)), mv(end, 0, dh), smooth))   # the link
        else: out.append((kind, None if handles is None else (mv(handles[0]), mv(handles[1])), mv(end), smooth))
    assert out[0][2][0] == w['S'] and out[2][2] == (w['B'], w['T']) and out[3][2] == (w['B'], w['y0']), 'the copy does not sit on this letter\'s block'
    assert out[last][2] == (w['P4'][0] + dx, w['P4'][1]) and out[last][1][1][1] == w['P4'][1], 'the link does not land level at the letter\'s height'
    return out, dx

def deeper_copy_of_b(segs_b, m_b, wb, w):
    """The r, Funnel's way: the b's nodes on the r's block, with the round end as much deeper as the r's own notch is
    deeper than the b's (20 units). The link leaves the round end in the b's direction and lands on the r's own
    landing point, which does not move. Returns segs in the r's canonical frame."""
    assert (w['N'] - w['B'], w['T'] - w['y0'], w['S'] - w['N']) == (wb['N'] - wb['B'], wb['T'] - wb['y0'], wb['S'] - wb['N']), 'the r\'s block is not the b\'s'
    ox, oy = w['N'] - wb['N'], w['y0'] - wb['y0']
    dd = (w['H'] - w['y0']) - (wb['H'] - wb['y0'])               # how much deeper the r's own notch is
    mv = lambda p, ey=0: (p[0] + ox, p[1] + oy + ey)
    out = []
    for k, (kind, handles, end, smooth) in enumerate(segs_b[:-1]):
        ey = dd if k >= 6 else 0                                 # from the end of the near wall on: the round end, deeper
        hy = dd if k >= 7 else 0
        out.append((kind, None if handles is None else (mv(handles[0], hy), mv(handles[1], hy)), mv(end, ey), smooth))
    E = out[-1][2]; b2 = out[-1][1][1]                           # the round end's last node and the handle before it
    P4 = w['P4']; te = (math.sin(m_b['al']), -math.cos(m_b['al']))   # the b's leaving direction
    s = (P4[1] - E[1]) / te[1]
    C = (E[0] + s * te[0], P4[1])                                # where that direction meets the level of the landing
    if not (s > 0 and C[0] < P4[0]): raise SystemExit('the r\'s link cannot land on its arm in the b\'s direction')
    w1 = (E[0] + 2 * (C[0] - E[0]) / 3, E[1] + 2 * (C[1] - E[1]) / 3)
    w2 = (R(P4[0] + 2 * (C[0] - P4[0]) / 3), P4[1])
    best = None
    for wx in range(int(math.floor(w1[0])) - 1, int(math.ceil(w1[0])) + 2):
        for wy in range(int(math.floor(w1[1])) - 1, int(math.ceil(w1[1])) + 2):
            dw = math.hypot(wx - w1[0], wy - w1[1])
            if dw > 1.0: continue
            ux, uy = wx - E[0], wy - E[1]; vx, vy = E[0] - b2[0], E[1] - b2[1]
            if ux * vx + uy * vy <= 0: continue
            ang = abs(math.degrees(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)))
            cost = (round(ang, 1), dw)
            if best is None or cost < best[0]: best = (cost, (wx, wy))
    out.append(('curve', (best[1], w2), (P4[0], P4[1]), True))
    assert out[2][2] == (w['B'], w['T']) and out[3][2] == (w['B'], w['y0']) and out[0][2][0] == w['S']
    return out

def nodes_from(old, ws, segs, dx):
    """The path's new node list from ready-made wedge segments (canonical frame). The kit's new_nodes, plus: the landing
    node and the handle after it slide dx along the stem-to-curve direction. old = [(x, y, code)]."""
    G = lambda p: (R(ws['sx'] * p[0]), R(ws['sy'] * p[1]))
    i = ws['index']; gdx = ws['sx'] * dx
    def slid(walk):
        """walk = the old nodes in walking order from P4 on"""
        walk = list(walk); moved = {}
        if dx:
            p4, h = walk[0], walk[1]
            if p4[2][0] == 'o' or h[2] != 'o' or h[1] != p4[1]: raise SystemExit('the letter\'s curve does not leave the landing level: %s %s' % (p4, h))
            walk[0] = (p4[0] + gdx, p4[1], p4[2]); walk[1] = (h[0] + gdx, h[1], h[2])
            moved = {p4: walk[0], h: walk[1]}
        return walk, moved
    if ws['direction'] == 1:
        run = []
        for k, (kind, handles, end, smooth) in enumerate(segs):
            if kind == 'curve': run += [G(handles[0]) + ('o',), G(handles[1]) + ('o',)]
            if k < len(segs) - 1: run.append(G(end) + (('c' if kind == 'curve' else 'l') + ('s' if smooth else ''),))
        seq = old[i:] + old[:i]
        rest, moved = slid(seq[8:])
        out = run + rest
    else:
        rev = old[::-1]; seq = rev[i:] + rev[:i]
        walk, moved = slid(seq[8:])
        rest = walk[::-1]
        run = []
        for k in range(len(segs) - 1, 0, -1):
            kind, handles, end, smooth = segs[k]
            if kind == 'curve': run += [G(handles[1]) + ('o',), G(handles[0]) + ('o',)]
            prev_end, prev_smooth = segs[k - 1][2], segs[k - 1][3]
            run.append(G(prev_end) + (('c' if kind == 'curve' else 'l') + ('s' if prev_smooth else ''),))
        out = rest + run
    # the landing node in the node list must be where the link ends
    land = G(segs[-1][2])
    if not any((q[0], q[1]) == land and q[2][0] != 'o' for q in out): raise SystemExit('the link does not end on the landing node')
    last = moved.get(old[-1], old[-1])                           # a Glyphs path is stored ending on its start node: keep it
    if last in out and last[2][0] != 'o': k = out.index(last)
    else: k = max(j for j, q in enumerate(out) if q[2][0] != 'o')
    return out[k + 1:] + out[:k + 1]

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
    if sorted(names) != sorted(('b', 'r', 'ordfeminine') + COPY): raise SystemExit('unexpected set of glyphs with a wedge: %s' % names)
    names = ['b'] + [n for n in names if n != 'b']
    src = glyphsLib.GSFont(source_path)
    masters = sorted(src.masters, key=lambda mm: mm.axes[0])
    if len(masters) != 2: raise SystemExit('expected two masters in the source, found %d' % len(masters))
    lines = open(source_path, encoding='utf-8').read().split('\n')
    code = {'line': 'l', 'curve': 'c', 'offcurve': 'o', 'qcurve': 'q'}
    done = []; b_of = {}
    for name in names:
        glyph = src.glyphs[name]
        if glyph is None: raise SystemExit('%s: not in the source' % name)
        for mi, (master, (font, wedges, base)) in enumerate(zip(masters, compiled)):
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
            dx = 0
            if name == 'b':
                rule = dict(base)
                segs, m = P2.wedge_cubic_top(wv, rule)
                segs = on_grid(segs); b_of[mi] = (segs, m, wv)
                how = 'the rule'
            elif name == 'ordfeminine':
                rule = P2.rule_for_glyph(name, wv, base, font)
                segs, m = P2.wedge_cubic_top(wv, rule); how = 'the rule, its own stroke'
            elif name == 'r':
                rule = dict(base); segs_b, m_b, wb = b_of[mi]
                keep = wr.leaving_angle; wr.leaving_angle = lambda *x, **k: (0.0, m_b['al'])
                try: m = wr.wedge_numbers(wv, rule)                                        # the r's numbers, for the record and the buildable test
                finally: wr.leaving_angle = keep
                segs = deeper_copy_of_b(segs_b, m_b, wb, wv)
                how = 'the b\'s nodes, cut 20 deeper, own arm'
            else:
                segs_b, m, wb = b_of[mi]; rule = dict(base)
                segs, dx = copy_of_b(segs_b, wb, wv); how = 'the b\'s nodes'
                if dx and name not in SLIDE: raise SystemExit('%s, master %s: its landing is not where the b\'s is (%+d)' % (name, master.name, dx))
            if not m['buildable']: raise SystemExit('%s, master %s: the rule is not buildable here' % (name, master.name))
            new = nodes_from(old, ws, segs, dx)
            text = ['(%s,%s,%s)' % q for q in new]
            lines[a:b] = [t + ',' for t in text[:-1]] + [text[-1]]
            done.append((name, master.name, len(old), len(new), how, dx, (wv['S'] - wv['N']) - (b_of[mi][2]['S'] - b_of[mi][2]['N']) if name != 'ordfeminine' else 0,
                         (wv['P4'][1] - wv['y0']) - (b_of[mi][2]['P4'][1] - b_of[mi][2]['y0']) if name != 'ordfeminine' else 0, m))
    with open(out_path, 'w', encoding='utf-8', newline='') as fh:
        fh.write('\n'.join(lines))
    return done

if __name__ == '__main__':
    rows = patch(sys.argv[1], sys.argv[2], sys.argv[3])
    print('glyph        master   nodes before -> after   drawn from                              landing slides  stem over  landing height vs the b\'s   cut')
    for name, master, n0, n1, how, dx, ds, dh, m in rows:
        print('%-12s %-8s %3d -> %-3d              %-38s  %+4d            %+3d        %+3d                        %5.1f x %-5g' % (name, master, n0, n1, how, dx, ds, dh, m['width'], m['depth']))
    print('%d paths rewritten in %s' % (len(rows), sys.argv[3]))
