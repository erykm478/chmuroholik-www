#!/usr/bin/env python3
"""Pobiera listę filmów z kanału YouTube Chmuroholik do dane/filmy.json.

Strona czyta ten plik, więc nowe odcinki i shorty pojawiają się na niej same,
bez edytowania HTML. Uruchamiaj co jakiś czas (np. co godzinę z GitHub Actions
albo z crona na serwerze): python3 narzedzia/aktualizuj_filmy.py

Źródła (bez klucza API):
- oficjalny kanał RSS YouTube (15 najnowszych filmów, z datą i wyświetleniami),
- strony kanału /videos i /shorts (pełniejsza lista),
- strona filmu, tylko dla filmów, których jeszcze nie znamy (data, opis, długość).
Filmy raz zapisane zostają w pliku, nawet jeśli wypadną z RSS.
"""
import json, os, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

KANAL = 'UC_JbBSEP0ljATQ0DWmCxADw'
UCHWYT = '@chmuroholik'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLIK = os.path.join(ROOT, 'dane', 'filmy.json')
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',
      'Accept-Language': 'pl-PL,pl;q=0.9'}
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}


def pobierz(url, prob=4):
    """YouTube czasem chwilowo zwraca 404/429/5xx (zwłaszcza dla serwerów GitHuba), więc ponawiamy."""
    ostatni = None
    for i in range(prob):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            ostatni = e
            time.sleep(5 * (i + 1))
    raise ostatni


def initial_data(html):
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', html)
    return json.loads(m.group(1)) if m else {}


def chodz(o, f):
    if isinstance(o, dict):
        f(o)
        for v in o.values():
            chodz(v, f)
    elif isinstance(o, list):
        for v in o:
            chodz(v, f)


def liczba(t):
    """„1,2 tys. wyświetleń” → 1200, „722 wyświetlenia” → 722."""
    if not t:
        return None
    t = t.replace('\xa0', ' ').lower()
    m = re.search(r'([\d.,]+)\s*(tys|mln)?', t)
    if not m:
        return None
    n = float(m.group(1).replace(',', '.').replace(' ', ''))
    return int(n * (1000 if m.group(2) == 'tys' else 1_000_000 if m.group(2) == 'mln' else 1))


def czysty_tytul(t):
    t = re.sub(r'\s+#\S+', '', t).strip()
    return t


def z_rss(filmy):
    xml = pobierz(f'https://www.youtube.com/feeds/videos.xml?channel_id={KANAL}')
    root = ET.fromstring(xml)
    for e in root.findall('a:entry', NS):
        vid = e.find('yt:videoId', NS).text
        link = e.find('a:link', NS).get('href')
        st = e.find('media:group/media:community/media:statistics', NS)
        f = filmy.setdefault(vid, {'id': vid})
        f['tytul'] = e.find('a:title', NS).text
        f['typ'] = 'short' if '/shorts/' in link else 'film'
        f['data'] = e.find('a:published', NS).text
        f['opis'] = (e.find('media:group/media:description', NS).text or '')
        if st is not None and st.get('views'):
            f['wyswietlenia'] = int(st.get('views'))


def z_kanalu(filmy):
    for zakladka in ('videos', 'shorts'):
        try:
            d = initial_data(pobierz(f'https://www.youtube.com/{UCHWYT}/{zakladka}'))
        except Exception as e:
            print('pomijam', zakladka, e, file=sys.stderr)
            continue

        def f(o):
            if 'lockupViewModel' in o:
                v = o['lockupViewModel']
                vid = v.get('contentId')
                md = v.get('metadata', {}).get('lockupMetadataViewModel', {})
                if vid and len(vid) == 11:
                    x = filmy.setdefault(vid, {'id': vid})
                    x.setdefault('tytul', md.get('title', {}).get('content'))
                    x['typ'] = 'film'
            if 'videoRenderer' in o:
                v = o['videoRenderer']
                x = filmy.setdefault(v['videoId'], {'id': v['videoId']})
                x.setdefault('tytul', ''.join(r['text'] for r in v['title']['runs']))
                x['typ'] = 'film'
            if 'shortsLockupViewModel' in o:
                v = o['shortsLockupViewModel']
                vid = v.get('onTap', {}).get('innertubeCommand', {}).get('reelWatchEndpoint', {}).get('videoId')
                if vid:
                    x = filmy.setdefault(vid, {'id': vid})
                    x.setdefault('tytul', v.get('overlayMetadata', {}).get('primaryText', {}).get('content'))
                    x['typ'] = 'short'
                    w = liczba(v.get('overlayMetadata', {}).get('secondaryText', {}).get('content'))
                    if w is not None:
                        x['wyswietlenia'] = w
        chodz(d, f)


def uzupelnij(f):
    """Strona filmu: data publikacji, opis, długość, wyświetlenia."""
    try:
        h = pobierz(f'https://www.youtube.com/watch?v={f["id"]}')
    except Exception as e:
        print('nie pobrałem', f['id'], e, file=sys.stderr)
        return
    m = re.search(r'var ytInitialPlayerResponse = (\{.*?\});(?:var|</script>)', h)
    if not m:
        return
    p = json.loads(m.group(1))
    vd = p.get('videoDetails', {})
    mf = p.get('microformat', {}).get('playerMicroformatRenderer', {})
    f.setdefault('tytul', vd.get('title'))
    f['opis'] = f.get('opis') or vd.get('shortDescription', '')
    if vd.get('lengthSeconds'):
        f['dlugosc'] = int(vd['lengthSeconds'])
    if vd.get('viewCount') and 'wyswietlenia' not in f:
        f['wyswietlenia'] = int(vd['viewCount'])
    data = mf.get('publishDate') or mf.get('uploadDate')
    if data and not f.get('data'):
        f['data'] = data if 'T' in data else data + 'T12:00:00+00:00'


def main():
    stare = {}
    if os.path.exists(PLIK):
        try:
            stare = {f['id']: f for f in json.load(open(PLIK, encoding='utf-8')).get('filmy', [])}
        except Exception:
            stare = {}
    filmy = {k: dict(v) for k, v in stare.items()}
    ok = 0
    for zrodlo in (z_rss, z_kanalu):
        try:
            zrodlo(filmy); ok += 1
        except Exception as e:
            print(f'uwaga: {zrodlo.__name__} nie zadziałało ({e}), próbuję dalej', file=sys.stderr)
    if not ok or not filmy:
        print('YouTube nie odpowiada, zostawiam listę bez zmian'); return
    for f in filmy.values():
        if not f.get('data') or not f.get('opis') or (f.get('typ') == 'film' and not f.get('dlugosc')):
            uzupelnij(f)
            time.sleep(0.5)
    wynik = []
    for f in filmy.values():
        if not f.get('tytul'):
            continue
        opis = f.get('opis') or ''
        f['tytul_krotki'] = czysty_tytul(f['tytul'])
        # seria o Linuxie: długie odcinki z #linux w opisie albo tytule
        f['seria'] = 'linux' if f.get('typ') == 'film' and (opis + ' ' + f['tytul']).lower().count('linux') >= 2 else None
        f['zajawka'] = re.split(r'\n\s*\n', opis.strip())[0][:280] if opis else ''
        f.pop('opis', None)
        # opis trzymamy tylko jako zajawkę, ale do wykrywania serii potrzebny jest pełny przy następnym razie
        f['_opis'] = opis[:2000]
        wynik.append(f)
    wynik.sort(key=lambda x: x.get('data') or '', reverse=True)
    linux = sorted([f for f in wynik if f['seria'] == 'linux'], key=lambda x: x.get('data') or '')
    for i, f in enumerate(linux, 1):
        f['czesc'] = i
    out = {
        'aktualizacja': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'kanal': {'id': KANAL, 'url': f'https://www.youtube.com/{UCHWYT}', 'tytul': 'Chmuroholik'},
        'filmy': [{k: v for k, v in f.items() if k != '_opis'} | {'opis': f['_opis']} for f in wynik],
    }
    # bez zmian w filmach = nie ruszamy pliku (żeby automat nie robił pustych commitów co godzinę)
    try:
        if json.load(open(PLIK, encoding='utf-8')).get('filmy') == out['filmy']:
            print('bez zmian w filmach'); return
    except Exception:
        pass
    os.makedirs(os.path.dirname(PLIK), exist_ok=True)
    tmp = PLIK + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, PLIK)
    nowe = len(set(filmy) - set(stare))
    print(f'filmy: {sum(1 for f in wynik if f["typ"] == "film")}, shorty: {sum(1 for f in wynik if f["typ"] == "short")}, nowe: {nowe}, seria Linux: {[f["tytul_krotki"] for f in linux]}')


if __name__ == '__main__':
    main()
