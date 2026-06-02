"""Builder for the FlowR2A project page.

Pulls the curated qualitative gallery from
 ../paper/69b90d5cd9d4bdcb2d603ac2/supplementary/supplementary/index.html
and embeds it into a Nerfies-style project page.
Run from the flowr2a-project-page/ directory:
    python build.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
SUPP = ROOT.parent / "paper" / "69b90d5cd9d4bdcb2d603ac2" / "supplementary" / "supplementary" / "index.html"

# ---- Pull <main>...</main> from supplementary and rewrite asset paths ----
supp_html = SUPP.read_text(encoding="utf-8")
m = re.search(r"<main>(.*?)</main>", supp_html, flags=re.DOTALL)
if not m:
    raise SystemExit("Could not find <main> in supplementary index.html")
qual = m.group(1)

# Strip the supp's own A/B section headers + B.1/B.2 sticky-nav anchors —
# we re-frame this as the project page's qualitative section, so its own
# "A. Video Comparisons" / "B. Frame Comparisons" h2/h3 wording stays, but
# we relabel A/B to be cleaner.
qual = qual.replace(
    '<h2>A. Video Comparisons</h2>',
    '<h3 class="gallery-title">Video comparisons</h3>'
)
qual = qual.replace(
    '<h2>B. Frame Comparisons</h2>',
    '<h3 class="gallery-title" style="margin-top:36px">Per-frame comparisons</h3>'
)
qual = qual.replace('<h3>B.1  Forward Scenes</h3>', '<h3>Forward scenes</h3>')
qual = qual.replace('<h3>B.2  Turning Scenes</h3>', '<h3>Turning scenes</h3>')

# Rewrite asset paths: images/ -> static/qualitative/frames/, videos/ -> static/qualitative/videos/
qual = re.sub(r'src="images/', 'src="static/qualitative/frames/', qual)
qual = re.sub(r'src="videos/', 'src="static/qualitative/videos/', qual)

# Strip per-card "header" rows that show the clip id + scenario tags.
# Each .video-card and .frame-card has a <div class="card-header">...</div> we want gone.
qual = re.sub(
    r'<div class="card-header">.*?</div>',
    '',
    qual,
    flags=re.DOTALL,
)
# Also strip the per-clip frame-tabs (for entries like 319-0/2/4 with multiple frames):
# keep only the first .frame-panel.active and remove the rest + the tabs button row.
qual = re.sub(r'<div class="frame-tabs">.*?</div>', '', qual, flags=re.DOTALL)
qual = re.sub(
    r'(<div class="frame-panel active"[^>]*>.*?</div>)(\s*<div class="frame-panel"[^>]*>.*?</div>)+',
    r'\1',
    qual,
    flags=re.DOTALL,
)

# Strip the repeated per-table <thead>...</thead> in the frame comparisons —
# we'll show one shared column header per subsection instead.
qual = re.sub(r'<thead>.*?</thead>', '', qual, flags=re.DOTALL)
# Inject one shared column header at the top of each subsection (just after its <h3>).
SHARED_HEADER = (
    '<div class="compare-header">'
    '<div>DiffusionDrive</div>'
    '<div>DiffusionDriveV2</div>'
    '<div>iPad</div>'
    '<div class="ours">FlowR2A (ours)</div>'
    '</div>'
)
qual = qual.replace(
    '<h3>Forward scenes</h3>',
    '<h3>Forward scenes</h3>' + SHARED_HEADER,
)
qual = qual.replace(
    '<h3>Turning scenes</h3>',
    '<h3>Turning scenes</h3>' + SHARED_HEADER,
)
# Same compare-header above the GIF gallery — each GIF tile shows the four
# planners side-by-side, so the column labels apply there too.
qual = qual.replace(
    '<h3 class="gallery-title">Video comparisons</h3>',
    '<h3 class="gallery-title">Video comparisons</h3>' + SHARED_HEADER,
)

# ---- Compose the page ----
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlowR2A: Learning Reward-to-Action Distribution for Multimodal Driving Planning</title>
<meta name="description" content="FlowR2A learns the reward-conditioned action distribution p(a|r) with flow matching, achieving SOTA multimodal planning on NAVSIM.">
<link rel="stylesheet" href="static/css/index.css">
</head>
<body>
"""

HERO = """
<header class="hero">
  <h1 class="paper-title">FlowR2A: Learning Reward-to-Action Distribution<br>for Multimodal Driving Planning</h1>
  <p class="authors">
    <a href="https://lixirui142.github.io/">Xirui Li</a><sup>1</sup>,
    <a href="https://happinesslz.github.io/">Zhe Liu</a><sup>1</sup>,
    <a href="https://shuluoshu.github.io/">Xiaoqing Ye</a><sup>2</sup>,
    Wenhua Han<sup>2</sup>,
    Yifeng Pan<sup>2</sup>,
    Junyu Han<sup>2</sup>,
    <a href="https://i.cs.hku.hk/~hszhao/index.html">Hengshuang Zhao</a><sup>1</sup>
  </p>
  <p class="affil">
    <sup>1</sup>The University of Hong Kong &nbsp;&nbsp;
    <sup>2</sup>Changan Automobile
  </p>
  <div class="badges">
    <a class="badge" href="static/FlowR2A.pdf"><span>Paper</span></a>
    <a class="badge" href="#"><span>arXiv</span></a>
    <a class="badge" href="https://github.com/lixirui142/FlowR2A"><span>Code</span></a>
    <a class="badge" href="#bibtex"><span>BibTeX</span></a>
  </div>
</header>

<section class="tldr">
  <div class="tldr-card">
    <strong>TL;DR.</strong>
    Instead of treating simulation rewards as discriminative targets, FlowR2A treats them as a <em>condition</em>. A flow-matching decoder learns the reward-to-action distribution <em>p(a&nbsp;|&nbsp;r)</em> from dense trajectory&ndash;reward pairs, unifying dense supervision with generative proposal modeling.
  </div>
</section>

<section class="section" id="teaser">
  <div class="teaser-wrap">
    <video id="teaser-video" autoplay muted loop playsinline>
      <source src="static/videos/teaser.mp4" type="video/mp4">
    </video>
  </div>
</section>

<nav class="sticky-nav"><div class="inner">
  <a href="#results">Results</a>
  <a href="#framework">Framework</a>
  <a href="#bibtex">BibTeX</a>
</div></nav>
"""

RESULTS_OPEN = """
<section class="section" id="results">
  <h2>Results</h2>
  <p class="section-desc">
    Analyses of FlowR2A's proposal quality and controllable sampling, followed by qualitative
    comparisons against DiffusionDrive, DiffusionDriveV2, and iPad on NAVSIM navtest.
  </p>
"""

RESULTS_CLOSE = "</section>"

# The supplementary <main> already contains the gallery <section>s; we prepend a
# qualitative subhead with its own one-line description (mentions the PDMS color scale).
QUALITATIVE = (
    '<h3 class="gallery-title results-subhead">Qualitative comparison</h3>'
    '<p class="section-desc">'
    'Side-by-side comparisons against DiffusionDrive, DiffusionDriveV2, and iPad. We show '
    '<em>all</em> proposals generated by each planner, colored by PDMS from '
    '0 (<span class="pdms-red">red</span>) to 1 (<span class="pdms-green">green</span>).'
    '</p>'
) + qual

FRAMEWORK = """
<section class="section" id="framework">
  <h2>Framework</h2>
  <p class="section-desc" style="max-width:none">FlowR2A unifies the dense reward supervision of scoring-based methods with the dynamic proposal generation of anchor-based methods, all within a single generative model.</p>

  <figure class="framework-fig">
    <img src="static/images/pipeline-v2.png" alt="Training pipeline of FlowR2A">
    <figcaption>
      <strong>Training.</strong> A flow-matching action decoder is conditioned on fine-grained reward signals (safety, progress, comfort, rule compliance) injected via AdaLN. Every action&ndash;reward pair from simulation becomes a valid training sample, so the model internalizes the correlation between an action and its outcomes rather than imitating a single ground-truth trajectory.
    </figcaption>
  </figure>

  <figure class="framework-fig">
    <img src="static/images/inference.png" alt="Inference pipeline of FlowR2A">
    <figcaption>
      <strong>Inference.</strong> Classifier-free reward guidance plus zero-shot anchored sampling span a 2D space of (score target, initial noise level). This produces a diverse set of high-quality proposals that a lightweight mode selector ranks for the final action.
    </figcaption>
  </figure>
</section>
"""

EXPERIMENTS = """
  <h3 class="gallery-title results-subhead" style="margin-top:8px">Proposal quality</h3>
  <p class="section-desc">FlowR2A produces consistently high-quality proposal candidates, surpassing the prior multimodal planner iPad on both single and average proposal quality.</p>
  <div class="exp-card exp-full">
    <img src="static/images/topk_comparison_linear_v2.png" alt="top-k comparison">
    <p>FlowR2A's top-K proposals dominate prior planners across K.</p>
  </div>

  <h3 class="gallery-title results-subhead">Interactive sampling space</h3>
  <p class="section-desc">FlowR2A offers flexible sampling control through two intuitive knobs: a reward target <em>r<sub>high</sub></em> steers proposals toward higher-PDMS regions, and an initial noise level <em>t<sub>init</sub></em> trades anchor fidelity for sampling diversity.</p>
  <div class="exp-card exp-full">
    <div class="sampling-interactive">
      <div class="sampling-controls">
        <div class="slider-row">
          <label>Reward target <em>r<sub>high</sub></em><span class="val" id="rhigh-val">0.90</span></label>
          <input type="range" id="rhigh-slider" min="0" max="3" step="1" value="2">
          <div class="ticks"><span>0.80</span><span>0.85</span><span>0.90</span><span>0.95</span></div>
        </div>
        <div class="slider-row">
          <label>Initial noise <em>t<sub>init</sub></em><span class="val" id="tinit-val">0.85</span></label>
          <input type="range" id="tinit-slider" min="0" max="4" step="1" value="2">
          <div class="ticks"><span>0.75</span><span>0.80</span><span>0.85</span><span>0.90</span><span>0.95</span></div>
        </div>
      </div>
      <div class="sampling-stage">
        <img id="sampling-stage-img" src="static/sampling_space/rhigh0.90_tinit0.85.png" alt="sampling space proposals">
      </div>
      <p class="sampling-hint">Higher <em>r<sub>high</sub></em> guides proposals toward higher-reward regions; higher <em>t<sub>init</sub></em> introduces more sampling diversity around the anchor.</p>
    </div>
  </div>
"""

BIBTEX = """
<section class="section" id="bibtex">
  <h2>BibTeX</h2>
  <div class="bibtex-wrap">
    <button class="bibtex-copy">Copy</button>
<pre>@article{flowr2a2026,
  title         = {FlowR2A: Learning Reward-to-Action Distribution for Multimodal Driving Planning},
  author        = {Li, Xirui and Liu, Zhe and Ye, Xiaoqing and Han, Wenhua and Pan, Yifeng and Han, Junyu and Zhao, Hengshuang},
  journal       = {arXiv preprint arXiv:XXXX.XXXXX},
  year          = {2026}
}</pre>
  </div>
</section>
"""

FOOTER = """
<footer class="page-footer">
  <p>Page template inspired by the <a href="https://github.com/nerfies/nerfies.github.io">Nerfies project page</a>.</p>
</footer>
<script src="static/js/index.js"></script>
</body>
</html>
"""

out = HEAD + HERO + RESULTS_OPEN + EXPERIMENTS + QUALITATIVE + RESULTS_CLOSE + FRAMEWORK + BIBTEX + FOOTER
(ROOT / "index.html").write_text(out, encoding="utf-8")
print(f"Wrote {ROOT/'index.html'}  ({len(out):,} bytes)")
