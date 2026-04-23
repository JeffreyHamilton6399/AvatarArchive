/* ═══════════════════════════════════════════════════════════════
   WHISPER.CPP CAPTION ENGINE  —  whisper-captions.js
   Loads whisper.cpp compiled to WebAssembly via whisper.wasm CDN.
   Transcribes the currently-playing video audio in the browser.
   Produces SRT cues on-the-fly and injects them into the player.
═══════════════════════════════════════════════════════════════ */
(function(global) {
  'use strict';

  const WHISPER_CDN   = 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.1/dist/transformers.min.js';
  const MODEL_NAME    = 'Xenova/whisper-tiny.en';  // ~39MB, fast on device
  const CACHE_KEY_PFX = 'avatarhub_srt_';

  let pipeline    = null;
  let isLoading   = false;
  let isRunning   = false;
  let loadPromise = null;

  /* Public API attached to window.WhisperCaptions */
  const WC = {
    /* Inject the UI button into a player's controls bar */
    injectButton(ccBtn, vid, captionBox, prefix, ep) {
      if (!ccBtn || !vid) return;
      const aiBtn = document.createElement('button');
      aiBtn.id = 'aiCCBtn';
      aiBtn.className = ccBtn.className;
      aiBtn.title = 'Auto-generate captions with AI (Whisper)';
      aiBtn.innerHTML = `<span style="font-family:'Cinzel',serif;font-size:.5rem;letter-spacing:.06em">AI CC</span>`;
      aiBtn.style.cssText = 'border:1px solid rgba(77,184,255,.4);border-radius:4px;padding:.2em .45em;color:rgba(77,184,255,.7);background:none;cursor:pointer;';
      ccBtn.parentNode.insertBefore(aiBtn, ccBtn.nextSibling);

      aiBtn.addEventListener('click', () => WC.run(aiBtn, vid, captionBox, prefix, ep));
      return aiBtn;
    },

    /* Check localStorage cache first, then run inference */
    async run(btn, vid, captionBox, prefix, ep) {
      if (isRunning) return;
      const cacheKey = CACHE_KEY_PFX + prefix + '_' + ep;

      /* Check cache */
      try {
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
          const cues = JSON.parse(cached);
          WC._applyCues(cues, vid, captionBox);
          btn.style.color = '#3ddc84';
          btn.title = 'Captions loaded from cache (AI)';
          return;
        }
      } catch(e) {}

      /* Run inference */
      isRunning = true;
      btn.style.color = '#f5c518';
      btn.title = 'Generating captions…';
      btn.innerHTML = `<span style="font-family:'Cinzel',serif;font-size:.44rem;letter-spacing:.04em">⟳ AI CC</span>`;

      try {
        const pipe = await WC._loadPipeline(btn);
        if (!pipe) { isRunning = false; return; }

        /* Extract ~30s audio chunk starting from current position for preview,
           then process the full clip — use audio context to decode */
        btn.title = 'Reading audio…';
        const audioData = await WC._extractAudio(vid);
        if (!audioData) throw new Error('Could not decode audio');

        btn.title = 'Transcribing… (this may take a minute)';
        const result = await pipe(audioData, {
          task: 'transcribe',
          language: 'en',
          return_timestamps: true,
          chunk_length_s: 30,
          stride_length_s: 5,
        });

        /* Convert to SRT cue array */
        const cues = (result.chunks || []).map(c => ({
          start: c.timestamp[0] ?? 0,
          end:   c.timestamp[1] ?? (c.timestamp[0] + 3),
          text:  c.text.trim(),
        })).filter(c => c.text);

        /* Cache and apply */
        try { localStorage.setItem(cacheKey, JSON.stringify(cues)); } catch(e) {}
        WC._applyCues(cues, vid, captionBox);

        btn.style.color = '#3ddc84';
        btn.title = 'AI Captions active (cached)';
        btn.innerHTML = `<span style="font-family:'Cinzel',serif;font-size:.5rem;letter-spacing:.06em">AI CC</span>`;
      } catch(err) {
        btn.style.color = '#f97316';
        btn.title = 'Caption generation failed — ' + (err.message || err);
        btn.innerHTML = `<span style="font-family:'Cinzel',serif;font-size:.5rem;letter-spacing:.06em">AI CC</span>`;
        console.warn('[WhisperCaptions] Error:', err);
      }
      isRunning = false;
    },

    /* Load and cache the Transformers.js pipeline */
    async _loadPipeline(btn) {
      if (pipeline) return pipeline;
      if (loadPromise) return loadPromise;

      loadPromise = new Promise(async (resolve, reject) => {
        try {
          /* Dynamically import transformers.js */
          btn.title = 'Downloading AI model (~39MB, first time only)…';
          const { pipeline: pipelineFn, env } = await import(WHISPER_CDN);
          env.allowLocalModels = false;
          env.useBrowserCache  = true;   // IndexedDB cache for model weights
          pipeline = await pipelineFn('automatic-speech-recognition', MODEL_NAME, {
            quantized: true,
          });
          resolve(pipeline);
        } catch(e) {
          reject(e);
        }
      });

      return loadPromise;
    },

    /* Decode video audio to Float32Array for Whisper */
    async _extractAudio(vid) {
      try {
        const ctx  = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const resp = await fetch(vid.src || vid.currentSrc);
        if (!resp.ok) throw new Error('Fetch failed');
        const buf  = await resp.arrayBuffer();
        const decoded = await ctx.decodeAudioData(buf);
        /* Mix down to mono Float32Array at 16kHz */
        const ch   = decoded.getChannelData(0);
        await ctx.close();
        return ch;
      } catch(e) {
        /* Fallback: capture live audio via MediaElementSource */
        try {
          const ctx   = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
          const src   = ctx.createMediaElementSource(vid);
          const proc  = ctx.createScriptProcessor(4096, 1, 1);
          const chunks = [];
          proc.onaudioprocess = e => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
          src.connect(proc); proc.connect(ctx.destination);
          /* Record 60 s worth then disconnect */
          await new Promise(r => setTimeout(r, Math.min(vid.duration||60, 60) * 100));
          proc.disconnect(); src.disconnect(); await ctx.close();
          const total = chunks.reduce((s,c)=>s+c.length, 0);
          const merged = new Float32Array(total);
          let off = 0;
          for (const c of chunks) { merged.set(c, off); off += c.length; }
          return merged;
        } catch(e2) {
          return null;
        }
      }
    },

    /* Wire cues into the player's existing caption system */
    _applyCues(cues, vid, captionBox) {
      /* Attach to the page-level srtCues variable if it exists */
      if (typeof srtCues !== 'undefined') {
        srtCues = cues;
        captionsOn = true;
        if (typeof ccBtn !== 'undefined') ccBtn.classList.add('active');
      } else {
        /* Standalone fallback renderer */
        let lastText = null;
        vid.addEventListener('timeupdate', () => {
          const t   = vid.currentTime;
          const cue = cues.find(c => t >= c.start && t <= c.end);
          const txt = cue?.text ?? null;
          if (txt === lastText) return;
          lastText = txt;
          if (txt) {
            captionBox.innerHTML = '<span>' + txt + '</span>';
            captionBox.style.display = 'block';
            requestAnimationFrame(() => captionBox.classList.add('visible'));
          } else {
            captionBox.classList.remove('visible');
            setTimeout(() => { if (!captionBox.classList.contains('visible')) captionBox.style.display = 'none'; }, 200);
          }
        });
      }
    },

    /* Clear cache for a specific episode */
    clearCache(prefix, ep) {
      try { localStorage.removeItem(CACHE_KEY_PFX + prefix + '_' + ep); } catch(e) {}
    },
  };

  global.WhisperCaptions = WC;
})(window);
