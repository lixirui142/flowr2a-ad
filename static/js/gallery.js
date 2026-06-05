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

  // ---- Carousel: collapse long galleries into a single-slide window ----
  function buildCarousel(slides, header) {
    var wrap = document.createElement('div');
    wrap.className = 'carousel';
    wrap.tabIndex = 0;
    wrap.innerHTML =
      '<button type="button" class="carousel-btn carousel-prev" aria-label="Previous">&lsaquo;</button>' +
      '<div class="carousel-viewport">' +
        '<div class="carousel-track"></div>' +
        '<div class="carousel-counter"></div>' +
      '</div>' +
      '<button type="button" class="carousel-btn carousel-next" aria-label="Next">&rsaquo;</button>';
    var viewport = wrap.querySelector('.carousel-viewport');
    var track = wrap.querySelector('.carousel-track');
    var counter = wrap.querySelector('.carousel-counter');
    var prev = wrap.querySelector('.carousel-prev');
    var next = wrap.querySelector('.carousel-next');
    var syncTimer = null;

    // Move the column header inside the viewport so its columns line up
    // with the slide's content (the arrow buttons occupy outer grid cells).
    if (header) viewport.insertBefore(header, track);

    slides.forEach(function (s) {
      s.classList.remove('active');
      track.appendChild(s);
    });

    var cur = 0;
    function syncSlideVideos(slide) {
      if (syncTimer) {
        clearInterval(syncTimer);
        syncTimer = null;
      }

      slides.forEach(function (s) {
        s.querySelectorAll('video').forEach(function (v) {
          v.pause();
        });
      });

      var videos = Array.from(slide.querySelectorAll('video'));
      if (!videos.length) return;

      videos.forEach(function (v) {
        v.muted = true;
        v.loop = true;
        v.playbackRate = 1;
        try { v.currentTime = 0; } catch (e) {}
      });

      function playAll() {
        videos.forEach(function (v) {
          var p = v.play();
          if (p && typeof p.catch === 'function') p.catch(function () {});
        });
      }

      if (videos.every(function (v) { return v.readyState >= 2; })) {
        playAll();
      } else {
        var remaining = videos.length;
        videos.forEach(function (v) {
          if (v.readyState >= 2) {
            remaining -= 1;
          } else {
            v.addEventListener('canplay', function onCanPlay() {
              v.removeEventListener('canplay', onCanPlay);
              remaining -= 1;
              if (remaining <= 0) playAll();
            });
          }
        });
        if (remaining <= 0) playAll();
      }

      syncTimer = setInterval(function () {
        if (!slide.classList.contains('active')) return;
        var master = videos[0];
        videos.slice(1).forEach(function (v) {
          if (Math.abs(v.currentTime - master.currentTime) > 0.08) {
            try { v.currentTime = master.currentTime; } catch (e) {}
          }
          if (master.paused && !v.paused) v.pause();
          if (!master.paused && v.paused) {
            var p = v.play();
            if (p && typeof p.catch === 'function') p.catch(function () {});
          }
        });
      }, 250);
    }

    function show(i) {
      cur = (i + slides.length) % slides.length;
      slides.forEach(function (s, j) { s.classList.toggle('active', j === cur); });
      counter.textContent = (cur + 1) + ' / ' + slides.length;
      syncSlideVideos(slides[cur]);
    }
    prev.addEventListener('click', function () { show(cur - 1); });
    next.addEventListener('click', function () { show(cur + 1); });
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { show(cur - 1); e.preventDefault(); }
      else if (e.key === 'ArrowRight') { show(cur + 1); e.preventDefault(); }
    });
    show(0);
    return wrap;
  }

  function carouselize(container, slideSelector) {
    if (!container) return;
    var slides = Array.from(container.querySelectorAll(slideSelector));
    if (slides.length < 2) return; // nothing to gain from a 1-slide carousel
    var header = container.querySelector(':scope > .compare-header, :scope > .frame-compare-header, :scope > .reward-header');
    var carousel = buildCarousel(slides, header);
    // Remove the original grids and the "Show N more" details that held these slides.
    container.querySelectorAll('.video-grid, .more-list, details.more').forEach(function (el) {
      el.parentNode && el.parentNode.removeChild(el);
    });
    container.appendChild(carousel);
  }

  // Videos: one carousel for the whole #videos gallery.
  carouselize(document.getElementById('videos'), '.video-card');
  // Training rewards: one carousel over scenes.
  carouselize(document.getElementById('train-rewards'), '.reward-scene-card');
  // Frames: one carousel per subsection (Forward / Turning).
  document.querySelectorAll('#frames .subsection, section.subsection').forEach(function (sub) {
    carouselize(sub, '.frame-card');
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
    if (t.tagName === 'IMG' && (t.closest('.compare-table') || t.closest('.reward-grid'))) {
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
