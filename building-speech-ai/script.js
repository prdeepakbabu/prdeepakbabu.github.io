/* ===================================================================
   Building Speech AI — interactive layer
   - Animated multi-band audio waveform on hero canvas
   - Sticky-nav state on scroll
   - Scroll-triggered reveals
   - Notebook hardware filter
   =================================================================== */

(() => {
  'use strict';

  /* ---------- 1. NAV SCROLL STATE ---------- */
  const nav = document.getElementById('nav');
  const onScroll = () => {
    if (window.scrollY > 12) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- 2. SCROLL REVEAL ---------- */
  const revealTargets = document.querySelectorAll(
    '.section-head, .about-grid, .arc-step, .chapter-card, .nb-card, .qs-step, .hw-block, .author-card, .final-cta'
  );
  revealTargets.forEach(el => el.classList.add('reveal'));

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          // small stagger for grid children
          const delay = entry.target.matches('.arc-step, .chapter-card, .nb-card, .qs-step')
            ? Math.min(i * 40, 240)
            : 0;
          setTimeout(() => entry.target.classList.add('in-view'), delay);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealTargets.forEach(el => io.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('in-view'));
  }

  /* ---------- 3. NOTEBOOK FILTER ---------- */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const nbCards = document.querySelectorAll('.nb-card');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      filterBtns.forEach(b => b.classList.toggle('active', b === btn));
      nbCards.forEach(card => {
        const match = filter === 'all' || card.dataset.hw === filter;
        card.style.display = match ? '' : 'none';
      });
    });
  });

  /* ---------- 4. HERO WAVEFORM (Canvas) ---------- */
  const canvas = document.getElementById('wave-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = 0, height = 0, dpr = window.devicePixelRatio || 1;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function resize() {
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  // Three independent sine bands with FM-like wobble — evokes the
  // mel-spectrogram bands without literally being one.
  const bands = [
    { amp: 0.18, freq: 0.0042, phase: 0,         speed: 0.0015, color: 'rgba(177, 77, 240, 0.55)', y: 0.32, lw: 1.6 },
    { amp: 0.12, freq: 0.0064, phase: 1.4,       speed: 0.0022, color: 'rgba(92, 225, 230, 0.55)', y: 0.50, lw: 1.4 },
    { amp: 0.16, freq: 0.0036, phase: 2.6,       speed: 0.0010, color: 'rgba(255, 148, 71, 0.65)', y: 0.66, lw: 1.8 },
    { amp: 0.08, freq: 0.0090, phase: 3.8,       speed: 0.0028, color: 'rgba(255, 209, 102, 0.45)', y: 0.78, lw: 1.2 },
  ];

  // particles drifting upward like spectrogram intensity ticks
  const particles = Array.from({ length: 36 }, () => ({
    x: Math.random(),
    y: Math.random(),
    r: 0.6 + Math.random() * 1.4,
    sp: 0.0002 + Math.random() * 0.0006,
    a: 0.18 + Math.random() * 0.4,
  }));

  function draw(t) {
    ctx.clearRect(0, 0, width, height);

    // soft horizon glow at the bottom
    const grad = ctx.createLinearGradient(0, height * 0.6, 0, height);
    grad.addColorStop(0, 'rgba(255, 148, 71, 0)');
    grad.addColorStop(1, 'rgba(255, 148, 71, 0.08)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, height * 0.6, width, height * 0.4);

    // particles
    particles.forEach(p => {
      const px = p.x * width;
      const py = (1 - p.y) * height;
      ctx.fillStyle = `rgba(255, 209, 102, ${p.a})`;
      ctx.beginPath();
      ctx.arc(px, py, p.r, 0, Math.PI * 2);
      ctx.fill();
      p.y += p.sp;
      if (p.y > 1) { p.y = 0; p.x = Math.random(); }
    });

    // waveform bands
    bands.forEach(b => {
      ctx.beginPath();
      ctx.strokeStyle = b.color;
      ctx.lineWidth = b.lw;
      ctx.lineCap = 'round';

      const baseY = b.y * height;
      const ampPx = b.amp * height;

      for (let x = 0; x <= width; x += 2) {
        const wobble = Math.sin(x * b.freq * 0.4 + t * b.speed * 0.5 + b.phase) * 0.3;
        const env = Math.sin(x * b.freq + t * b.speed + b.phase + wobble);
        const env2 = 0.5 * Math.sin(x * b.freq * 2.7 + t * b.speed * 1.3);
        const y = baseY + (env + env2) * ampPx * 0.6;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    });
  }

  let raf = 0;
  let last = performance.now();
  function loop(now) {
    draw(now);
    raf = requestAnimationFrame(loop);
  }

  if (!reduced) {
    raf = requestAnimationFrame(loop);
  } else {
    draw(0);
  }

  // pause when tab hidden
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(raf);
    } else if (!reduced) {
      raf = requestAnimationFrame(loop);
    }
  });

  /* ---------- 5. SMOOTH SCROLL OFFSET ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      const y = target.getBoundingClientRect().top + window.scrollY - 64;
      window.scrollTo({ top: y, behavior: 'smooth' });
    });
  });

  /* ===================================================================
     CHAPTER SAMPLE MODAL
     One curated sample per chapter — voice/tone matches the book.
     Click any chapter card → modal opens with a real, readable excerpt.
     =================================================================== */

  const chapterSamples = {
    1: {
      title: 'Introduction to Speech &amp; Audio AI',
      html: `
        <p>Speech AI sits at the intersection of four disciplines that rarely sit at the same table. Signal processing supplies the math of waves. Linguistics supplies the structure of language. Machine learning supplies the function approximators. Systems engineering decides whether any of it ships.</p>
        <p>Most failures I have seen in production were not failures of the model. They were failures at the seams between these four domains — places where the engineer who knew Fourier did not know phonetics, or the linguist did not know what a 50&nbsp;ms latency budget looks like in a streaming pipeline.</p>
        <blockquote>If you can't run it, you don't really understand it.</blockquote>
        <p>The book starts here because you cannot reason about the rest of speech AI until you can hold all four of these in your head at the same time.</p>
        <h4>The thread that runs through every chapter</h4>
        <ul>
          <li><strong>Sound is a physical thing</strong> — pressure waves that decay, refract, and lose information.</li>
          <li><strong>Hearing is a perceptual thing</strong> — the cochlea is a bank of frequency-tuned filters, not an FFT.</li>
          <li><strong>Speech is a linguistic thing</strong> — phonemes, prosody, semantics, pragmatics, in that order of fragility.</li>
          <li><strong>Production speech AI is an engineering thing</strong> — and the engineering is what decides reach.</li>
        </ul>
      `
    },
    2: {
      title: 'Understanding Audio Data',
      html: `
        <p>Audio is the data type that beginners most often underestimate. It looks like just another modality — a sequence, like text — and the temptation is to reach for the same tools. That temptation is a trap.</p>
        <h4>Audio versus text versus images</h4>
        <table>
          <thead>
            <tr><th>Property</th><th>Text</th><th>Image</th><th>Audio</th></tr>
          </thead>
          <tbody>
            <tr><td>Tokens</td><td>~10<sup>4</sup>/page</td><td>~10<sup>5</sup> px</td><td>~10<sup>6</sup>/min</td></tr>
            <tr><td>Natural alphabet</td><td>discrete</td><td>continuous</td><td>continuous</td></tr>
            <tr><td>Temporal axis</td><td>logical</td><td>none</td><td><strong>physical</strong></td></tr>
            <tr><td>Reorderable</td><td>no</td><td>n/a</td><td><strong>no</strong></td></tr>
            <tr><td>Locality</td><td>strong</td><td>strong</td><td>multi-scale</td></tr>
          </tbody>
        </table>
        <p>The last two rows are where the trap lives. Audio cannot be reordered. A spectrogram is not a picture — it is an image whose <em>x-axis is time</em> and whose information is multi-scale. Convolutional priors that work on photos quietly mislearn this.</p>
        <p class="pull"><strong>The computational storm:</strong> 16 kHz audio means 16,000 numbers per second per channel. A one-hour podcast is 57 million samples. Whatever you do, you will do it 16,000 times a second.</p>
      `
    },
    3: {
      title: 'Signal Processing Fundamentals',
      html: `
        <p>The Fourier transform is not optional. You can defer learning it for a while — most modern libraries hide it — but eventually you will be staring at a spectrogram trying to debug a model, and you will need to know what each pixel means.</p>
        <h4>The intuition without the calculus</h4>
        <p>Any periodic signal can be decomposed into sinusoids. The Fourier transform tells you <em>which sinusoids</em>. That is the whole idea.</p>
        <pre><code>signal(t) = Σ A_k · sin(2π·f_k·t + φ_k)
            └────────────┬────────────┘
                  the k-th component:
                  amplitude A_k at frequency f_k</code></pre>
        <p>The Short-Time Fourier Transform (STFT) does this on overlapping windows of the signal — 25&nbsp;ms windows hopped every 10&nbsp;ms is the canonical recipe. The output is a 2D array: rows are frequency bins, columns are time. That array, log-scaled and color-mapped, is a spectrogram.</p>
        <h4>Why the mel scale</h4>
        <p>Human hearing is not linear in frequency. Doubling the Hz from 100→200 sounds like a much bigger jump than 4000→4100. The mel scale warps frequency to roughly match perception — and for speech, perception is exactly what the model needs to capture.</p>
        <blockquote>If filtering feels like magic, replace the word "filtering" in your head with "selective attention." That's all it is, in the time domain.</blockquote>
      `
    },
    4: {
      title: 'The Evolution of Speech Technology',
      html: `
        <p>Speech recognition has had three eras. Knowing which one a paper belongs to is half the battle when reading the literature.</p>
        <ul class="timeline">
          <li><b>1970s</b>Acoustic-phonetic — hand-crafted rules over phonemes. Brittle.</li>
          <li><b>1980s</b>Hidden Markov Models. Probabilistic. The DARPA evaluations.</li>
          <li><b>1990s</b>HMM-GMM. Mixture of Gaussians for acoustic, n-grams for language. Dragon and IBM ViaVoice ship.</li>
          <li><b>2010s</b>DNN-HMM hybrid. Deep nets replace GMMs. Word error rates halve.</li>
          <li><b>2014–17</b>End-to-end neural ASR — CTC, attention, RNN-T. The pipeline collapses into one model.</li>
          <li><b>2017–22</b>Self-supervised pretraining. Wav2Vec, HuBERT. Labeled data stops being the bottleneck.</li>
          <li><b>2022–</b>Whisper-style weak supervision at scale. Multilingual by default.</li>
        </ul>
        <p>The temptation, looking back, is to say each era was a "mistake." It was not. Each one squeezed everything it could out of the assumptions of its time. <strong>HMM-GMM was the right answer for 1995's compute budget.</strong> What changed was the compute, not the math.</p>
        <p class="pull">Lesson that survives every era: <strong>language modeling is half the system.</strong> Acoustic accuracy buys you decoded phonemes. Language modeling turns those into words you would actually say.</p>
      `
    },
    5: {
      title: 'Modern ASR Architectures',
      html: `
        <p>If you only learn one modern ASR architecture, learn Whisper. Not because it is the best at every benchmark — it is not — but because it teaches the lesson that defines this era: <em>scale and data quality beat clever architecture</em>.</p>
        <h4>Whisper's quiet trick</h4>
        <p>Whisper was trained on 680,000 hours of weakly-labeled multilingual audio scraped from the open web. The labels are imperfect — auto-generated subtitles, transcriptions of varying quality. The architecture is a vanilla encoder-decoder Transformer with no exotic tricks. The breakthrough was the data pipeline.</p>
        <table>
          <thead><tr><th>Model</th><th>Params</th><th>WER (LibriSpeech clean)</th><th>Multilingual</th></tr></thead>
          <tbody>
            <tr><td><code>tiny</code></td><td>39 M</td><td>~7.5 %</td><td>yes</td></tr>
            <tr><td><code>base</code></td><td>74 M</td><td>~5.0 %</td><td>yes</td></tr>
            <tr><td><code>small</code></td><td>244 M</td><td>~3.4 %</td><td>yes</td></tr>
            <tr><td><code>medium</code></td><td>769 M</td><td>~2.9 %</td><td>yes</td></tr>
            <tr><td><code>large-v3</code></td><td>1550 M</td><td>~1.8 %</td><td>99 langs</td></tr>
          </tbody>
        </table>
        <p>The other family — wav2vec 2.0, HuBERT — is the self-supervised line. They learn audio representations <em>without</em> labels, by predicting masked frames or quantized targets. Those representations transfer. With as little as 10 minutes of labeled data, a fine-tuned wav2vec 2.0 model can reach competitive WER on a new language.</p>
        <blockquote>Self-supervised learning is the dark matter of audio AI: invisible in benchmarks, but holding up everything you actually use.</blockquote>
      `
    },
    6: {
      title: 'Audio Representations &amp; Embeddings',
      html: `
        <p>Embeddings are the universal currency of modern audio AI. Understand what an embedding <em>encodes</em> and what it <em>discards</em>, and most of the rest of the field reduces to "pick the right embedding for the job."</p>
        <h4>Three things an embedding might capture, in order of separability</h4>
        <ol>
          <li><strong>Content</strong> — the words said. CTC-style models lean here.</li>
          <li><strong>Speaker identity</strong> — who said them. x-vectors and WavLM-SV lean here.</li>
          <li><strong>Emotion / paralinguistics</strong> — how they were said. Wav2Vec emotion heads lean here.</li>
        </ol>
        <p>The interesting empirical fact: these three are <em>more separable than you might guess</em>. You can take a content embedding from one model, project out the speaker direction, and get a representation that lets two voices saying the same sentence land in nearly the same spot in vector space.</p>
        <h4>The cosine-similarity reality check</h4>
        <pre><code>"Hello, my name is Alice."   (Alice speaking)
"Hello, my name is Alice."   (Bob speaking)
                                   ↓
content embedding cos-sim:  0.94
speaker embedding cos-sim:  0.21</code></pre>
        <p class="pull">The takeaway: <strong>which embedding you choose is a design decision, not a default.</strong> ASR uses content. Verification uses speaker. Voice cloning uses both. Get this wrong and your downstream system inherits the confusion.</p>
      `
    },
    7: {
      title: 'Text-to-Speech Synthesis',
      html: `
        <p>Modern TTS is a stack, not a single model. Reading any TTS paper means knowing where in the stack the contribution lives.</p>
        <h4>The classical TTS stack</h4>
        <pre><code>text  →  phonemes / linguistic features   (front-end)
        →  acoustic features (mel)        (acoustic model)
        →  waveform                        (vocoder)</code></pre>
        <p>Each layer was a separate research community for a decade. Then the layers started collapsing.</p>
        <ul>
          <li><strong>WaveNet (2016)</strong> — autoregressive sample-by-sample vocoding. Beautiful, slow.</li>
          <li><strong>FastSpeech / Tacotron 2 (2017–19)</strong> — non-autoregressive acoustic model. Real-time on a CPU.</li>
          <li><strong>HiFi-GAN (2020)</strong> — adversarial vocoder. Indistinguishable from natural for many listeners.</li>
          <li><strong>VITS (2021)</strong> — first end-to-end neural TTS. Text in, waveform out, single model.</li>
          <li><strong>VALL-E / F5-TTS (2023–24)</strong> — zero-shot voice cloning from 3 seconds of reference audio.</li>
          <li><strong>Diffusion TTS (2024–)</strong> — iterative refinement, controllable, still in flux.</li>
        </ul>
        <blockquote>Voice cloning makes fraud trivially easy. Synthetic speech can spread misinformation at scale. We are, all of us working in this field, responsible for what we build and how it's used.</blockquote>
        <p>Every section on synthesis in this book has an ethics paragraph. Not as a footnote — as <em>the point</em>. The math and the consent live in the same chapter for a reason.</p>
      `
    },
    8: {
      title: 'Advanced Applications',
      html: `
        <p>Once ASR and TTS work, the field opens into the applications that depend on them. Each one teaches a different lesson about what audio is.</p>
        <h4>Diarization — who spoke when</h4>
        <p>Diarization is a clustering problem in disguise. Slice audio into short windows, embed each window with a speaker embedding, cluster. The hard parts are the boundaries (when did one speaker stop?) and the unknowns (how many speakers are there?). Production diarization systems combine speaker embeddings with VAD (voice activity detection) and a Bayesian or spectral clusterer.</p>
        <h4>Audio deepfakes — the asymmetric arms race</h4>
        <p>Detection lags generation. Always. Every detector is trained on the previous generation of synthetic audio; the next generation is, by construction, the one that fools it. The honest stance is: <strong>do not rely on detection alone.</strong> Pair it with provenance — cryptographic signatures, watermarks at synthesis time, callback verification.</p>
        <h4>Bias in speech AI is bias in the data, recorded</h4>
        <table>
          <thead><tr><th>Subgroup</th><th>WER lift vs. corpus mean</th></tr></thead>
          <tbody>
            <tr><td>African American Vernacular English</td><td>+2× to +3×</td></tr>
            <tr><td>Indian-accented English</td><td>+1.5× to +2×</td></tr>
            <tr><td>Children</td><td>+1.7× to +2.5×</td></tr>
            <tr><td>Speakers with disordered speech</td><td>+3× to +5×</td></tr>
          </tbody>
        </table>
        <p class="pull">These gaps are <em>not</em> immutable. They shrink as soon as you collect representative data. The persistence of the gap is a sourcing decision, not a technical limit.</p>
      `
    },
    9: {
      title: 'Audio Language Models',
      html: `
        <p>For a decade we built voice assistants as cascades: speech-to-text → language model → text-to-speech. The cascade is what most production systems still are. It also has three problems that audio language models exist to solve.</p>
        <h4>The cascade problem</h4>
        <ol>
          <li><strong>Latency stacks.</strong> Each stage adds 100–300&nbsp;ms. Conversational targets (sub-300&nbsp;ms total) are out of reach.</li>
          <li><strong>Information leaks.</strong> Tone, hesitation, emotion, prosody — all flattened into text by the ASR step. The LLM never sees them.</li>
          <li><strong>Errors compound.</strong> ASR mistakes propagate downstream. The TTS stage cannot recover what the ASR stage threw away.</li>
        </ol>
        <h4>The native audio LM bet</h4>
        <p>Audio language models train one model to operate on <em>discrete audio tokens</em> directly. Audio in, audio out. Words emerge as a side effect of token prediction, the way they do in a text LLM.</p>
        <pre><code>cascade:    audio → text → audio   (3 models, 3 latencies, 2 lossy bottlenecks)
audio LM:   audio → audio          (1 model, 1 latency, no bottleneck)</code></pre>
        <p>The trade-off is honest: audio LMs require enormous training data, demand much more compute at inference, and are harder to align. The cascade isn't going away tomorrow. But the design space has split, and ignoring the native side is no longer a defensible default.</p>
        <blockquote>The future of how humans and machines communicate is being written now, by people like you.</blockquote>
      `
    },
    10: {
      title: 'Ethics, Society &amp; the Future',
      html: `
        <p>This chapter is short on purpose. The arguments are not novel; the responsibilities are.</p>
        <h4>Robustness ≠ accuracy</h4>
        <p>A model can hit 98 % accuracy on its evaluation set and fail catastrophically when deployed. The benchmark is not the population. <strong>Robustness</strong> measures how the model degrades on distribution shifts you didn't anticipate. For voice systems, those shifts are: accents, ages, devices, rooms, background noise, distance from microphone, emotional state. Test all of them, deliberately, before you ship.</p>
        <h4>Edge AI — the corner where compute, privacy, and latency converge</h4>
        <p>Pushing inference to the device gives you three things at once: lower latency, better privacy (data never leaves the device), and offline capability. It costs you model size — you have a few hundred megabytes of RAM, not a few hundred gigabytes. The compression tools in chapter&nbsp;11 (quantization, distillation, pruning) are how you make the trade.</p>
        <h4>What I'd want a reader to remember in five years</h4>
        <ul>
          <li><strong>Datasheet your data.</strong> Who recorded it, where, in what conditions, with what consent. Future-you will thank present-you.</li>
          <li><strong>Measure subgroup performance.</strong> A single WER number hides a lot.</li>
          <li><strong>Build provenance in, not on.</strong> Watermark synthetic audio at generation time. Bolting it on later doesn't work.</li>
          <li><strong>Latency is a UX feature.</strong> A "smart" system that takes a beat too long stops feeling smart.</li>
        </ul>
        <blockquote>I hope this book gives you both the technical skills to build speech AI systems and the judgment to deploy them thoughtfully.</blockquote>
      `
    },
    11: {
      title: 'Voice as Human-Computer Interface',
      html: `
        <p>Voice is not text-with-audio-attached. It is a different interface with different costs, different affordances, and different failure modes. The chapter starts with this because most voice products still ship as if it were "ASR + a chatbot."</p>
        <h4>The latency budget for conversational voice</h4>
        <p>A natural conversational turn-taking gap is 200–300 ms. The whole pipeline has to fit inside that:</p>
        <table>
          <thead><tr><th>Stage</th><th>Budget</th><th>Notes</th></tr></thead>
          <tbody>
            <tr><td>Endpointing</td><td>~100 ms</td><td>VAD decides "they're done speaking"</td></tr>
            <tr><td>ASR</td><td>~80 ms</td><td>Streaming, finalize on EOU</td></tr>
            <tr><td>NLU + LLM</td><td>~120 ms</td><td>First-token latency, not full response</td></tr>
            <tr><td>TTS first audio</td><td>~80 ms</td><td>Streaming TTS — start before full text</td></tr>
            <tr><td><strong>Total</strong></td><td><strong>~380 ms</strong></td><td>Already over budget. Optimize relentlessly.</td></tr>
          </tbody>
        </table>
        <h4>The habit-inertia problem</h4>
        <p>People have decades of muscle memory for keyboards. Voice has to be <em>materially better</em> at a task — not equal — for users to switch. The tasks where voice wins are the ones where typing is ergonomically painful (driving, cooking, walking) or the alternative interface is worse (smart speakers without screens). Everything else is uphill.</p>
        <p class="pull"><strong>Design rule:</strong> if your voice feature would also be good as a typed feature, you have not yet found the voice-only insight.</p>
      `
    },
    12: {
      title: 'Hands-On Implementation',
      html: `
        <p>This is the chapter the companion repo is built around. Twelve runnable notebooks, twelve CLI scripts. Read the chapter; run the code. Both, in that order.</p>
        <h4>Notebook → production: the gap that kills most projects</h4>
        <p>A notebook that works in the demo is one or two orders of magnitude away from a system that works in production. The gap is not a single thing — it is a checklist of unglamorous engineering tasks that each take an afternoon and together take a quarter:</p>
        <ul>
          <li><strong>Memory.</strong> 8&nbsp;GB GPUs are common. Whisper-large-v3 weighs ~3&nbsp;GB. Add KV-cache, batch, and overhead — you have less room than you think.</li>
          <li><strong>Streaming.</strong> Notebook code reads a whole file. Production sees 20&nbsp;ms chunks. Different code path entirely.</li>
          <li><strong>Quantization.</strong> bitsandbytes 4-bit, FP16, INT8 — pick a strategy and measure the WER cost.</li>
          <li><strong>Robust audio I/O.</strong> Sample rates, channels, bit depths, container formats. Test on real-world inputs (WhatsApp voice notes, Zoom recordings).</li>
          <li><strong>Observability.</strong> Log audio length, latency, confidence, errors. Without this, you cannot debug post-launch.</li>
          <li><strong>Cost.</strong> A T4 hour is ~$0.30. A H100 hour is ~$3. Doing the math early prevents painful rewrites.</li>
        </ul>
        <h4>The companion repo, in one paragraph</h4>
        <p>Each chapter has a notebook (already executed, browsable on GitHub) and a CLI script (idempotent, scriptable). Chapters 1–8 run on a CPU or a 4&nbsp;GB GPU. Chapters 9–10 want 8&nbsp;GB. Chapter 11 — the LoRA scaling experiment — wants 16&nbsp;GB. Chapter 12 ties it together with an end-to-end voice pipeline you can talk to.</p>
        <p class="pull">Do not just read this chapter. <strong>Run it.</strong> The understanding you get from typing <code>pip install</code> and watching the GPU light up is not available any other way.</p>
      `
    }
  };

  const grid = document.querySelector('.chapters-grid');
  const isTouch = window.matchMedia('(hover: none)').matches;
  let currentCh = null;
  let activeCard = null;

  function findLastCardInRow(card) {
    if (!grid) return card;
    const cards = Array.from(grid.querySelectorAll('.chapter-card'));
    const top = card.offsetTop;
    let last = card;
    for (const c of cards) {
      if (Math.abs(c.offsetTop - top) < 4) last = c;
    }
    return last;
  }

  function removeExpansion() {
    const existing = grid && grid.querySelector('.ch-expansion');
    if (existing) existing.remove();
    if (activeCard) {
      activeCard.classList.remove('active');
      activeCard.classList.remove('flipped');
      activeCard = null;
    }
  }

  function buildExpansion(n) {
    const sample = chapterSamples[n];
    if (!sample) return null;
    const exp = document.createElement('div');
    exp.className = 'ch-expansion';
    exp.setAttribute('data-ch', n);
    exp.innerHTML = `
      <div class="ch-expansion-arrow"></div>
      <div class="ch-expansion-inner">
        <button class="ch-expansion-close" aria-label="Close sample">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
        <div class="ch-expansion-meta">
          <span class="ch-expansion-eyebrow">Sample · Chapter ${n}</span>
          <h3 class="ch-expansion-title">${sample.title}</h3>
        </div>
        <div class="ch-expansion-body">${sample.html}</div>
        <div class="ch-expansion-foot">
          <button class="ch-expansion-nav" data-nav="prev" ${n <= 1 ? 'disabled' : ''}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            Prev chapter
          </button>
          <span class="ch-expansion-counter">${n} / 12</span>
          <button class="ch-expansion-nav" data-nav="next" ${n >= 12 ? 'disabled' : ''}>
            Next chapter
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
          </button>
        </div>
      </div>
    `;
    return exp;
  }

  function expandChapter(n, scroll) {
    if (!grid) return;
    const card = grid.querySelector(`.chapter-card[data-ch="${n}"]`);
    if (!card) return;

    // Toggle: clicking the active card again closes it.
    if (currentCh === n && grid.querySelector('.ch-expansion')) {
      removeExpansion();
      currentCh = null;
      return;
    }

    removeExpansion();
    currentCh = n;
    activeCard = card;
    card.classList.add('active');

    const exp = buildExpansion(n);
    if (!exp) return;

    const lastInRow = findLastCardInRow(card);
    lastInRow.after(exp);

    // Position the little arrow under the clicked card.
    requestAnimationFrame(() => {
      const arrow = exp.querySelector('.ch-expansion-arrow');
      if (!arrow) return;
      const cardRect = card.getBoundingClientRect();
      const expRect = exp.getBoundingClientRect();
      const offsetLeft = (cardRect.left + cardRect.width / 2) - expRect.left - 9;
      arrow.style.left = `${Math.max(20, offsetLeft)}px`;
    });

    if (scroll !== false) {
      // gentle scroll so the expansion is comfortably in view
      requestAnimationFrame(() => {
        const rect = exp.getBoundingClientRect();
        const targetTop = rect.top + window.scrollY - 90;
        if (rect.top < 80 || rect.bottom > window.innerHeight) {
          window.scrollTo({ top: targetTop, behavior: 'smooth' });
        }
      });
    }

    if (typeof window.gtag === 'function') {
      window.gtag('event', 'chapter_sample_open', {
        event_category: 'speech_ai_book',
        event_label: `chapter_${n}`,
        value: n
      });
    }
  }

  document.querySelectorAll('.chapter-card').forEach(card => {
    const n = parseInt(card.dataset.ch, 10);
    if (!n) return;

    card.addEventListener('click', e => {
      // ignore clicks bubbling from inside the expansion (which sits later in DOM)
      if (e.target.closest('.ch-expansion')) return;

      if (isTouch && !card.classList.contains('flipped') && currentCh !== n) {
        // first tap on touch: flip to show watch-points; second tap opens
        document.querySelectorAll('.chapter-card.flipped').forEach(c => c.classList.remove('flipped'));
        card.classList.add('flipped');
        return;
      }
      expandChapter(n, true);
    });
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        expandChapter(n, true);
      }
    });
  });

  // Delegated handlers inside the (dynamically inserted) expansion
  if (grid) {
    grid.addEventListener('click', e => {
      const closeBtn = e.target.closest('.ch-expansion-close');
      if (closeBtn) {
        removeExpansion();
        currentCh = null;
        if (typeof window.gtag === 'function') {
          window.gtag('event', 'chapter_sample_close', {
            event_category: 'speech_ai_book'
          });
        }
        return;
      }
      const navBtn = e.target.closest('.ch-expansion-nav');
      if (navBtn && currentCh != null) {
        const dir = navBtn.dataset.nav;
        if (dir === 'prev' && currentCh > 1) expandChapter(currentCh - 1, true);
        else if (dir === 'next' && currentCh < 12) expandChapter(currentCh + 1, true);
      }
    });
  }

  document.addEventListener('keydown', e => {
    if (currentCh == null) return;
    if (e.key === 'Escape') {
      removeExpansion();
      currentCh = null;
    } else if (e.key === 'ArrowLeft' && currentCh > 1) {
      expandChapter(currentCh - 1, true);
    } else if (e.key === 'ArrowRight' && currentCh < 12) {
      expandChapter(currentCh + 1, true);
    }
  });

  // Re-position the arrow on resize
  window.addEventListener('resize', () => {
    if (currentCh != null && activeCard) {
      const exp = grid && grid.querySelector('.ch-expansion');
      if (!exp) return;
      const arrow = exp.querySelector('.ch-expansion-arrow');
      if (!arrow) return;
      const cardRect = activeCard.getBoundingClientRect();
      const expRect = exp.getBoundingClientRect();
      const offsetLeft = (cardRect.left + cardRect.width / 2) - expRect.left - 9;
      arrow.style.left = `${Math.max(20, offsetLeft)}px`;
      // also re-locate the expansion if the wrapping has changed
      const lastInRow = findLastCardInRow(activeCard);
      if (lastInRow.nextSibling !== exp) lastInRow.after(exp);
    }
  });

  /* ===================================================================
     ANALYTICS — Google Analytics 4 (gtag) instrumentation
     =================================================================== */

  const EVENT_CATEGORY = 'speech_ai_book';
  const sendEvent = (eventName, params) => {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, Object.assign({ event_category: EVENT_CATEGORY }, params || {}));
  };

  /* ---------- A. AUTO-TAG NOTEBOOK CARD BUTTONS ----------
     12 cards × 3 buttons (Notebook / Script / Colab). We derive the
     analytics label from the chapter number + button role, so the GA
     report shows e.g. "07_voice_assistant__notebook". */
  document.querySelectorAll('.nb-card').forEach(card => {
    const num = (card.querySelector('.nb-num')?.textContent || '').trim();
    const title = (card.querySelector('h3')?.textContent || '').trim()
      .toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
    card.querySelectorAll('.nb-btn').forEach(btn => {
      const text = btn.textContent.trim().toLowerCase();
      let role = 'unknown';
      if (text.startsWith('notebook')) role = 'notebook';
      else if (text.startsWith('script')) role = 'script';
      else if (text.startsWith('colab')) role = 'colab';
      btn.setAttribute('data-analytics-event', 'notebook_card_click');
      btn.setAttribute('data-analytics-label', `${num}_${title}__${role}`);
    });
  });

  /* ---------- B. DELEGATED CLICK TRACKING ----------
     Catches every [data-analytics-event] in one listener — works for
     elements that didn't exist at page load too. */
  document.addEventListener('click', e => {
    const target = e.target.closest('[data-analytics-event]');
    if (!target) return;
    const event = target.getAttribute('data-analytics-event');
    const label = target.getAttribute('data-analytics-label')
      || target.textContent.trim().slice(0, 60)
      || 'unlabeled';
    const href = target.getAttribute('href') || null;
    sendEvent(event, {
      event_label: label,
      link_url: href,
      outbound: href && /^https?:\/\//i.test(href) && !href.includes(location.host)
    });
  });

  /* ---------- C. SCROLL DEPTH (25 / 50 / 75 / 100) ---------- */
  const milestones = [25, 50, 75, 100];
  const fired = new Set();
  const checkScrollDepth = () => {
    const doc = document.documentElement;
    const max = doc.scrollHeight - doc.clientHeight;
    if (max <= 0) return;
    const pct = Math.round((window.scrollY / max) * 100);
    milestones.forEach(m => {
      if (pct >= m && !fired.has(m)) {
        fired.add(m);
        sendEvent('scroll_depth', {
          event_label: `${m}%`,
          value: m
        });
      }
    });
  };
  let scrollTimer = null;
  window.addEventListener('scroll', () => {
    if (scrollTimer) return;
    scrollTimer = setTimeout(() => { scrollTimer = null; checkScrollDepth(); }, 250);
  }, { passive: true });

  /* ---------- D. SECTION VIEW (one event per section, fires once) ---------- */
  const sectionMap = [
    { id: 'top',        label: 'hero' },
    { id: 'about',      label: 'about_book' },
    { id: 'arc',        label: 'four_parts_arc' },
    { id: 'chapters',   label: 'chapters_grid' },
    { id: 'code',       label: 'companion_code' },
    { id: 'quickstart', label: 'quick_start' },
    { id: 'author',     label: 'author' }
  ];
  if ('IntersectionObserver' in window) {
    const seen = new Set();
    const sectionIO = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        if (seen.has(id)) return;
        seen.add(id);
        const meta = sectionMap.find(s => s.id === id);
        sendEvent('section_view', { event_label: meta ? meta.label : id });
        sectionIO.unobserve(entry.target);
      });
    }, { threshold: 0.35 });
    sectionMap.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) sectionIO.observe(el);
    });
  }

  /* ---------- E. ENGAGEMENT MILESTONES ----------
     Gives a sense of "did this person actually read?" beyond pageview. */
  const engagementSeconds = [10, 30, 60, 180];
  const engagementFired = new Set();
  const startTime = Date.now();
  const checkEngagement = () => {
    if (document.hidden) return;
    const elapsed = Math.round((Date.now() - startTime) / 1000);
    engagementSeconds.forEach(s => {
      if (elapsed >= s && !engagementFired.has(s)) {
        engagementFired.add(s);
        sendEvent('engagement_time', {
          event_label: `${s}s`,
          value: s
        });
      }
    });
  };
  setInterval(checkEngagement, 5000);

  /* ---------- F. EXIT / TAB CLOSE ----------
     Fire one final event with total seconds + max scroll depth. */
  let maxScrollPct = 0;
  window.addEventListener('scroll', () => {
    const doc = document.documentElement;
    const max = doc.scrollHeight - doc.clientHeight;
    if (max <= 0) return;
    const pct = Math.round((window.scrollY / max) * 100);
    if (pct > maxScrollPct) maxScrollPct = pct;
  }, { passive: true });

  const sendExit = () => {
    const seconds = Math.round((Date.now() - startTime) / 1000);
    sendEvent('page_exit', {
      event_label: `${seconds}s_${maxScrollPct}pct`,
      time_on_page: seconds,
      max_scroll: maxScrollPct
    });
  };
  // pagehide is more reliable than beforeunload on modern browsers
  window.addEventListener('pagehide', sendExit, { once: true });
})();
