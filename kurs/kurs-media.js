// Oprawa kursu jak w odcinkach Chmuroholika: pikselowe sceny, ilustracje analogii,
// piszący terminal, chiptune'owa muzyka modułów, efekty dźwiękowe, XP i odznaki.
// Wszystko własne: sprite'y rysowane z siatek znaków, muzyka generowana w przeglądarce (Web Audio).
(function(){
  'use strict';
  const KLUCZ = 'chmuroholik-kurs-v1';
  const RUCH = !matchMedia('(prefers-reduced-motion: reduce)').matches;
  const czytaj = () => { try { const s = JSON.parse(localStorage.getItem(KLUCZ)) || {}; s.zrobione = s.zrobione || {}; s.dni = s.dni || {}; s.odznaki = s.odznaki || {}; s.dzwiek = s.dzwiek || { muz:false, sfx:true }; return s; } catch { return { zrobione:{}, dni:{}, odznaki:{}, dzwiek:{ muz:false, sfx:true } }; } };
  const zapisz = (zm) => { const s = czytaj(); zm(s); try { localStorage.setItem(KLUCZ, JSON.stringify(s)); } catch {} return s; };

  /* =============== SPRITE'Y =============== */
  const PAL = { k:'#000', w:'#fff', y:'#ffd60a', r:'#e0322b', b:'#2e6fd6', g:'#9aa0a6', o:'#f28c28', z:'#2fa84f', s:'#f1c27d', d:'#555', H:'#5a3a1e', p:'#7d3cff', c:'#7fd3ff', n:'#1b2a4a' };
  const S = {
    pingwin:['....kkkk....','...kkkkkk...','..kkwkkwkk..','..kkkookkk..','.kkkwwwwkkk.','kkkwwwwwwkkk','kkwwwwwwwwkk','kkwwwwwwwwkk','.kwwwwwwwwk.','.kkwwwwwwkk.','..kkkkkkkk..','.oooo..oooo.'],
    terminal:['kkkkkkkkkkkkkk','kwwwwwwwwwwwwk','kkkkkkkkkkkkkk','kkkkkkkkkkkkkk','kkzkkkkkkkkkkk','kkkzkkkkkkkkkk','kkkkzkkkkkkkkk','kkkzkkkkkkkkkk','kkzkkkzzzzkkkk','kkkkkkkkkkkkkk','.kkkkkkkkkkkk.'],
    folder:['kkkkk.......','kyyyyk......','kkkkkkkkkkkk','kyyyyyyyyyyk','kyyyyyyyyyyk','kyyyyyyyyyyk','kyyyyyyyyyyk','kkkkkkkkkkkk'],
    plik:['kkkkkkk.','kwwwwkwk','kwwwwkkk','kwkkkkwk','kwwwwwwk','kwkkkkwk','kwwwwwwk','kwkkkwwk','kwwwwwwk','kkkkkkkk'],
    kosz:['.kkkkkk.','kkkkkkkk','.kwkwkk.','.kwkwkk.','.kwkwkk.','.kwkwkk.','.kkkkkk.'],
    klucz:['.kkk.......','kyyyk......','kykykkkkkkk','kyyykyykyyk','.kkk.kk.kk.'],
    klodka:['..kkkk..','.k....k.','.k....k.','kkkkkkkk','kyyyyyyk','kyyk.yyk','kyyyyyyk','kkkkkkkk'],
    serwer:['kkkkkkkk','kwwwwwwk','kkkkkkkk','kwwwwzwk','kkkkkkkk','kwwwwzwk','kkkkkkkk','kwwwwwwk','kkkkkkkk','.k....k.'],
    globus:['...kkkk...','.kkbbzbkk.','kbbzzbbbbk','kbzzzbbzbk','kbbzbbzzbk','kbbbbbzzbk','kbzbbbbbbk','.kkbbbbkk.','...kkkk...'],
    dysk:['kkkkkkkkkk','kggggggggk','kgkkkkkkgk','kgkwwwwkgk','kgkkkkkkgk','kggggggggk','kggggggzgk','kkkkkkkkkk'],
    paczka:['..kkkkkkk..','.koooyoook.','kooooyooook','kkkkkykkkkk','kooooyooook','kooooyooook','kooooyooook','kkkkkkkkkkk'],
    zebatka:['...kk.kk...','..kggkggk..','.kkgggggkk.','kgggkkkgggk','.kggk.kggk.','.kggk.kggk.','kgggkkkgggk','.kkgggggkk.','..kggkggk..','...kk.kk...'],
    robot:['....k....','..kkkkk..','.kwwwwwk.','.kwbwbwk.','.kwwwwwk.','.kwkkkwk.','..kkkkk..','.kgggggk.','kkgggggkk','..k...k..'],
    krawat:['.kkkkkk.','.kwwwwk.','..kwwk..','...rr...','..krrk..','..krrk..','.krrrrk.','.krrrrk.','..krrk..','...kk...'],
    puchar:['kkkkkkkkk','kyyyyyyyk','kkyyyyykk','k.kyyyk.k','.kkyyykk.','...kyk...','...kyk...','..kkkkk..','.kyyyyyk.','.kkkkkkk.'],
    ksiazka:['kkkkkkkkkk','kwwwwkwwwk','kwkkwkwkkk','kwwwwkwwwk','kwkkwkwkkk','kwwwwkwwwk','kkkkkkkkkk'],
    lupa:['..kkkk...','.kwwwwk..','kwwccwwk.','kwcwwwwk.','kwwwwwwk.','.kwwwwk..','..kkkkkk.','......kkk','.......kk'],
    zegar:['..kkkkk..','.kwwwwwk.','kwwwkwwwk','kwwwkwwwk','kwwwkkkwk','kwwwwwwwk','kwwwwwwwk','.kwwwwwk.','..kkkkk..'],
    rura:['kkkkkkkkkkkk','kggggggggggk','kgwwwwwwwwgk','kggggggggggk','kkkkkkkkkkkk'],
    osoba:['...kkkk...','..kHHHHk..','..kssssk..','..kskksk..','..kssssk..','...kssk...','..kbbbbk..','.kbbbbbbk.','kbkbbbbkbk','kskbbbbksk','..kbbbbk..','..knnnnk..','..kn..nk..','..kk..kk..'],
    ochroniarz:['..kkkkkk..','..knnnnk..','..kssssk..','..kskksk..','..kssssk..','...kssk...','..knnnnk..','.knnynnnk.','knknnnnknk','ksknnnnksk','..knnnnk..','..kkkkkk..','..kk..kk..','..kk..kk..'],
    budynek:['..kkkkkk..','.kggggggk.','kkkkkkkkkk','kgcgcgcgck','kggggggggk','kgcgcgcgck','kggggggggk','kgcgcgcgck','kggggggggk','kggkkkkggk','kggkwwkggk','kkkkkkkkkk'],
    garnek:['..kkkkkk..','.k......k.','kkkkkkkkkk','kggggggggk','kggggggggk','kggggggggk','.kggggggk.','..kkkkkk..'],
    kamera:['kkkkkkk...','kgggggkk.k','kgkkkgkkkk','kgkbkgkkkk','kgkkkgkkkk','kgggggkk.k','kkkkkkk...'],
    glosnik:['....k...','...kk...','kkkgk.k.','kgggk..k','kgggk..k','kkkgk.k.','...kk...','....k...'],
    segregator:['kkkkkkkk','kyyyyyyk','kykkkkyk','kykwwkyk','kykkkkyk','kyyyyyyk','kyykkyyk','kyykkyyk','kyyyyyyk','kkkkkkkk'],
    sejf:['kkkkkkkkkk','kggggggggk','kgkkkkkkgk','kgkwwwwkgk','kgkwkkwkgk','kgkwwwwkgk','kgkkkkkkgk','kggggggggk','kkkkkkkkkk','.k......k.'],
    taksowka:['...kkkk....','..kyyyyk...','kkkkkkkkkk.','kyyyyyyyyyk','kywwkyywwyk','kkkkkkkkkkk','.kgk...kgk.','..k.....k..'],
    pizza:['kkkkkkkkkk','kyyryyyyyk','.kyyyyryk.','.kyryyyyk.','..kyyyyk..','..kyyryk..','...kyyk...','...kyyk...','....kk....'],
    koperta:['kkkkkkkkkk','kwkwwwwkwk','kwwkwwkwwk','kwwwkkwwwk','kwwwwwwwwk','kkkkkkkkkk'],
    git:['.zz.......','.zz.......','..k.......','..k...zz..','..k..kzz..','..k.k.....','..kk......','..k.......','.zz.......','.zz.......'],
    zarowka:['..kkkk..','.kyyyyk.','kyyyyyyk','kyyyyyyk','.kyyyyk.','..kyyk..','..kggk..','..kggk..','...kk...'],
    bomba:['......k.','.....k.r','..kkkk..','.kkkkkk.','kkwkkkkk','kkkkkkkk','kkkkkkkk','.kkkkkk.','..kkkk..'],
    olowek:['......kk','.....kyk','....kyk.','...kyk..','..kyk...','.kyk....','kwk.....','kk......'],
    strzalka:['...k....','...kk...','kkkkwk..','kwwwwwk.','kwwwwwwk','kwwwwwk.','kkkkwk..','...kk...','...k....'],
    megafon:['......kk','....kkwk','kkkkwwwk','kwwwwwwk','kwwwwwwk','kkkkwwwk','..k.kkwk','..k...kk'],
    ciezarowka:['kkkkkkk....','koooook....','koooookkkk.','koooookwwkk','koooookkkkk','kkkkkkkkkkk','.kgk...kgk.','..k.....k..'],
    wykres:['k.........','k......z..','k.....z.z.','k..z.z...z','k.z.z.....','kz........','kkkkkkkkkk'],
    tarcza:['kkkkkkkkk','kyyyyyyyk','kyyyyyykk','kyyyyykyk','kykyykyyk','kyykkyyyk','.kyyyyyk.','..kyyyk..','...kkk...'],
    chmura:['.....kkkk.......','....kwwwwk......','..kkwwwwwwkkk...','.kwwwwwwwwwwwk..','kwwwwwwwwwwwwwk.','kwwwwwwwwwwwwwwk','kwwwwwwwwwwwwwwk','.kkkkkkkkkkkkkk.'],
    komputer:['kkkkkkkkkk','kwwwwwwwwk','kwkkkkkkwk','kwkzkkkkwk','kwkkzkkkwk','kwkzkkkkwk','kwkkkkkkwk','kwwwwwwwwk','kkkkkkkkkk','.kwwwwwwk.','kkkkkkkkkk'],
    tabela:['kkkkkkkkkkk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk','kwwkwwwkwwk','kkkkkkkkkkk'],
    nuta:['...kkk','...k.k','...k.k','...k..','.kkk..','kkkk..','.kk...'],
    gwiazda:['....k....','...kyk...','kkkkyykkk','.kyyyyyk.','..kyyyk..','.kyykyyk.','.kk...kk.'],
    ksiezyc:['..kkk...','.kyyk...','kyyk....','kyyk....','kyyk....','.kyyk...','..kkkk..'],
    ogien:['...r....','..rr..r.','..ror.r.','.roorrr.','.rooyor.','royyyoor','royyyyor','.ryyyyr.','..rrrr..']
  };
  function rysuj(nazwa, skala, zamiana){
    const g = S[nazwa] || S.pingwin, c = document.createElement('canvas'), w = Math.max(...g.map(r => r.length));
    c.width = w * skala; c.height = g.length * skala; c.setAttribute('aria-hidden', 'true'); c.className = 'spr';
    const x = c.getContext('2d');
    g.forEach((r, yy) => [...r].forEach((ch, xx) => { const k = (zamiana && zamiana[ch]) || PAL[ch]; if (k) { x.fillStyle = k; x.fillRect(xx * skala, yy * skala, skala, skala); } }));
    return c;
  }

  /* =============== DŹWIĘK (Web Audio, własna muzyka) =============== */
  let ac = null, master = null, muzykaGra = false, harmonogram = null;
  const stanD = czytaj().dzwiek;
  function audio(){
    if (!ac) {
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
      ac = new AC(); master = ac.createGain(); master.gain.value = .9;
      const lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 6000;
      master.connect(lp); lp.connect(ac.destination);
    }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  }
  const hz = m => 440 * Math.pow(2, (m - 69) / 12);
  const fala25 = () => { const re = new Float32Array(32), im = new Float32Array(32); for (let n = 1; n < 32; n++) re[n] = (2 / (n * Math.PI)) * Math.sin(n * Math.PI * .25); return ac.createPeriodicWave(re, im); };
  let FALA25 = null;
  function ton(t, f, dl, typ, glos, dokad){
    const o = ac.createOscillator(), g = ac.createGain();
    if (typ === 'p25') { FALA25 = FALA25 || fala25(); o.setPeriodicWave(FALA25); } else o.type = typ;
    o.frequency.setValueAtTime(f, t); if (dokad) o.frequency.exponentialRampToValueAtTime(dokad, t + dl);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(glos, t + .006); g.gain.exponentialRampToValueAtTime(.0005, t + dl);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dl + .02);
  }
  let SZUM = null;
  function szum(t, dl, glos, filtr){
    if (!SZUM) { SZUM = ac.createBuffer(1, ac.sampleRate * .5, ac.sampleRate); const d = SZUM.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
    const s = ac.createBufferSource(), g = ac.createGain(), f = ac.createBiquadFilter();
    s.buffer = SZUM; f.type = 'highpass'; f.frequency.value = filtr || 6000;
    g.gain.setValueAtTime(glos, t); g.gain.exponentialRampToValueAtTime(.0005, t + dl);
    s.connect(f); f.connect(g); g.connect(master); s.start(t); s.stop(t + dl + .02);
  }
  const SFX = {
    klik: () => { const t = ac.currentTime; ton(t, 1400, .03, 'square', .05); },
    typ: () => { const t = ac.currentTime; szum(t, .012, .05, 3000 + Math.random() * 3000); },
    odkryj: () => { const t = ac.currentTime; ton(t, 300, .25, 'p25', .07, 1200); },
    ding: () => { const t = ac.currentTime; ton(t, hz(84), .35, 'triangle', .12); ton(t + .09, hz(91), .5, 'triangle', .12); },
    fanfara: () => { const t = ac.currentTime; [72, 76, 79, 84, 79, 84].forEach((n, i) => ton(t + i * .09, hz(n), i === 5 ? .6 : .14, 'p25', .08)); [48, 55].forEach((n, i) => ton(t + i * .27, hz(n), .5, 'triangle', .12)); },
    odznaka: () => { const t = ac.currentTime; [76, 79, 83, 88, 91].forEach((n, i) => ton(t + i * .07, hz(n), .3, 'square', .05)); ton(t + .38, hz(96), .8, 'triangle', .1); },
    start: () => { const t = ac.currentTime; [60, 64, 67, 72].forEach(n => ton(t, hz(n), 1.2, 'triangle', .05)); ton(t, hz(48), 1.2, 'triangle', .07); }
  };
  function graj(nazwa){ if (!czytaj().dzwiek.sfx) return; if (!audio()) return; try { SFX[nazwa](); } catch {} }

  // Muzyka modułu: inna tonacja, tempo i melodia dla każdego z 14 modułów (deterministycznie z numeru).
  function utworModulu(m){
    let ziarno = 1234 + m * 977; const los = () => (ziarno = (ziarno * 16807) % 2147483647) / 2147483647;
    const korzenie = [57, 60, 55, 62, 52, 57, 59, 53, 62, 55, 57, 64, 60, 57];
    const moll = m % 3 !== 1;
    const skala = moll ? [0, 3, 5, 7, 10, 12, 15, 17] : [0, 2, 4, 7, 9, 12, 14, 16];
    const prog = moll ? [[0, 'm'], [8, 'M'], [3, 'M'], [10, 'M']] : [[0, 'M'], [7, 'M'], [9, 'm'], [5, 'M']];
    const tempo = 100 + ((m * 13) % 36);
    const motyw = Array.from({ length: 16 }, (_, i) => (i % 4 === 3 && los() < .5) ? null : skala[Math.floor(los() * 6)]);
    return { r: korzenie[m % korzenie.length], prog, tempo, motyw, moll };
  }
  function muzykaStart(m){
    if (!audio() || muzykaGra) return; muzykaGra = true;
    const u = utworModulu(m), osemka = 60 / u.tempo / 2;
    let krok = 0, nast = ac.currentTime + .1;
    harmonogram = setInterval(() => {
      while (nast < ac.currentTime + .15) {
        const takt = Math.floor(krok / 8) % 4, w = krok % 8, [st, q] = u.prog[takt], root = u.r + st;
        const akord = [0, q === 'm' ? 3 : 4, 7];
        // bas: ósemki na prymie i kwincie
        ton(nast, hz(root - 24 + (w % 4 === 2 ? 7 : 0)), osemka * .9, 'triangle', .13);
        // arpeggio w szesnastkach, ciche
        for (let h = 0; h < 2; h++) ton(nast + h * osemka / 2, hz(root + 12 + akord[(krok * 2 + h) % 3]), osemka * .45, 'p25', .018);
        // melodia: motyw z wariacją co drugi przebieg
        const nuta = u.motyw[(krok + (Math.floor(krok / 32) % 2 ? 4 : 0)) % 16];
        if (w % 2 === 0 && nuta !== null) ton(nast, hz(u.r + 12 + nuta), osemka * 1.6, 'square', .028);
        // perkusja: stopa, werbel, hi-hat
        if (w === 0 || w === 4) ton(nast, 150, .12, 'sine', .22, 40);
        if (w === 2 || w === 6) szum(nast, .09, .06, 1800);
        szum(nast, .025, .025, 8000);
        nast += osemka; krok++;
      }
    }, 25);
  }
  function muzykaStop(){ muzykaGra = false; clearInterval(harmonogram); harmonogram = null; }

  /* przełączniki w menu */
  const bm = document.getElementById('przel-muzyka'), bs = document.getElementById('przel-sfx');
  const modul = +(document.querySelector('.lekcja')?.dataset.modul || 0);
  function ikonyPrzelacznikow(){
    const d = czytaj().dzwiek;
    if (bm) { bm.setAttribute('aria-pressed', d.muz); bm.textContent = d.muz ? '♪ ON' : '♪ OFF'; }
    if (bs) { bs.setAttribute('aria-pressed', d.sfx); bs.textContent = d.sfx ? 'SFX ON' : 'SFX OFF'; }
  }
  ikonyPrzelacznikow();
  bm && bm.addEventListener('click', () => {
    const d = zapisz(s => { s.dzwiek.muz = !s.dzwiek.muz; }).dzwiek;
    if (d.muz) { muzykaStart(modul); przyznaj('dj'); } else muzykaStop();
    ikonyPrzelacznikow();
  });
  bs && bs.addEventListener('click', () => { zapisz(s => { s.dzwiek.sfx = !s.dzwiek.sfx; }); ikonyPrzelacznikow(); graj('klik'); });
  // przeglądarka wymaga gestu: muzykę wznawiamy przy pierwszym kliknięciu, jeśli była włączona
  addEventListener('pointerdown', function raz(){ if (czytaj().dzwiek.muz) muzykaStart(modul); removeEventListener('pointerdown', raz); }, { once: true });
  // klik na przyciskach i linkach
  document.addEventListener('click', e => { if (e.target.closest('a.btn, .lista-lekcji a, .lekcje-modulu summary, .podpowiedzi button')) graj('klik'); });

  /* =============== SCENA TYTUŁOWA LEKCJI =============== */
  const TEMATY = [
    [/folder|ścież|katalog|\bcd\b|\bls\b|pwd|plik/, ['folder', 'plik', 'pingwin']],
    [/uprawnie|chmod|chown|sudo|root|użytkown|grup|hasł|acl|umask/, ['klucz', 'klodka', 'osoba']],
    [/proces|\bps\b|\btop\b|kill|sygna|zadania w tle|jobs|nice|pamięć/, ['zebatka', 'wykres', 'pingwin']],
    [/grep|sed|awk|regex|wyrażen|tekst|potok|przekier|sort|uniq|cut|napis/, ['lupa', 'rura', 'plik']],
    [/dysk|partycj|lvm|mount|system(y)? plików|fstab|raid|ext4|xfs|swap|df\b|du\b/, ['dysk', 'serwer', 'pingwin']],
    [/pakiet|apt|dnf|rpm|deb|repozyt|snap|flatpak|kompil/, ['paczka', 'ciezarowka', 'pingwin']],
    [/sieć|sieci|\bip\b|dns|ssh|port|firewall|tcp|http|curl|ping|routing|vpn|tcpdump/, ['globus', 'serwer', 'koperta']],
    [/bezpiecz|selinux|apparmor|audyt|fail2ban|szyfr|certyfik|gpg|utwardz|aide/, ['tarcza', 'klodka', 'ochroniarz']],
    [/cron|harmonogr|timer|planow|o trzeciej/, ['zegar', 'robot', 'pingwin']],
    [/git\b|ansible|automaty|playbook|wiele serwer/, ['robot', 'git', 'serwer']],
    [/usług|systemd|nginx|apache|baz[ay]|log|journal|backup|kopi|monitor|kontener|docker/, ['serwer', 'sejf', 'wykres']],
    [/rekrutac|rozmow|cv\b|pytania/, ['krawat', 'osoba', 'pingwin']],
    [/projekt|egzamin|portfolio|finał/, ['puchar', 'gwiazda', 'pingwin']],
    [/skrypt|bash|zmienn|funkcj|pętl|warun|tablic|argument|shebang|błęd|debug/, ['terminal', 'olowek', 'pingwin']],
    [/edytor|nano|vim|vi\b|mc\b/, ['plik', 'olowek', 'pingwin']],
    [/pomoc|man\b|help/, ['ksiazka', 'lupa', 'pingwin']]
  ];
  function scenaDla(tekst){ const t = tekst.toLowerCase(); for (const [re, s] of TEMATY) if (re.test(t)) return s; return ['terminal', 'chmura', 'pingwin']; }

  const lekcja = document.querySelector('.lekcja');
  if (lekcja) {
    const nr = +lekcja.dataset.nr, h1 = lekcja.querySelector('h1');
    const sprite = scenaDla((h1?.textContent || '') + ' ' + (lekcja.dataset.tematy || ''));
    const pl = document.getElementById('plansza');
    if (pl) {
      const pierwszy = lekcja.querySelector('.kod code');
      const komenda = (pierwszy ? pierwszy.textContent.split('\n').find(l => l.trim() && !l.trim().startsWith('#')) || 'echo "Cześć"' : 'echo "Cześć"').trim().slice(0, 38);
      pl.innerHTML = `<div class="sc-niebo"></div><div class="sc-chmury"></div><div class="sc-ziemia"></div>
        <div class="sc-numer"><span>LEKCJA</span><b>${nr}</b></div>
        <div class="sc-glowny"></div><div class="sc-pomocnik"></div><div class="sc-maskotka"><div class="sc-dymek"></div></div>
        <div class="sc-term"><div class="sc-term-belka"></div><pre><span class="sc-p">$ </span><span class="sc-k"></span><span class="sc-kursor">█</span></pre></div>`;
      pl.querySelector('.sc-glowny').appendChild(rysuj(sprite[0], 9));
      pl.querySelector('.sc-pomocnik').appendChild(rysuj(sprite[1], 6));
      pl.querySelector('.sc-maskotka').appendChild(rysuj('pingwin', 6));
      for (let i = 0; i < 4; i++) { const c = rysuj('chmura', 3 + (i % 2)); c.style.cssText = `left:${10 + i * 24}%;top:${8 + (i % 2) * 18}%;animation-delay:${-i * 4}s`; pl.querySelector('.sc-chmury').appendChild(c); }
      const dymki = ['Do dzieła!', 'Odpalamy terminal!', 'Bez stresu, krok po kroku.', 'To będzie dobra lekcja.', 'Kawa jest? Zaczynamy.', 'Czas na kolejny level!'];
      pl.querySelector('.sc-dymek').textContent = dymki[nr % dymki.length];
      const k = pl.querySelector('.sc-k');
      if (RUCH) { let i = 0; const t = setInterval(() => { k.textContent = komenda.slice(0, ++i); if (i >= komenda.length) clearInterval(t); }, 70); }
      else k.textContent = komenda;
    }
    // przyjemny „start” przy wejściu, jeśli dźwięki już odblokowane
    if (czytaj().dzwiek.sfx && ac) graj('start');
  }

  /* =============== IKONY SEKCJI =============== */
  const IK_SEKCJI = [[/^wstęp/i, 'megafon'], [/typow|błąd|błęd/i, 'bomba'], [/^zadanie/i, 'olowek'], [/^co dalej/i, 'strzalka'], [/pułapk|uwaga/i, 'bomba'], [/ściąg|podsumow|zapamięt/i, 'zarowka']];
  document.querySelectorAll('.tresc-lekcji section > h2').forEach(h => {
    const t = h.textContent.trim();
    let n = (IK_SEKCJI.find(([re]) => re.test(t)) || [])[1];
    if (!n) n = scenaDla(t)[0];
    const ik = h.querySelector('.ikona-r'); if (ik) ik.remove();
    const c = rysuj(n, 3); c.classList.add('ik-sekcji'); h.prepend(c);
  });
  document.querySelectorAll('.ramka-tytul').forEach(r => { const n = /zapamięt/i.test(r.textContent) ? 'zarowka' : /dociekl/i.test(r.textContent) ? 'lupa' : null; if (n) { const c = rysuj(n, 2); c.classList.add('ik-ramki'); r.prepend(c); } });

  /* =============== ILUSTRACJE ANALOGII =============== */
  const ANALOGIE = [
    [/urzędni|okienk\w* w urzędzie|w urzędzie/i, 'osoba', 'urzędnik za szybą'],
    [/budyn\w*|piętr/i, 'budynek', 'budynek z piętrami'],
    [/kuchni|kucharz|przepis/i, 'garnek', 'kuchnia'],
    [/kamer/i, 'kamera', 'kamera'],
    [/głośnik/i, 'glosnik', 'dwa głośniki'],
    [/segregator|teczk/i, 'segregator', 'segregator'],
    [/\brur[aęyo]\w*/i, 'rura', 'rura'],
    [/sejf/i, 'sejf', 'sejf'],
    [/ochroniarz|bramkarz/i, 'ochroniarz', 'ochroniarz'],
    [/taksówk/i, 'taksowka', 'taksówka'],
    [/pizz/i, 'pizza', 'pizza'],
    [/paczk|sortowni|kurier/i, 'paczka', 'paczka'],
    [/kłódk|zamek w drzwiach/i, 'klodka', 'kłódka'],
    [/\bklucz\w*/i, 'klucz', 'klucz'],
    [/(?:^|[^a-ząćęłńóśźż])list(?![a-ząćęłńóśźż])|koperta|poczt/i, 'koperta', 'list'],
    [/robot/i, 'robot', 'robot'],
    [/pożar|płon/i, 'ogien', 'pożar']
  ];
  if (lekcja) {
    const uzyte = new Set(); let ile = 0;
    lekcja.querySelectorAll('.tresc-lekcji section > p').forEach(p => {
      if (ile >= 4) return;
      const t = p.textContent;
      for (const [re, spr, nazwa] of ANALOGIE) {
        if (uzyte.has(spr) || !re.test(t)) continue;
        uzyte.add(spr); ile++;
        const zdanie = (t.split(/(?<=[.!?])\s+/).find(z => re.test(z)) || t).trim();
        const f = document.createElement('figure'); f.className = 'analogia' + (ile % 2 ? '' : ' lewa');
        const ram = document.createElement('div'); ram.className = 'analogia-ram'; ram.appendChild(rysuj(spr, 6));
        f.appendChild(ram);
        const cap = document.createElement('figcaption'); cap.innerHTML = `<b>${nazwa}</b>`; cap.appendChild(document.createTextNode(zdanie.length > 110 ? zdanie.slice(0, 107) + '…' : zdanie));
        f.appendChild(cap);
        p.before(f);
        break;
      }
    });
  }

  /* =============== PISZĄCY TERMINAL =============== */
  if (RUCH) {
    const ioK = new IntersectionObserver(w => w.forEach(x => {
      if (!x.isIntersecting) return; ioK.unobserve(x.target);
      const code = x.target.querySelector('code'), pelny = code.textContent;
      if (pelny.length > 600) return;
      code.dataset.pelny = pelny; code.textContent = ''; x.target.classList.add('pisze');
      let i = 0; const dl = Math.max(4, Math.min(22, 1800 / pelny.length));
      const t = setInterval(() => {
        i += pelny.length > 200 ? 3 : 1; code.textContent = pelny.slice(0, i);
        if (i % 3 === 0 && pelny[i] && pelny[i] !== ' ') graj('typ');
        if (i >= pelny.length) { clearInterval(t); code.textContent = pelny; x.target.classList.remove('pisze'); }
      }, dl);
      x.target.addEventListener('click', () => { clearInterval(t); code.textContent = pelny; x.target.classList.remove('pisze'); }, { once: true });
    }), { threshold: .6 });
    document.querySelectorAll('.tresc-lekcji .kod').forEach(k => ioK.observe(k));
  }

  /* =============== PASEK CZYTANIA =============== */
  const pc = document.getElementById('pasek-czytania');
  if (pc) { const f = () => { const h = document.documentElement; pc.style.width = Math.min(100, h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight) * 100) + '%'; }; addEventListener('scroll', f, { passive: true }); f(); }

  /* =============== XP, POZIOMY, ODZNAKI =============== */
  const POZIOMY = [[0, 'Stażysta'], [40, 'Kursant'], [120, 'Power user'], [260, 'Skrypciarz'], [450, 'Junior admin'], [700, 'Admin'], [1000, 'Starszy admin'], [1400, 'Guru terminala'], [1800, 'Root']];
  const MODULY = [0, 4, 18, 30, 40, 48, 55, 63, 67, 77, 86, 100, 105, 109, 117]; // ostatnia lekcja każdego modułu (granice)
  const IK_MOD = ['chmura', 'komputer', 'zebatka', 'ksiazka', 'tabela', 'tarcza', 'dysk', 'paczka', 'globus', 'klodka', 'serwer', 'robot', 'krawat', 'puchar'];
  const modulLekcji = n => MODULY.findIndex((g, i) => i > 0 && n <= g) - 1;
  const lekcjeModulu = m => { const a = []; for (let n = MODULY[m] + 1; n <= MODULY[m + 1]; n++) a.push(n); return a; };
  function xp(s){ const l = Object.keys(s.zrobione).length; let mod = 0; for (let m = 0; m < 14; m++) if (lekcjeModulu(m).every(n => s.zrobione[n])) mod++; return l * 10 + mod * 50 + Object.keys(s.odznaki).length * 5; }
  function poziom(p){ let i = 0; while (i + 1 < POZIOMY.length && p >= POZIOMY[i + 1][0]) i++; return i; }
  const ODZ = [
    { id: 'start', n: 'Pierwsze kroki', o: 'ukończ pierwszą lekcję', s: 'terminal', w: s => Object.keys(s.zrobione).length >= 1 },
    { id: 'l10', n: 'Dziesiątka', o: 'ukończ 10 lekcji', s: 'gwiazda', w: s => Object.keys(s.zrobione).length >= 10 },
    { id: 'l59', n: 'Półmetek', o: 'ukończ połowę kursu', s: 'gwiazda', w: s => Object.keys(s.zrobione).length >= 59 },
    ...IK_MOD.map((sp, m) => ({ id: 'm' + m, n: 'Moduł ' + m, o: 'ukończ cały moduł ' + m, s: sp, w: s => lekcjeModulu(m).every(n => s.zrobione[n]) })),
    { id: 'seria3', n: 'Trzy dni z rzędu', o: 'ucz się 3 dni pod rząd', s: 'ogien', w: s => serie(s) >= 3 },
    { id: 'seria7', n: 'Tydzień w terminalu', o: 'ucz się 7 dni pod rząd', s: 'ogien', w: s => serie(s) >= 7 },
    { id: 'nocny', n: 'Nocny dyżur', o: 'ukończ lekcję między północą a piątą', s: 'ksiezyc', w: s => Object.values(s.zrobione).some(t => new Date(t).getHours() < 5) },
    { id: 'dj', n: 'DJ serwerowni', o: 'włącz muzykę kursu', s: 'nuta', w: s => s.odznaki.dj },
    { id: 'root', n: 'Root', o: 'ukończ cały kurs', s: 'puchar', w: s => Object.keys(s.zrobione).length >= 117 }
  ];
  function serie(s){ const dni = new Set(Object.keys(s.dni)); let max = 0; dni.forEach(d => { let n = 0, t = new Date(d + 'T12:00'); while (dni.has(t.toISOString().slice(0, 10))) { n++; t.setDate(t.getDate() - 1); } max = Math.max(max, n); }); return max; }
  const dzis = () => new Date(Date.now() - new Date().getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
  function przyznaj(id){ const s = czytaj(); if (s.odznaki[id]) return; zapisz(x => { x.odznaki[id] = Date.now(); }); const o = ODZ.find(z => z.id === id); if (o) alertOdznaki(o); odswiezPoziom(); }
  function sprawdzOdznaki(){ const s = czytaj(); ODZ.forEach(o => { if (!s.odznaki[o.id] && o.id !== 'dj' && o.w(s)) przyznaj(o.id); }); }

  let kolejka = Promise.resolve();
  function alertOdznaki(o){
    kolejka = kolejka.then(() => new Promise(gotowe => {
      graj('odznaka');
      const d = document.createElement('div'); d.className = 'alert-odznaki'; d.setAttribute('role', 'alertdialog'); d.setAttribute('aria-label', 'Zdobyto odznakę: ' + o.n);
      d.innerHTML = `<div class="okno duze"><div class="belka"><span>Gablota.app</span></div><div class="tresc"><div class="ao-ikona"></div><div><b>Zdobyto odznakę!</b><p class="ao-n"></p><p class="ao-o"></p><button class="btn domyslny zolty" type="button">OK</button></div></div></div>`;
      d.querySelector('.ao-ikona').appendChild(rysuj(o.s, 8));
      d.querySelector('.ao-n').textContent = o.n; d.querySelector('.ao-o').textContent = o.o + ' · +5 XP';
      document.body.appendChild(d);
      const b = d.querySelector('button'); b.focus();
      const zamknij = () => { d.remove(); gotowe(); }; b.addEventListener('click', zamknij); setTimeout(() => d.isConnected && zamknij(), 6000);
    }));
  }
  function odswiezPoziom(){
    const s = czytaj(), p = xp(s), i = poziom(p), el = document.getElementById('poziom');
    if (el) { el.textContent = `LVL ${i + 1} · ${p} XP`; el.title = POZIOMY[i][1]; }
    const t = document.getElementById('xp-tekst');
    if (t) {
      const nast = POZIOMY[i + 1];
      t.textContent = `Poziom ${i + 1}: ${POZIOMY[i][1]} · ${p} XP`;
      document.getElementById('xp-nast').textContent = nast ? `do „${nast[1]}”: ${nast[0] - p} XP` : 'maksymalny poziom!';
      document.getElementById('xp-i').style.width = (nast ? (p - POZIOMY[i][0]) / (nast[0] - POZIOMY[i][0]) * 100 : 100) + '%';
      const g = document.getElementById('odznaki'); g.innerHTML = '';
      ODZ.forEach(o => {
        const ma = !!s.odznaki[o.id], d = document.createElement('div'); d.className = 'odznaka' + (ma ? ' zdobyta' : '');
        d.title = o.o; d.appendChild(rysuj(o.s, 5));
        d.insertAdjacentHTML('beforeend', `<b></b><small></small>`); d.querySelector('b').textContent = o.n; d.querySelector('small').textContent = ma ? 'zdobyta' : o.o;
        g.appendChild(d);
      });
    }
  }
  // ukończenie lekcji: fanfara, dzień nauki, odznaki
  const box = document.getElementById('ukonczone');
  if (box) box.addEventListener('change', () => setTimeout(() => {
    if (box.checked) { graj('fanfara'); zapisz(s => { s.dni[dzis()] = 1; }); }
    sprawdzOdznaki(); odswiezPoziom();
    const nr = +lekcja.dataset.nr, m = modulLekcji(nr);
    if (box.checked && lekcjeModulu(m).every(n => czytaj().zrobione[n])) graj('fanfara');
  }, 30));
  document.querySelectorAll('.rozwiazanie').forEach(d => d.addEventListener('toggle', () => { if (d.open) graj('odkryj'); }));
  sprawdzOdznaki(); odswiezPoziom();
})();
