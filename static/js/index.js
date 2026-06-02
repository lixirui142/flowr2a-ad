(function () {
  // ---- Frame tab switcher (in qualitative gallery) ----
  document.querySelectorAll('.frame-card').forEach(function (card) {
    var tabs = card.querySelectorAll('.frame-tabs button');
    if (!tabs.length) return;
    tabs.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var frame = btn.getAttribute('data-frame');
        tabs.forEach(function (b) { b.classList.toggle('active', b === btn); });
        card.querySelectorAll('.frame-panel').forEach(function (p) {
          p.classList.toggle('active', p.getAttribute('data-frame') === frame);
        });
      });
    });
  });

  // ---- Lightbox ----
  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<img alt=""><div class="lb-caption"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img');
  var lbCap = lb.querySelector('.lb-caption');

  function openLightbox(src, caption) {
    lbImg.src = src;
    lbCap.textContent = caption || '';
    lb.classList.add('open');
  }
  function closeLightbox() {
    lb.classList.remove('open');
    lbImg.src = '';
  }
  lb.addEventListener('click', closeLightbox);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
  });
  document.body.addEventListener('click', function (e) {
    var t = e.target;
    if (t.tagName === 'IMG' && t.closest('.compare-table')) {
      var caption = t.getAttribute('data-caption') || t.alt || '';
      openLightbox(t.src, caption);
    }
  });

  // ---- Interactive sampling-space sliders ----
  var rVals = [0.80, 0.85, 0.90, 0.95];
  var tVals = [0.75, 0.80, 0.85, 0.90, 0.95];
  var rSlider = document.getElementById('rhigh-slider');
  var tSlider = document.getElementById('tinit-slider');
  var rOut = document.getElementById('rhigh-val');
  var tOut = document.getElementById('tinit-val');
  var stageImg = document.getElementById('sampling-stage-img');

  function fmt(v) { return v.toFixed(2); }
  function updateSampling() {
    if (!rSlider || !tSlider || !stageImg) return;
    var rv = rVals[parseInt(rSlider.value, 10)];
    var tv = tVals[parseInt(tSlider.value, 10)];
    rOut.textContent = fmt(rv);
    tOut.textContent = fmt(tv);
    var src = 'static/sampling_space/rhigh' + fmt(rv) + '_tinit' + fmt(tv) + '.png';
    stageImg.src = src;
  }
  if (rSlider && tSlider) {
    rSlider.addEventListener('input', updateSampling);
    tSlider.addEventListener('input', updateSampling);
    updateSampling();
    // Preload all 20 frames
    rVals.forEach(function (rv) {
      tVals.forEach(function (tv) {
        var im = new Image();
        im.src = 'static/sampling_space/rhigh' + fmt(rv) + '_tinit' + fmt(tv) + '.png';
      });
    });
  }

  // ---- BibTeX copy ----
  var copyBtn = document.querySelector('.bibtex-copy');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var pre = copyBtn.parentElement.querySelector('pre');
      if (!pre) return;
      navigator.clipboard.writeText(pre.textContent.trim()).then(function () {
        copyBtn.classList.add('copied');
        copyBtn.textContent = 'Copied!';
        setTimeout(function () {
          copyBtn.classList.remove('copied');
          copyBtn.textContent = 'Copy';
        }, 1500);
      });
    });
  }
})();
