// Kurs: postęp (localStorage), kopiowanie kodu, wyszukiwarka, menu, pikselowe ikony.
(function(){
  const KLUCZ = 'chmuroholik-kurs-v1';
  const czytaj = () => { try { return JSON.parse(localStorage.getItem(KLUCZ)) || {}; } catch { return {}; } };
  const zapisz = (s) => { try { localStorage.setItem(KLUCZ, JSON.stringify(s)); } catch {} };
  let stan = czytaj(); stan.zrobione = stan.zrobione || {};

  /* ---- pikselowe ikony ---- */
  const PAL = { k:'#000', w:'#fff', y:'#ffd60a', r:'#e0322b', b:'#2e6fd6', g:'#9aa0a6', o:'#f28c28', z:'#2fa84f', s:'#f1c27d', d:'#555' };
  const S = {
    terminal:['kkkkkkkkkkkkkk','kwwwwwwwwwwwwk','kkkkkkkkkkkkkk','kkkkkkkkkkkkkk','kkwkkkkkkkkkkk','kkkwkkkkkkkkkk','kkkkwkkkkkkkkk','kkkwkkkkkkkkkk','kkwkkkwwwwkkkk','kkkkkkkkkkkkkk','kkkkkkkkkkkkkk','.kkkkkkkkkkkk.'],
    chmura:['.....kkkk.......','....kwwwwk......','..kkwwwwwwkkk...','.kwwwwwwwwwwwk..','kwwwwwwwwwwwwwk.','kwwwwwwwwwwwwwwk','kwwwwwwwwwwwwwwk','.kkkkkkkkkkkkkk.'],
    komputer:['kkkkkkkkkk','kwwwwwwwwk','kwkkkkkkwk','kwkzkkkkwk','kwkkzkkkwk','kwkzkkkkwk','kwkkkkkkwk','kwwwwwwwwk','kkkkkkkkkk','.kwwwwwwk.','kkkkkkkkkk'],
    zebatka:['...kk.kk...','..kggkggk..','.kkgggggkk.','kgggkkkgggk','.kggk.kggk.','.kggk.kggk.','kgggkkkgggk','.kkgggggkk.','..kggkggk..','...kk.kk...'],
    ksiazka:['kkkkkkkkkk','kwwwwkwwwk','kwkkwkwkkk','kwwwwkwwwk','kwkkwkwkkk','kwwwwkwwwk','kkkkkkkkkk'],
    tabela:['kkkkkkkkkkk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk'],
    tarcza:['kkkkkkkkk','kyyyyyyyk','kyyyyyykk','kyyyyykyk','kykyykyyk','kyykkyyyk','.kyyyyyk.','..kyyyk..','...kkk...'],
    dysk:['kkkkkkkkkk','kggggggggk','kgkkkkkkgk','kgkwwwwkgk','kgkkkkkkgk','kggggggggk','kggggggzgk','kkkkkkkkkk'],
    paczka:['..kkkkkkk..','.koooyoook.','kooooyooook','kkkkkykkkkk','kooooyooook','kooooyooook','kooooyooook','kkkkkkkkkkk'],
    globus:['...kkkk...','.kkbbzbkk.','kbbzzbbbbk','kbzzzbbzbk','kbbzbbzzbk','kbbbbbzzbk','kbzbbbbbbk','.kkbbbbkk.','...kkkk...'],
    klodka:['..kkkk..','.k....k.','.k....k.','kkkkkkkk','kyyyyyyk','kyyk.yyk','kyyyyyyk','kkkkkkkk'],
    serwer:['kkkkkkk','kwwwwwk','kkkkkkk','kwwwzwk','kkkkkkk','kwwwwwk','kkkkkkk','.k...k.'],
    robot:['....k....','..kkkkk..','.kwwwwwk.','.kwkwkwk.','.kwwwwwk.','.kwkkkwk.','..kkkkk..','.kgggggk.','kkgggggkk','..k...k..'],
    krawat:['..kkk..','.kwkwk.','..krk..','..krk..','.krrrk.','.krrrk.','..krk..','...k...'],
    puchar:['kkkkkkkkk','kyyyyyyyk','kkyyyyykk','k.kyyyk.k','.kkyyykk.','...kyk...','...kyk...','..kkkkk..','.kyyyyyk.','.kkkkkkk.']
  };
  function rysuj(el, nazwa, skala){
    const g = S[nazwa]; if(!g) return;
    const c = document.createElement('canvas'), w = Math.max(...g.map(r=>r.length));
    c.width = w*skala; c.height = g.length*skala; c.setAttribute('aria-hidden','true');
    const x = c.getContext('2d');
    g.forEach((r,yy)=>[...r].forEach((ch,xx)=>{ if(PAL[ch]){ x.fillStyle=PAL[ch]; x.fillRect(xx*skala,yy*skala,skala,skala);} }));
    el.appendChild(c);
  }
  document.querySelectorAll('[data-sprite]').forEach(el => rysuj(el, el.dataset.sprite, el.classList.contains('hero-ikona') ? 12 : 6));

  /* ---- menu mobilne ---- */
  const burger = document.querySelector('.burger'), linki = document.getElementById('linki');
  if (burger) burger.addEventListener('click', () => { const o = linki.classList.toggle('otwarte'); burger.setAttribute('aria-expanded', o); });

  /* ---- postęp ---- */
  let wszystkie = [];
  function odswiez(){
    const zrob = Object.keys(stan.zrobione).length;
    document.querySelectorAll('[data-lekcja]').forEach(a => a.classList.toggle('zrobione', !!stan.zrobione[a.dataset.lekcja]));
    const pm = document.getElementById('postep-menu');
    if (pm && wszystkie.length) pm.textContent = `${zrob}/${wszystkie.length}`;
    const pr = document.getElementById('procent');
    if (pr && wszystkie.length) pr.textContent = Math.round(zrob / wszystkie.length * 100) + '%';
    document.querySelectorAll('.modul').forEach(m => {
      const l = [...m.querySelectorAll('[data-lekcja]')];
      const z = l.filter(a => stan.zrobione[a.dataset.lekcja]).length;
      const i = m.querySelector('.pasek-modulu i'); if (i) i.style.width = (l.length ? z / l.length * 100 : 0) + '%';
    });
    const k = document.getElementById('kontynuuj');
    if (k && wszystkie.length) {
      const nast = wszystkie.find(x => !stan.zrobione[x.n]);
      if (zrob && nast) { k.href = `lekcja-${String(nast.n).padStart(3,'0')}.html`; k.textContent = `▶ Kontynuuj: lekcja ${nast.n}`; }
      else if (zrob && !nast) { k.textContent = '★ Kurs ukończony!'; }
    }
  }
  fetch('lekcje.json').then(r => r.json()).then(j => { wszystkie = j; odswiez(); wyszukiwarka(); }).catch(() => odswiez());

  const lekcja = document.querySelector('.lekcja');
  if (lekcja) {
    const nr = lekcja.dataset.nr, box = document.getElementById('ukonczone');
    stan = czytaj(); stan.zrobione = stan.zrobione || {}; stan.ostatnia = +nr; zapisz(stan);
    box.checked = !!stan.zrobione[nr];
    box.addEventListener('change', () => {
      stan = czytaj(); stan.zrobione = stan.zrobione || {};
      if (box.checked) { stan.zrobione[nr] = Date.now(); konfetti(box); } else delete stan.zrobione[nr];
      zapisz(stan); odswiez();
    });
    // przewinięcie do końca = propozycja oznaczenia (bez automatu, decyduje człowiek)
  }

  /* ---- kopiowanie kodu ---- */
  document.querySelectorAll('.kod').forEach(k => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'kopiuj'; b.textContent = 'kopiuj';
    b.addEventListener('click', async () => {
      try { const c = k.querySelector('code'); await navigator.clipboard.writeText(c.dataset.pelny || c.innerText); b.textContent = 'skopiowane ✓'; }
      catch { b.textContent = 'zaznacz ręcznie'; }
      setTimeout(() => b.textContent = 'kopiuj', 1600);
    });
    k.appendChild(b);
  });

  /* ---- wyszukiwarka na stronie kursu ---- */
  function wyszukiwarka(){
    const pole = document.getElementById('szukaj'); if (!pole) return;
    const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/ł/g,'l');
    const mapa = new Map(wszystkie.map(x => [String(x.n), norm(x.t + ' ' + x.k)]));
    pole.addEventListener('input', () => {
      const q = norm(pole.value.trim()); let ile = 0;
      document.querySelectorAll('.modul').forEach(m => {
        let w = 0;
        m.querySelectorAll('.lista-lekcji li').forEach(li => {
          const a = li.querySelector('a'); const ok = !q || (mapa.get(a.dataset.lekcja) || '').includes(q);
          li.hidden = !ok; if (ok) w++;
        });
        m.hidden = q && !w; if (q && w) m.querySelector('details').open = true; ile += w;
      });
      document.getElementById('brak').hidden = !(q && !ile);
    });
  }

  /* ---- pojawianie się ---- */
  const io = new IntersectionObserver(w => w.forEach(x => { if (x.isIntersecting) { x.target.classList.add('widoczne'); io.unobserve(x.target); } }), { threshold: .1 });
  document.querySelectorAll('.pojaw').forEach(e => io.observe(e));

  /* ---- konfetti z pikseli ---- */
  function konfetti(el){
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const r = el.getBoundingClientRect(), kol = ['#000','#ffd60a','#fff','#2e6fd6','#e0322b'];
    for (let i = 0; i < 40; i++) {
      const p = document.createElement('div'); p.className = 'piksel'; p.style.background = kol[i % kol.length];
      p.style.left = r.left + 10 + 'px'; p.style.top = r.top + 10 + 'px'; document.body.appendChild(p);
      const a = Math.random() * Math.PI * 2, v = 80 + Math.random() * 200;
      p.animate([{ transform: 'translate(0,0)' }, { transform: `translate(${Math.cos(a) * v}px,${Math.sin(a) * v + 160}px)` }], { duration: 800 + Math.random() * 400, easing: 'steps(10)', fill: 'forwards' }).onfinish = () => p.remove();
    }
  }
})();
