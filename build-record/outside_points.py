"""Which points of a redrawn glyph are 'outside': not part of the wedge and, on the letters whose landing slides
(n eng m u a), not part of the one curve of the letter that starts at the landing either.
Pairs (index in the untouched glyph, index in the patched glyph) of every outside point, phantom points included."""
import sys
sys.path.insert(0, '/home/claude/kit/basedrive-wedge-handover-kit')
import wedge_rule as wr
SLIDE = ('n', 'eng', 'm', 'u', 'a')

def pairs_outside(fo, name, co, eo, flo, cn, en, fln):
    """returns (pairs, original points left out after the eight wedge points: 0, or the landing plus the control points of the letter's next curve)"""
    ci, w = wr.wedges_in_font(fo)[name]
    so = [0] + [e + 1 for e in eo[:-1]]; sn = [0] + [e + 1 for e in en[:-1]]
    out = []; left_out = 0
    for k in range(len(eo)):
        io = list(range(so[k], eo[k] + 1)); inn = list(range(sn[k], en[k] + 1))
        if k != ci:
            assert len(io) == len(inn), name; out += list(zip(io, inn)); continue
        seq = io if w['direction'] == 1 else io[::-1]
        seq = seq[w['index']:] + seq[:w['index']]
        rest = seq[8:]                                  # the original points after the eight wedge points, starting at the landing
        seqn = inn if w['direction'] == 1 else inn[::-1]
        def find(idx):
            key = [(co[i], flo[i] & 1) for i in idx]
            for off in range(len(seqn)):
                cand = [seqn[(off + j) % len(seqn)] for j in range(len(idx))]
                if [(cn[i], fln[i] & 1) for i in cand] == key: return cand
            return None
        hit = find(rest)
        if hit is None:
            if name not in SLIDE: raise SystemExit('%s: a point outside the wedge has moved in the default outline' % name)
            assert w['p4_explicit'], name
            for j in range(1, 9):
                if not (flo[rest[j]] & 1): continue        # the curve ends on the next on-curve point
                hit = find(rest[j:]); left_out = j; break
            if hit is None: raise SystemExit('%s: more than the landing and the letter\'s next curve has moved' % name)
            rest = rest[left_out:]
        out += list(zip(rest, hit))
    no, nn = len(co) - 4, len(cn) - 4
    out += [(no + j, nn + j) for j in range(4)]
    assert all(co[a] == cn[b] for a, b in out), name
    return out, left_out
