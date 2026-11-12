# Basedrive Funnel Flow

From: [basedrive.ai](https://basedrive.ai)

![The Basedrive wordmark set in Basedrive Funnel Flow](artwork/basedrive-wordmark.png)

> **Note:** This font has not been thoroughly tested yet, so expect minor changes. Non-English
> characters (accented letters and other characters outside basic English) are not yet fully tested.

## Before and after

| Before: Funnel Display | After: Basedrive Funnel Flow |
| --- | --- |
| ![A pangram set in the original Funnel Display](artwork/funnel-display-original-the-quick-brown-fox-jumps-over-t-3600x2400.png) | ![The same pangram set in Basedrive Funnel Flow](artwork/basedrive-funnel-flow-the-quick-brown-fox-jumps-over-t-3600x2400.png) |

Funnel Display has a small block that steps out from the stem of some letters, with a square
notch beside it. In Basedrive Funnel Flow that notch becomes a deeper, round-ended cut, and a
curve flows from it back into the letter. Look at the q, u, b, r, n, m, p, a, d and g above.

- **Twelve letters change:** `a b d g m n ŋ p q r u ª`, plus their accented forms.
- **Nothing else changes:** every other glyph, the spacing and the kerning are the same, so text
  takes exactly the space it takes in Funnel Display.

## In use

![Basedrive headline: Unify your customers, work and business operations on one base](artwork/basedrive-funnel-flow-unify-your-customers-work-and-bu-3600x2400.png)

![Big number: 1,284,907 rows synced today](artwork/basedrive-funnel-flow-1-284-907-3600x2400.png)

![Dashboard figures for revenue, orders and refunds](artwork/basedrive-funnel-flow-revenue-48-200-3600x2400.png)

![All six weights, from Light to ExtraBold](artwork/basedrive-funnel-flow-light-3600x2400.png)

![The alphabet in capitals and lowercase, with numerals](artwork/basedrive-funnel-flow-abcdefghijklmnopqrs-3600x2400.png)

![Numerals, currency and percentages](artwork/basedrive-funnel-flow-0123456789-3600x2400.png)

![A news headline](artwork/basedrive-funnel-flow-city-approves-new-tram-line-afte-3600x2400.png)

![A café menu with prices](artwork/basedrive-funnel-flow-flat-white-4-20-3600x2400.png)

![A bank payment alert](artwork/basedrive-funnel-flow-you-paid-48-20-at-green-grocer-3600x2400.png)

![A weather reading](artwork/basedrive-funnel-flow-18-3600x2400.png)

![An error message from a rail app](artwork/basedrive-funnel-flow-no-trains-found-3600x2400.png)

![A paragraph from a recipe](artwork/basedrive-funnel-flow-warm-the-oil-in-a-wide-pan-and-s-3600x2400.png)

![Insurance small print](artwork/basedrive-funnel-flow-cover-starts-on-the-date-shown-i-3600x2400.png)

These images were made with the [editor](editor.html) in this repository.

## Release

Release candidate 2 (flip rules), 12 November 2026. This replaces the candidate of the same name
made earlier that day, in which each letter's wedge was fitted to the letter separately.

## What this is

A modified version of [Funnel Display](https://github.com/Dicotype/Funnel) 1.001 by The Funnel
Project Authors (upstream commit
[`5f3a46a`](https://github.com/Dicotype/Funnel/commit/5f3a46a76b89b91e47d9c191042c91d73b7479c9)).
On twelve glyphs, the square notch beside the wedge block is redrawn as a deeper, round-ended
cut. The wedge is the same shape on every letter: the b's, mirrored. Every other glyph, all
advance widths, side bearings, kerning and vertical metrics are upstream's. Text set in this
family takes exactly the space it takes in Funnel Display.

Weights: Light (300), Regular (400), Medium (500), SemiBold (600), Bold (700) and
ExtraBold (800). There is also a variable font covering 300–800.

## How this was made (please read)

The design was done carefully by human eye: the wedge was drawn, compared and approved by
looking at it. Most of the production work was done by an AI assistant (Claude, by Anthropic):
patching the Glyphs source, generating the font files, and writing and running the tests. The
source has not been opened in the Glyphs app, and the fonts have not been proofed in print or
tried in every application. Please test them in your own setting before relying on them for
anything critical.

## Files

| Folder | Contents |
| --- | --- |
| [`variable/`](variable/) | `BasedriveFunnelFlow[wght].ttf`, weight 300–800 |
| [`ttf/`](ttf/) | Six static TrueType files, autohinted with ttfautohint 1.8.4.16 |
| [`otf/`](otf/) | Six static OpenType (CFF) files |
| [`webfonts/`](webfonts/) | WOFF2 versions of the variable font and of each static TrueType file |
| [`sources/`](sources/) | `BasedriveFunnelFlow.glyphs` (the patched Glyphs source) and `config_display.yaml` (the build recipe) |
| [`build-record/`](build-record/) | The scripts as they were run, and the exact tool versions |

## Try it in the browser

[Open the editor](https://basedrive-ai.github.io/basedrive-funnel-flow/editor.html) to type your own text, change the
weight, size and colours, load sample texts, and download the result as a PNG. The same page is
[`editor.html`](editor.html) in this repository; it also works when opened from a local copy of the repo.

## Use on the web

```css
@font-face {
  font-family: "Basedrive Funnel Flow";
  src: url("webfonts/BasedriveFunnelFlow[wght].woff2") format("woff2-variations"),
       url("webfonts/BasedriveFunnelFlow[wght].woff2") format("woff2");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
}

body {
  font-family: "Basedrive Funnel Flow", sans-serif;
}
```

On the desktop, install either the variable font or the static files from `otf/` or `ttf/`.
Don't install both, or the apps may show duplicate entries.

## What was changed in the design

Glyphs redrawn: `a b d g m n eng p q r u` and `ordfeminine`, in both masters (Light and
ExtraBold). 29 accented letters follow their base letter. There are no other outline changes.

The wedge has three parts:

- **the block:** upstream's square, untouched;
- **the cut:** the round-ended slot beside the block;
- **the link:** the curve from the cut back into the letter.

| Glyph | Rule |
| --- | --- |
| `b` | The master. The cut is stroke / φ² wide (0.38 of the stroke) and ends level with the block's inner edge. The block's corner beside the cut has radius stroke / φ², and the join between block and stem has radius stroke / φ³. The link is one curve from the round end to the point where it lands on the bowl. |
| `d p q` | The b, mirrored (the whole letter, as in upstream). |
| `g` | The b's wedge, mirrored. |
| `n eng m u a` | The b's wedge, mirrored, landing included. For this, the point where the link lands on the letter's own curve slides sideways to where the b's sits: n and eng 5 to 6 units toward the stem, m 3 to 6 away from it, u 8 toward it, and a from 6 toward it at Light to 4 away at ExtraBold. The one curve of the letter that starts there is adjusted at that end; its far end does not move. The landing keeps the letter's own height, 1 unit from the b's. On the a, the stem meets the block 4 units over, as in upstream. |
| `r` | As Funnel Display treats it: the b's block and cut, with the cut 20 units deeper (the r's notch is 20 deeper in upstream). The link leaves in the b's direction and lands on the r's own arm, which is unchanged. |
| `ordfeminine` | The same rule, from its own smaller stroke. |

Every wedge is written into the source as an explicit list of nodes. No boolean or
path-merging operation was used on the masters.

## What was changed in the names

- Family name: "Funnel Display" → "Basedrive Funnel Flow". This covers name records 1, 3, 4, 6,
  16 and 25, the instance PostScript names of the variable font, and the font names inside the
  OpenType files.
- Vendor code: "DICO" → blank.
- Unchanged from upstream: the weight names, the copyright, licence, maker and designer records,
  and the version (1.001).

The longest family-plus-weight name is 31 characters (ExtraBold), and the longest PostScript
name is 29.

## How it was built

1. Upstream's `sources/FunnelDisplay.glyphs` was patched as text by
   `build-record/patch_stage3.py`; only the node lines of 24 paths change. Then the family name
   and vendor code were changed.
2. `gftools builder` was run on `sources/config_display.yaml`, which is upstream's recipe with
   the family name changed. Tool versions: gftools 0.10.8, fontmake 3.12.2, glyphsLib 6.17.2,
   ufo2ft 3.11.0 and fontTools 4.68.0. The full list is in
   `build-record/requirements-as-built.txt`.
3. One step outside the recipe, applied to the variable font only:
   `build-record/pin_deltas_s3.py` restored the stored deltas of every point outside the
   redrawn parts of the twelve glyphs (the gvar table) to what the untouched build stores.
   Without it, some points of m, n and eng landed one unit off at in-between weights. The
   variable font's woff2 was then compressed again.

### Rebuilding

Running `gftools builder sources/config_display.yaml` writes to `fonts/Basedrive_Funnel_Flow/`,
which git ignores. A plain rebuild leaves out step 3 above, so its variable font is not
identical to the released one.

The scripts in `build-record/` are a record of what was run, not a runnable pipeline. They
contain paths from the build machine and need the wedge handover kit (`wedge_rule.py`,
`patch_glyphs_source.py`), which is not in this repository.

## Not done

The source has not been opened in the Glyphs app. glyphsLib reads it, fontmake builds it, and
the two masters of every redrawn glyph are compatible.

## Thank you

To NORD ID and Kristian Möller, who designed Funnel Display for Funnel, and to The Funnel
Project Authors, who released it under the SIL Open Font License. This family exists because of
their work. The original typeface: https://github.com/Dicotype/Funnel

## Licence

SIL Open Font License 1.1. See [OFL.txt](OFL.txt), which is upstream's file, unchanged. The
licence is also available, with a FAQ, at https://openfontlicense.org.

Copyright 2025 The Funnel Project Authors (https://github.com/Dicotype/Funnel).
No copyright line has been added for the modification.
