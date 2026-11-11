#!/usr/bin/env python3
"""Generator kursu „Linux i Bash od zera do admina” dla strony Chmuroholika.

Wejście: katalog z plikami XML pobranymi z dokumentu Claude Docs
(<zakładka>-pNN.xml: 00-plan, m00 … m13). Wyjście: strona-chmuroholik/kurs/.

Scenariusze odcinków zamieniamy na lekcje do czytania:
- didaskalia ([na ekranie: …], [pauza], [cięcie …]) i notatki B-ROLL wypadają,
  a komendy pokazywane na ekranie zostają jako kod;
- „Hak” → „Wstęp”, „Zapowiedź” → „Co dalej”;
- „Typowy błąd” → ramka ostrzeżenia, „Plansza: …” → „Do zapamiętania”,
  „[dla zaawansowanych: …]” → „Dla dociekliwych”;
- „Zadanie dla widza” → zadanie z rozwijanym rozwiązaniem (rozwiązanie
  przeniesione z początku następnego odcinka);
- język nagrania („odcinek”, „widz”) → język kursu („lekcja”, „Ty”).
użycie: python3 narzedzia/generuj_kurs.py <katalog-xml>
"""
import subprocess, glob, html, json, os, re, sys
import xml.etree.ElementTree as ET

ZRODLO = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WYJ = os.path.join(ROOT, 'kurs')
os.makedirs(WYJ, exist_ok=True)


# ---------- wczytanie XML (sklejenie stron) ----------
def wczytaj(zakladka):
    pliki = sorted(glob.glob(os.path.join(ZRODLO, f'{zakladka}-p*.xml')))
    if not pliki:
        raise SystemExit(f'brak plików dla {zakladka}')
    dzieci = []

    def bez_luk(el):
        for c in list(el):
            if c.tag == 'gap':
                el.remove(c)
            else:
                bez_luk(c)

    def znajdz(lista, sufiks, tag):
        for el in lista:
            for x in el.iter(tag):
                if (x.get('id') or '').endswith(sufiks):
                    return x
        return None

    for p in pliki:
        s = open(p, encoding='utf-8').read()
        d = ET.fromstring(s)
        bez_luk(d)
        if d.get('parent'):
            # dokończenie rozciętego bloku (np. tabeli) z poprzedniej strony
            for el in d:
                sufiks = '.' + el.get('id', '').rsplit('.', 1)[-1]
                cel = znajdz(dzieci, sufiks, el.tag)
                if cel is None:
                    raise SystemExit(f'nie znalazłem {el.tag} {el.get("id")} z {p}')
                for c in el:
                    cel.append(c)
            continue
        dzieci.extend(list(d))
    return dzieci


# ---------- tekst i inline ----------
ZAMIANY = [
    # kolejność ma znaczenie: najpierw całe frazy, potem pojedyncze słowa
    (r'\bRozwiązanie (?:zadania )?(?:znajdziesz )?na początku następnego odcinka\.?', 'Rozwiązanie znajdziesz pod spodem.'),
    (r'\bRozwiązanie w następnym odcinku\.?', 'Rozwiązanie znajdziesz pod spodem.'),
    (r'\bw tym odcinku\b', 'w tej lekcji'), (r'\bW tym odcinku\b', 'W tej lekcji'),
    (r'\bw tej serii\b', 'w tym kursie'), (r'\bW tej serii\b', 'W tym kursie'),
    (r'\bcałej serii\b', 'całego kursu'), (r'\bcała seria\b', 'cały kurs'), (r'\bcałą serię\b', 'cały kurs'),
    (r'\bod środka serii\b', 'od połowy kursu'), (r'\bserii\b', 'kursu'),
    (r'\b(n|N)astępnym odcinku\b', r'\1astępnej lekcji'), (r'\b(n|N)astępnego odcinka\b', r'\1astępnej lekcji'),
    (r'\b(n|N)astępny odcinek\b', r'\1astępna lekcja'), (r'\b(n|N)astępnym odcinkiem\b', r'\1astępną lekcją'),
    (r'\b(p|P)oprzednim odcinku\b', r'\1oprzedniej lekcji'), (r'\b(p|P)oprzedniego odcinka\b', r'\1oprzedniej lekcji'),
    (r'\b(p|P)oprzedni odcinek\b', r'\1oprzednia lekcja'),
    (r'\b(d|D)zisiejszego odcinka\b', r'\1zisiejszej lekcji'), (r'\b(d|D)zisiejszym odcinku\b', r'\1zisiejszej lekcji'),
    (r'\b(o|O)statnim odcinku\b', r'\1statniej lekcji'), (r'\b(o|O)statniego odcinka\b', r'\1statniej lekcji'),
    (r'\b(p|P)ierwszym odcinku\b', r'\1ierwszej lekcji'), (r'\b(p|P)ierwszego odcinka\b', r'\1ierwszej lekcji'),
    (r'\b(p|P)ierwszych odcinków\b', r'\1ierwszych lekcji'), (r'\b(k|K)olejnych odcinkach\b', r'\1olejnych lekcjach'),
    (r'\b(k|K)olejnym odcinku\b', r'\1olejnej lekcji'), (r'\b(t|T)ego odcinka\b', r'\1ej lekcji'),
    (r'\b(t|T)en odcinek\b', r'\1a lekcja'), (r'\b(t|T)ym odcinkiem\b', r'\1ą lekcją'),
    (r'\bodcinkach\b', 'lekcjach'), (r'\bodcinków\b', 'lekcji'), (r'\bodcinkami\b', 'lekcjami'), (r'\bodcinkom\b', 'lekcjom'),
    (r'\bodcinku\b', 'lekcji'), (r'\bodcinka\b', 'lekcji'), (r'\bodcinkiem\b', 'lekcją'), (r'\bodcinki\b', 'lekcje'),
    (r'\bodcinek\b', 'lekcja'), (r'\bOdcinek\b', 'Lekcja'), (r'\bodc\. ', 'lekcja '),
    (r'\bwidzowie\b', 'kursanci'), (r'\bwidzów\b', 'kursantów'), (r'\bwidzom\b', 'kursantom'),
    (r'\bwidza\b', 'kursanta'), (r'\bwidzowi\b', 'kursantowi'), (r'\bwidz\b', 'kursant'),
    (r'\bnowych widzów\b', 'nowych osób'), (r'\bna kanale\b', 'w kursie'),
    (r'\b(n|N)agrani[ae] ekranu\b', r'\1agranie ekranu'),
]


def przymiotnik(m):
    """„osobny odcinek” → „osobna lekcja”, „całego odcinka” → „całej lekcji” itd."""
    przym, rzecz = m.group(1), m.group(2)
    rdzen = None
    for kon, nowe in ((('ego',), {'odcinka': 'ej'}), (('ym', 'im'), {'odcinku': 'ej', 'odcinkiem': 'ą'}), (('y', 'i'), {'odcinek': 'a'})):
        for k in kon:
            if przym.endswith(k) and rzecz in nowe:
                rdzen = przym[: -len(k)]
                # ostatni → ostatnia, tani → tania (miękki temat zostawia „i”)
                if k in ('i', 'im') and nowe[rzecz] in ('a', 'ej', 'ą'):
                    rdzen += 'i'
                    if nowe[rzecz] == 'ej':
                        return f'{rdzen}ej {LEKCJA[rzecz]}'
                return f'{rdzen}{nowe[rzecz]} {LEKCJA[rzecz]}'
    if przym.lower() in ('ten',) and rzecz == 'odcinek':
        return przym[0] + 'a ' + LEKCJA[rzecz]
    return m.group(0)


LEKCJA = {'odcinek': 'lekcja', 'odcinka': 'lekcji', 'odcinku': 'lekcji', 'odcinkiem': 'lekcją'}


KONCOWKI = [
    ('Dobra, nie poczekam, montaż przytnie.', ''),
    ('na którym nagrywam', 'na którym pracuję'), ('bo nagrywam na maszynie', 'bo pracuję na maszynie'),
    ('„tylko obejrzałeś kurs na YouTubie”', '„tylko przeczytałeś kurs w internecie”'),
    ('Napisz w komentarzu, ile punktów zdobyłeś w egzaminie próbnym za pierwszym i za drugim razem. Niech kolejni kursanci zobaczą, że postęp jest prawdziwy.',
     'Zapisz, ile punktów zdobyłeś w egzaminie próbnym za pierwszym i za drugim razem. Różnica między tymi liczbami to Twój dowód, że postęp jest prawdziwy.'),
    ('Wrzuć link do swojego repozytorium z projektami albo z laboratorium. Najciekawsze omówię w osobnej lekcji.',
     'Opublikuj repozytorium z projektami i laboratorium. To Twoje portfolio na rozmowę rekrutacyjną.'),
    ('Napisz, czego chcesz dalej: Python dla admina? Kubernetes od zera? Przygotowanie do konkretnego certyfikatu? Seria idzie tam, gdzie pokażecie palcem.',
     'Wybierz, co dalej: Python dla admina? Kubernetes od zera? Przygotowanie do konkretnego certyfikatu? Napisz na kanale Chmuroholik, czego potrzebujesz, a kolejny kurs pójdzie tam, gdzie pokażecie palcem.'),
    ('To będzie najlepszy komentarz pod tym filmem.', 'To będzie najlepsza wiadomość, jaką mogę dostać.'),
]


def popraw(t):
    t = re.sub(r'\b(\w+) (odcinek|odcinka|odcinku|odcinkiem)\b', przymiotnik, t)
    for a, b in KONCOWKI:
        t = t.replace(a, b)
    for a, b in ZAMIANY:
        t = re.sub(a, b, t)
    t = re.sub(r'Rozwiązanie (?:zadania )?(?:znajdziesz |będzie |pokażę )?(?:na początku|w) następnej lekcji\.?', 'Rozwiązanie znajdziesz pod spodem.', t)
    t = re.sub(r'\s*\[pauza\]\s*', ' ', t)
    return t


def inline(el):
    """Zawartość akapitu → HTML (tekst, pogrubienia, kod, data)."""
    out = []
    for c in el:
        if c.tag == 'text':
            out.append(text_html(c))
        elif c.tag == 'date':
            out.append(html.escape(c.get('value', '')))
        elif c.tag == 'mention':
            out.append(html.escape(c.get('name', '')))
        else:
            out.append(text_html(c))
    return ''.join(out)


def text_html(t):
    parts = []
    if t.text:
        parts.append(html.escape(popraw(t.text)))
    for c in t:
        inner = html.escape(c.text or '') if c.tag == 'code' else text_html(c) if len(c) else html.escape(popraw(c.text or ''))
        if c.tag == 'bold':
            parts.append(f'<strong>{inner}</strong>')
        elif c.tag == 'code':
            parts.append(f'<code>{inner}</code>')
        else:
            parts.append(inner)
        if c.tail:
            parts.append(html.escape(popraw(c.tail)))
    return ''.join(parts)


def plain(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()


def zetnij_nawiasy(h):
    """Usuwa [didaskalia] z HTML akapitu; zwraca (html, czy_coś_zostało)."""
    h2 = re.sub(r'\[(?:pauza|cięcie|cisza|przerwa)[^\]]*\]', '', h)
    return h2


# ---------- bloki ----------
def blok(el):
    """Jeden blok XML → (rodzaj, html). rodzaj: h1/h2/h3/p/kod/lista/tabela/pomin."""
    if el.tag == 'paragraph':
        lvl = el.get('heading')
        h = inline(el).strip()
        txt = plain(el)
        if lvl:
            return ('h' + lvl, h, txt)
        if not txt:
            return ('pomin', '', '')
        m = re.fullmatch(r'\*?\*?\[(.*)\]\*?\*?\.?', txt, re.S)
        if m:
            wnetrze = m.group(1).strip()
            low = wnetrze.lower()
            if low.startswith('b-roll'):
                return ('broll', '', '')
            if low.startswith('dla zaawansowanych'):
                body = re.sub(r'^\s*\[?\s*dla zaawansowanych\s*:\s*', '', h, flags=re.I)
                body = re.sub(r'\]\s*$', '', body)
                return ('dociekliwi', body, txt)
            if '<code>' in h:
                body = re.sub(r'^\s*\[\s*', '', h)
                body = re.sub(r'\]\s*$', '', body)
                body = re.sub(r'^(na ekranie|plansza|w terminalu)[^:]*:\s*', '', body, flags=re.I)
                kody = re.findall(r'<code>(.*?)</code>', body)
                # sama komenda → blok kodu, a z opisem → notka
                if len(kody) == 1 and re.sub(r'<code>.*?</code>', '', body).strip(' .,;') == '':
                    return ('kod', kody[0], txt)
                return ('notka', body, txt)
            if low.startswith('plansza'):
                body = re.sub(r'^\s*\[\s*plansza\s*:?\s*', '', h, flags=re.I)
                return ('plansza', re.sub(r'\]\s*$', '', body), txt)
            return ('pomin', '', '')
        h = zetnij_nawiasy(h)
        if re.match(r'^\s*\[na ekranie', h):
            h = re.sub(r'^\s*\[na ekranie[^\]]*\]\s*', '', h)
        if not re.sub(r'<[^>]+>', '', h).strip():
            return ('pomin', '', '')
        if re.match(r'^plansza\s*:', txt, re.I):
            return ('plansza', re.sub(r'^\s*plansza\s*:\s*', '', h, flags=re.I), txt)
        return ('p', h, txt)
    if el.tag == 'codeBlock':
        kod = ''.join(el.itertext())
        return ('kod', html.escape(kod), kod)
    if el.tag == 'list':
        tag = 'ol' if el.get('kind') == 'ordered' else 'ul'
        items, plansze = [], []
        for li in el:
            if li.tag != 'listItem':
                continue
            sub = []
            for c in li:
                r = blok(c)
                if r[0] in ('p', 'plansza', 'notka'):
                    sub.append(r)
                elif r[0] == 'kod':
                    sub.append(('kod', r[1], r[2]))
                elif r[0] == 'lista':
                    sub.append(r)
            if sub and all(s[0] == 'plansza' for s in sub):
                plansze.extend(s[1] for s in sub)
                continue
            items.append(''.join(
                (f'<pre><code>{s[1]}</code></pre>' if s[0] == 'kod' else s[1] if s[0] == 'lista' else s[1]) for s in sub))
        out = ''
        if items:
            out += f'<{tag}>' + ''.join(f'<li>{i}</li>' for i in items) + f'</{tag}>'
        if plansze:
            out += '<aside class="ramka zapamietaj"><div class="ramka-tytul">Do zapamiętania</div><ul>' + ''.join(
                f'<li>{re.sub(r"^„(.*)”$", r"\\1", p.strip())}</li>' for p in plansze) + '</ul></aside>'
        return ('lista', out, plain(el))
    if el.tag == 'table':
        rows = []
        for r in el:
            if r.tag != 'row':
                continue
            cells = []
            for c in r:
                tagc = 'th' if c.get('header') == 'true' else 'td'
                inner = ' '.join(blok(x)[1] for x in c if blok(x)[0] in ('p', 'kod', 'lista'))
                cells.append(f'<{tagc}>{inner}</{tagc}>')
            rows.append('<tr>' + ''.join(cells) + '</tr>')
        return ('tabela', '<div class="tabela"><table>' + ''.join(rows) + '</table></div>', plain(el))
    return ('pomin', '', '')


# ---------- składanie lekcji ----------
SEKCJE_NAZWY = {
    'hak': 'Wstęp',
    'zapowiedź': 'Co dalej',
}


def nazwa_sekcji(t):
    low = t.lower()
    if low == 'hak':
        return 'Wstęp'
    if low.startswith('zapowiedź'):
        return 'Co dalej'
    if low.startswith('zadanie dla widza') or low.startswith('zadanie dla widzów'):
        return 'Zadanie'
    return popraw(t)


def parsuj_modul(zakladka):
    bloki = wczytaj(zakladka)
    modul = {'tytul': '', 'opis': [], 'lekcje': []}
    lekcja = None
    sekcja = None
    w_broll = False
    for el in bloki:
        r = blok(el)
        rodz = r[0]
        if rodz == 'h1':
            modul['tytul'] = r[2]
            continue
        if rodz == 'h2':
            w_broll = False
            m = re.match(r'Odcinek\s+(\d+)\s*[—–-]\s*(.*)', r[2])
            if m:
                lekcja = {'nr': int(m.group(1)), 'tytul': m.group(2).strip(), 'cel': '', 'sekcje': []}
                modul['lekcje'].append(lekcja)
                sekcja = None
            else:
                # nagłówek h2 bez numeru: część opisu modułu albo dodatek
                if lekcja is None:
                    modul['opis'].append(f'<h2>{r[1]}</h2>')
                else:
                    sekcja = {'tytul': popraw(r[2]), 'html': []}
                    lekcja['sekcje'].append(sekcja)
            continue
        if rodz == 'broll':
            w_broll = True
            continue
        if w_broll:
            if rodz in ('h3',):
                w_broll = False
            else:
                continue
        if rodz == 'h3':
            if lekcja is None:
                modul['opis'].append(f'<h3>{r[1]}</h3>')
                continue
            sekcja = {'tytul': nazwa_sekcji(r[2]), 'html': [], 'oryg': r[2]}
            lekcja['sekcje'].append(sekcja)
            continue
        if rodz == 'h4':
            if sekcja is not None:
                sekcja['html'].append(f'<h4>{r[1]}</h4>')
            continue
        if rodz == 'pomin':
            continue
        # zwykła treść
        frag = render(r)
        if lekcja is None:
            modul['opis'].append(frag)
        elif sekcja is None:
            if r[0] == 'p' and r[2].startswith('Cel:'):
                lekcja['cel'] = re.sub(r'^\s*<strong>Cel:</strong>\s*', '', r[1])
            else:
                lekcja.setdefault('przed', []).append(frag)
        else:
            sekcja['html'].append(frag)
    return modul


def render(r):
    rodz, h = r[0], r[1]
    if rodz == 'p':
        return f'<p>{h}</p>'
    if rodz == 'kod':
        return f'<div class="kod"><pre><code>{h}</code></pre></div>'
    if rodz == 'notka':
        return f'<p class="ekran">{h}</p>'
    if rodz == 'plansza':
        h = re.sub(r'^„(.*)”\.?$', r'\1', h.strip())
        return f'<aside class="ramka zapamietaj"><div class="ramka-tytul">Do zapamiętania</div><p>{h}</p></aside>'
    if rodz == 'dociekliwi':
        return f'<aside class="ramka dociekliwi"><div class="ramka-tytul">Dla dociekliwych</div><p>{h}</p></aside>'
    return h


# ---------- przeniesienie rozwiązań do zadań ----------
def przenies_rozwiazania(lekcje):
    for i, l in enumerate(lekcje):
        zostaw = []
        for s in l['sekcje']:
            if s['tytul'].lower().startswith('rozwiązanie') and i > 0:
                lekcje[i - 1]['rozwiazanie'] = s['html']
            else:
                zostaw.append(s)
        l['sekcje'] = zostaw


# ---------- czas czytania ----------
def minuty(lekcja):
    tekst = ' '.join(re.sub(r'<[^>]+>', ' ', ''.join(s['html'])) for s in lekcja['sekcje'])
    return max(3, round(len(tekst.split()) / 180))


def slug(n):
    return f'lekcja-{n:03d}.html'


# ---------- plan kursu ----------
def parsuj_plan():
    bloki = wczytaj('00-plan')
    plan = {'wstep': [], 'moduly': {}, 'analogie': '', 'reszta': []}
    tryb, akt = 'wstep', None
    for el in bloki:
        r = blok(el)
        if r[0] == 'h1':
            continue
        if r[0] == 'h2':
            t = r[2]
            tryb = 'plan' if t.startswith('Plan całej') else 'analogie' if t.startswith('Analogie') else 'stop' if t.startswith('Scenariusze') else 'wstep'
            if tryb == 'wstep':
                plan['wstep'].append(f'<h2>{r[1]}</h2>')
            continue
        if r[0] == 'h3' and tryb == 'plan':
            m = re.match(r'Moduł\s+(\d+)\s*[—–-]\s*(.*)', r[2])
            if m:
                akt = int(m.group(1))
                po = re.search(r'\(po nim:\s*(.*?)\)', m.group(2))
                plan['moduly'][akt] = {'tytul': re.sub(r'\s*\(po nim:.*?\)', '', m.group(2)).strip(), 'po': po.group(1) if po else '', 'tabela': [], 'opis': []}
            continue
        if tryb == 'stop' or r[0] == 'pomin':
            continue
        if tryb == 'plan' and akt is not None:
            if el.tag == 'table':
                for row in el:
                    cells = [plain(c) for c in row if c.tag == 'cell']
                    if len(cells) >= 3 and cells[0].isdigit():
                        plan['moduly'][akt]['tabela'].append((int(cells[0]), cells[1], cells[2]))
            else:
                plan['moduly'][akt]['opis'].append(render(r))
            continue
        if tryb == 'analogie':
            plan['analogie'] += render(r)
            continue
        if tryb == 'wstep':
            plan['wstep'].append(render(r))
    return plan


# ---------- szablony ----------
NAZWY_TAB = ['m%02d' % i for i in range(14)]
IKONY = ['chmura', 'komputer', 'zebatka', 'ksiazka', 'tabela', 'tarcza', 'dysk', 'paczka', 'globus', 'klodka', 'serwer', 'robot', 'krawat', 'puchar']


ADRES = 'https://chmuroholik.com'


def strona(tytul, opis, tresc, kanon, glebokosc='', plik=''):
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(tytul)}</title>
<meta name="description" content="{html.escape(opis)}">
<meta property="og:title" content="{html.escape(tytul)}">
<meta property="og:description" content="{html.escape(opis)}">
<link rel="canonical" href="{ADRES}/kurs/{plik}">
<meta property="og:url" content="{ADRES}/kurs/{plik}">
<meta property="og:type" content="article">
<meta property="og:image" content="{ADRES}/img/og.png">
<link rel="icon" type="image/png" href="../img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;500;600;700&family=Silkscreen:wght@400;700&family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="kurs.css">
</head>
<body data-strona="{kanon}">
<a class="pomin" href="#tresc">Przejdź do treści</a>
<nav class="menu" aria-label="Menu">
  <a class="logo" href="../index.html" aria-label="Chmuroholik — strona główna"><img src="../img/favicon.png" alt="" width="30" height="30"></a>
  <div class="linki" id="linki">
    <a href="../index.html">Kanał</a>
    <a href="index.html"{' class="aktywny"' if kanon == 'kurs' else ''}>Kurs</a>
    <a href="index.html#moduly">Moduły</a>
    <a href="index.html#analogie">Analogie</a>
  </div>
  <button class="dzwiek" id="przel-muzyka" type="button" aria-pressed="false" title="Muzyka">♪</button>
  <button class="dzwiek" id="przel-sfx" type="button" aria-pressed="true" title="Efekty dźwiękowe">SFX</button>
  <span class="poziom" id="poziom" title="Twój poziom">LVL 1</span>
  <span class="postep-menu" id="postep-menu" title="Ukończone lekcje">0/0</span>
  <button class="burger" aria-expanded="false" aria-controls="linki">Menu</button>
</nav>
<div class="pasek-czytania" aria-hidden="true"><i id="pasek-czytania"></i></div>
{tresc}
<footer><div class="kontener">© Chmuroholik · kurs „Linux i Bash od zera do admina” · <a href="../index.html">wróć na stronę kanału</a></div></footer>
<script src="kurs.js"></script>
<script src="kurs-media.js"></script>
</body>
</html>
'''


def sekcja_html(s):
    t = s['tytul']
    body = ''.join(s['html'])
    low = t.lower()
    if low.startswith('typowy błąd') or low.startswith('typowe błędy'):
        return f'<section class="ramka blad"><h2><span class="ikona-r">⚠</span> {html.escape(t)}</h2>{body}</section>'
    if low == 'zadanie':
        return None  # renderowane osobno
    return f'<section><h2 id="{kotwica(t)}">{html.escape(t)}</h2>{body}</section>'


def kotwica(t):
    t = t.lower()
    t = re.sub(r'[ąćęłńóśźż]', lambda m: 'acelnoszz'['ąćęłńóśźż'.index(m.group(0))], t)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:50]


def lekcja_html(l, mod_nr, mod, wszystkie, idx):
    poprz = wszystkie[idx - 1] if idx > 0 else None
    nast = wszystkie[idx + 1] if idx + 1 < len(wszystkie) else None
    spis, czesci, zadanie, co_dalej = [], [], None, None
    for s in l['sekcje']:
        if s['tytul'].lower() == 'zadanie':
            zadanie = s
            continue
        if s['tytul'] == 'Co dalej':
            co_dalej = s
            continue
        h = sekcja_html(s)
        if h:
            czesci.append(h)
            if not s['tytul'].lower().startswith('typowy'):
                spis.append(f'<li><a href="#{kotwica(s["tytul"])}">{html.escape(s["tytul"])}</a></li>')
    przed = ''.join(l.get('przed', []))
    zad = ''
    if zadanie:
        roz = ''.join(l.get('rozwiazanie') or [])
        roz_html = f'<details class="rozwiazanie"><summary>Pokaż rozwiązanie</summary><div>{roz}</div></details>' if roz else ''
        zad = f'<section class="ramka zadanie" id="zadanie"><h2><span class="ikona-r">✎</span> Zadanie</h2>{"".join(zadanie["html"])}{roz_html}</section>'
        spis.append('<li><a href="#zadanie">Zadanie</a></li>')
    if co_dalej:
        zad += f'<section class="co-dalej"><h2 id="co-dalej">Co dalej</h2>{"".join(co_dalej["html"])}</section>'
        spis.append('<li><a href="#co-dalej">Co dalej</a></li>')
    boczne = ''.join(
        f'<li><a href="{slug(x["nr"])}" data-lekcja="{x["nr"]}"{" aria-current=\"page\" class=\"biezaca\"" if x["nr"] == l["nr"] else ""}><span class="znacznik"></span><span class="nr">{x["nr"]}</span> {html.escape(x["tytul"])}</a></li>'
        for x in mod['lekcje'])
    nav = '<nav class="nawigacja" aria-label="Poprzednia i następna lekcja">'
    nav += f'<a class="btn" href="{slug(poprz["l"]["nr"])}" rel="prev">← {poprz["l"]["nr"]}. {html.escape(poprz["l"]["tytul"])}</a>' if poprz else '<span></span>'
    nav += f'<a class="btn domyslny zolty" href="{slug(nast["l"]["nr"])}" rel="next">{nast["l"]["nr"]}. {html.escape(nast["l"]["tytul"])} →</a>' if nast else '<a class="btn domyslny zolty" href="index.html">Koniec kursu! Wróć do spisu →</a>'
    nav += '</nav>'
    cel = f'<p class="cel"><strong>Po tej lekcji:</strong> {l["cel"]}</p>' if l['cel'] else ''
    tresc = f'''
<div class="uklad-lekcji">
  <aside class="boczny" aria-label="Lekcje modułu">
    <div class="okno">
      <div class="belka"><span>Moduł {mod_nr}</span></div>
      <div class="boczny-tytul"><a href="index.html#m{mod_nr:02d}">{html.escape(krotki(mod['tytul']))}</a></div>
      <ol class="lista-lekcji">{boczne}</ol>
    </div>
  </aside>
  <main id="tresc" class="okno duze lekcja" data-nr="{l['nr']}" data-modul="{mod_nr}" data-tematy="{html.escape(l.get('tematy', ''))}">
    <div class="belka"><span>Lekcja {l['nr']} z {len(wszystkie)}</span></div>
    <article class="tresc-lekcji">
      <p class="okruszki"><a href="index.html">Kurs</a> › <a href="index.html#m{mod_nr:02d}">Moduł {mod_nr}</a> › Lekcja {l['nr']}</p>
      <div class="plansza" id="plansza" aria-hidden="true"></div>
      <h1>{html.escape(l['tytul'])}</h1>
      <p class="meta"><span>⏱ ok. {l['min']} min czytania</span><span>· moduł {mod_nr}: {html.escape(krotki(mod['tytul']))}</span></p>
      {cel}
      {f'<nav class="spis" aria-label="W tej lekcji"><strong>W tej lekcji</strong><ol>{"".join(spis)}</ol></nav>' if len(spis) > 2 else ''}
      {przed}
      {''.join(czesci)}
      {zad}
      <label class="ukonczone"><input type="checkbox" id="ukonczone"> <span>Lekcja ukończona</span></label>
      {nav}
    </article>
  </main>
</div>'''
    opis = f'Lekcja {l["nr"]} kursu Linux i Bash od zera do admina: {plain_txt(l["tytul"])}. {plain_txt(l["cel"])}'
    return strona(f'{l["nr"]}. {l["tytul"]} — kurs Linux i Bash | Chmuroholik', opis[:300], tresc, 'lekcja', plik=slug(l['nr']))


def krotki(t):
    return t.split('—', 1)[-1].strip()


def plain_txt(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h or '')).strip()


def indeks_html(plan, moduly, wszystkie):
    karty = []
    for nr, mod in moduly:
        p = plan['moduly'].get(nr, {})
        lekcje = ''.join(
            f'<li><a href="{slug(l["nr"])}" data-lekcja="{l["nr"]}"><span class="znacznik"></span><span class="nr">{l["nr"]}</span><span class="t">{html.escape(l["tytul"])}</span><span class="tematy">{html.escape(tematy(p, l["nr"]))}</span></a></li>'
            for l in mod['lekcje'])
        minut = sum(l['min'] for l in mod['lekcje'])
        karty.append(f'''
<section class="okno modul pojaw" id="m{nr:02d}" data-modul="{nr}">
  <div class="belka"><span>Moduł {nr}</span></div>
  <div class="modul-glowa">
    <div class="modul-ikona" data-sprite="{IKONY[nr]}"></div>
    <div>
      <h3>{html.escape(mod['tytul'].split('—', 1)[-1].strip())}</h3>
      {f'<p class="po-nim">Po nim: {html.escape(p.get("po", ""))}</p>' if p.get('po') else ''}
      <p class="meta">{len(mod['lekcje'])} lekcji · ok. {max(1, round(minut / 60 * 2) / 2):g} h czytania</p>
    </div>
    <div class="pasek-modulu" aria-hidden="true"><i></i></div>
  </div>
  <details class="lekcje-modulu"{' open' if nr == 0 else ''}><summary>Lekcje</summary><ol class="lista-lekcji duza">{lekcje}</ol></details>
</section>''')
    wstep = ''.join(plan['wstep'])
    razem = sum(l['min'] for _, m in moduly for l in m['lekcje'])
    tresc = f'''
<main id="tresc">
<header class="pulpit-kursu">
  <div class="okno duze hero-kursu">
    <div class="belka"><span>Kurs.app</span></div>
    <div class="tresc hero-tresc">
      <div class="hero-ikona" data-sprite="terminal"></div>
      <div>
        <p class="nadtytul">Darmowy kurs od Chmuroholika</p>
        <h1>Linux i Bash<br>od zera do admina</h1>
        <p class="lead">Od pierwszego otwarcia terminala do samodzielnej pracy administratora serwerów. Bez znajomości programowania na starcie.</p>
        <div class="liczby">
          <div><b>{len(wszystkie)}</b><small>lekcji</small></div>
          <div><b>{len(moduly)}</b><small>modułów</small></div>
          <div><b>~{round(razem / 60)} h</b><small>czytania</small></div>
          <div><b id="procent">0%</b><small>Twój postęp</small></div>
        </div>
        <div class="akcje">
          <a class="btn domyslny zolty" id="kontynuuj" href="{slug(wszystkie[0]['l']['nr'])}">▶ Zacznij od lekcji 1</a>
          <a class="btn" href="#moduly">Zobacz program</a>
        </div>
      </div>
    </div>
  </div>
</header>
<section class="kontener">
  <div class="okno pojaw">
    <div class="belka"><span>Czytaj mnie.txt</span></div>
    <div class="tresc proza">{wstep}</div>
  </div>
</section>
<section class="kontener" id="moduly">
  <div class="naglowek"><h2>PROGRAM KURSU</h2>
    <label class="szukaj"><span class="sr">Szukaj lekcji</span><input type="search" id="szukaj" placeholder="Szukaj: grep, ssh, cron…"></label>
  </div>
  <p class="brak" id="brak" hidden>Nic nie znalazłem. Spróbuj innej komendy.</p>
  <div class="moduly">{''.join(karty)}</div>
</section>
<section class="kontener" id="odznaki-sekcja">
  <div class="naglowek"><h2>ODZNAKI</h2><span class="etykieta" id="poziom-opis">zbieraj XP i odznaki za ukończone lekcje</span></div>
  <div class="okno"><div class="belka"><span>Gablota.app</span></div><div class="tresc"><div class="xp-pasek"><span id="xp-tekst">0 XP</span><div class="xp"><i id="xp-i"></i></div><span id="xp-nast"></span></div><div class="odznaki" id="odznaki"></div></div></div>
</section>
<section class="kontener" id="analogie">
  <div class="naglowek"><h2>ANALOGIE</h2><span class="etykieta">jedno pojęcie, jedno porównanie</span></div>
  <div class="okno pojaw"><div class="belka"><span>Słowniczek obrazkowy</span></div><div class="tresc proza">{plan['analogie']}</div></div>
</section>
</main>'''
    return strona('Kurs Linux i Bash od zera do admina | Chmuroholik', f'Darmowy kurs po polsku: {len(wszystkie)} lekcji od pierwszego otwarcia terminala do pracy administratora serwerów Linux. Bash, skrypty, sieć, bezpieczeństwo, Ansible i przygotowanie do rozmowy.', tresc, 'kurs', plik='')


def tematy(p, nr):
    for n, _, t in p.get('tabela', []):
        if n == nr:
            return t
    return ''


# ---------- główna część ----------
if __name__ == '__main__':
    plan = parsuj_plan()
    moduly = []
    for i, tab in enumerate(NAZWY_TAB):
        m = parsuj_modul(tab)
        moduly.append((i, m))
    wszystkie = [{'l': l, 'm': i} for i, m in moduly for l in m['lekcje']]
    przenies_rozwiazania([w['l'] for w in wszystkie])
    for w in wszystkie:
        w['l']['min'] = minuty(w['l'])
        w['l']['tematy'] = tematy(plan['moduly'].get(w['m'], {}), w['l']['nr'])
    for idx, w in enumerate(wszystkie):
        i = w['m']
        open(os.path.join(WYJ, slug(w['l']['nr'])), 'w', encoding='utf-8').write(lekcja_html(w['l'], i, moduly[i][1], wszystkie, idx))
    open(os.path.join(WYJ, 'index.html'), 'w', encoding='utf-8').write(indeks_html(plan, moduly, wszystkie))
    # indeks do wyszukiwarki i postępu
    idx = [{'n': w['l']['nr'], 'm': w['m'], 't': w['l']['tytul'], 'k': tematy(plan['moduly'].get(w['m'], {}), w['l']['nr'])} for w in wszystkie]
    open(os.path.join(WYJ, 'lekcje.json'), 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False))
    # raport
    print('lekcji:', len(wszystkie), 'modułów:', len(moduly))
    for i, m in moduly:
        print(f'  m{i:02d}', m['tytul'], '→', [l['nr'] for l in m['lekcje']][:1], '…', [l['nr'] for l in m['lekcje']][-1:], len(m['lekcje']))
    bez_zad = [w['l']['nr'] for w in wszystkie if not any(s['tytul'] == 'Zadanie' for s in w['l']['sekcje'])]
    bez_roz = [w['l']['nr'] for w in wszystkie if any(s['tytul'] == 'Zadanie' for s in w['l']['sekcje']) and not w['l'].get('rozwiazanie')]
    print('bez zadania:', bez_zad)
    print('zadanie bez rozwiązania:', bez_roz)
    # mapa strony dla Google (sitemap.xml + robots.txt)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapa_strony.py')])
