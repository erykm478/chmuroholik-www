#!/usr/bin/env python3
"""Tworzy sitemap.xml i robots.txt dla chmuroholik.com.

Mapa zawiera stronę główną, spis kursu i wszystkie lekcje (z kurs/lekcje.json).
Uruchamiaj po każdym przegenerowaniu kursu: python3 narzedzia/mapa_strony.py
(generuj_kurs.py robi to sam na końcu).
"""
import json, os, subprocess
from datetime import date

ADRES = 'https://chmuroholik.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def zmiana(sciezka):
    """Data ostatniej zmiany pliku z gita (a jak go nie ma w gicie — dzisiejsza)."""
    try:
        d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', sciezka], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    except Exception:
        d = ''
    return d or date.today().isoformat()


def main():
    adresy = [('', 'index.html', '1.0'), ('kurs/', 'kurs/index.html', '0.9')]
    lekcje = json.load(open(os.path.join(ROOT, 'kurs', 'lekcje.json'), encoding='utf-8'))
    for l in lekcje:
        plik = f'kurs/lekcja-{int(l["n"]):03d}.html'
        adresy.append((plik, plik, '0.7'))
    wiersze = [f'  <url><loc>{ADRES}/{u}</loc><lastmod>{zmiana(p)}</lastmod><priority>{pr}</priority></url>'
               for u, p, pr in adresy]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(wiersze) + '\n</urlset>\n')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(
        f'User-agent: *\nAllow: /\nDisallow: /narzedzia/\n\nSitemap: {ADRES}/sitemap.xml\n')
    print(f'sitemap.xml: {len(adresy)} adresów')


if __name__ == '__main__':
    main()
