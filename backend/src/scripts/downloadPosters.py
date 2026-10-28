import sys
import os
import json
import re
import time
import urllib.parse
import urllib.request

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DEST_DIR = os.path.abspath('frontend/public/posters')
os.makedirs(DEST_DIR, exist_ok=True)

USER_AGENT_API = 'CineGraphApp/1.0 (contact@example.com)'
USER_AGENT_IMG = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Specific Wikipedia page slugs mapping for exact matches
SPECIFIC_SLUGS = {
    'inception-2010': 'Inception',
    'the-dark-knight-2008': 'The_Dark_Knight',
    'interstellar-2014': 'Interstellar_(film)',
    'the-prestige-2006': 'The_Prestige_(film)',
    'memento-2000': 'Memento_(film)',
    'dunkirk-2017': 'Dunkirk_(2017_film)',
    'oppenheimer-2023': 'Oppenheimer_(film)',
    'tenet-2020': 'Tenet_(film)',
    'batman-begins-2005': 'Batman_Begins',
    'the-dark-knight-rises-2012': 'The_Dark_Knight_Rises',
    'arrival-2016': 'Arrival_(film)',
    'blade-runner-2049-2017': 'Blade_Runner_2049',
    'dune-2021': 'Dune_(2021_film)',
    'dune-part-two-2024': 'Dune:_Part_Two',
    'prisoners-2013': 'Prisoners_(2013_film)',
    'sicario-2015': 'Sicario_(2015_film)',
    'blade-runner-1982': 'Blade_Runner',
    'alien-1979': 'Alien_(film)',
    'gladiator-2000': 'Gladiator_(2000_film)',
    'the-martian-2015': 'The_Martian_(film)',
    'aliens-1986': 'Aliens_(film)',
    'terminator-2-1991': 'Terminator_2:_Judgment_Day',
    'titanic-1997': 'Titanic_(1997_film)',
    'avatar-2009': 'Avatar_(2009_film)',
    'jurassic-park-1993': 'Jurassic_Park_(film)',
    'saving-private-ryan-1998': 'Saving_Private_Ryan',
    'catch-me-if-you-can-2002': 'Catch_Me_If_You_Can_(film)',
    'raiders-of-the-lost-ark-1981': 'Raiders_of_the_Lost_Ark',
    'schindlers-list-1993': "Schindler's_List",
    'the-departed-2006': 'The_Departed',
    'shutter-island-2010': 'Shutter_Island_(film)',
    'the-wolf-of-wall-street-2013': 'The_Wolf_of_Wall_Street_(2013_film)',
    'goodfellas-1990': 'Goodfellas',
    'fight-club-1999': 'Fight_Club',
    'se7en-1995': 'Seven_(1995_film)',
    'gone-girl-2014': 'Gone_Girl_(film)',
    'the-social-network-2010': 'The_Social_Network',
    'zodiac-2007': 'Zodiac_(film)',
    'pulp-fiction-1994': 'Pulp_Fiction',
    'django-unchained-2012': 'Django_Unchained',
    'inglourious-basterds-2009': 'Inglourious_Basterds',
    'once-upon-a-time-in-hollywood-2019': 'Once_Upon_a_Time_in_Hollywood',
    'kill-bill-vol-1-2003': 'Kill_Bill:_Volume_1',
    'the-matrix-1999': 'The_Matrix',
    'mad-max-fury-road-2015': 'Mad_Max:_Fury_Road',
    'edge-of-tomorrow-2014': 'Edge_of_Tomorrow',
    'mission-impossible-fallout-2018': 'Mission:_Impossible_–_Fallout',
    'top-gun-maverick-2022': 'Top_Gun:_Maverick',
    'everything-everywhere-all-at-once-2022': 'Everything_Everywhere_All_at_Once',
    '2001-a-space-odyssey-1968': '2001:_A_Space_Odyssey_(film)',
    'back-to-the-future-1985': 'Back_to_the_Future',
    'toy-story-1995': 'Toy_Story',
    'up-2009': 'Up_(2009_film)',
    'inside-out-2015': 'Inside_Out_(2015_film)',
    'wall-e-2008': 'WALL-E',
    'finding-nemo-2003': 'Finding_Nemo',
    'spirited-away-2001': 'Spirited_Away',
    'my-neighbor-totoro-1988': 'My_Neighbor_Totoro',
    'spider-man-into-the-spider-verse-2018': 'Spider-Man:_Into_the_Spider-Verse',
    'lotr-fellowship-of-the-ring-2001': 'The_Lord_of_the_Rings:_The_Fellowship_of_the_Ring',
    'lotr-the-two-towers-2002': 'The_Lord_of_the_Rings:_The_Two_Towers',
    'lotr-return-of-the-king-2003': 'The_Lord_of_the_Rings:_The_Return_of_the_King',
    'la-la-land-2016': 'La_La_Land',
    'whiplash-2014': 'Whiplash_(2014_film)',
    'the-grand-budapest-hotel-2014': 'The_Grand_Budapest_Hotel',
    'forrest-gump-1994': 'Forrest_Gump',
    'cast-away-2000': 'Cast_Away',
    'eternal-sunshine-of-the-spotless-mind-2004': 'Eternal_Sunshine_of_the_Spotless_Mind',
    'her-2013': 'Her_(film)',
    'parasite-2019': 'Parasite_(2019_film)',
    'the-shawshank-redemption-1994': 'The_Shawshank_Redemption',
    'the-green-mile-1999': 'The_Green_Mile_(film)',
    'the-revenant-2015': 'The_Revenant_(2015_film)',
    'joker-2019': 'Joker_(2019_film)',
    'the-godfather-1972': 'The_Godfather',
    'heat-1995': 'Heat_(1995_film)',
    'get-out-2017': 'Get_Out',
    'us-2019': 'Us_(2019_film)',
    'the-shining-1980': 'The_Shining_(film)',
    'a-quiet-place-2018': 'A_Quiet_Place'
}

def fetch_wiki_thumbnail(slug):
    quoted = urllib.parse.quote(slug)
    url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{quoted}'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT_API})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('thumbnail', {}).get('source')
    except Exception as e:
        return None

def download_image(img_url, out_path):
    # Wikimedia thumbnail URLs often end with ?... or have /thumb/.../220px-...
    # Let's request the high-res or original image if possible
    # e.g., if /thumb/a/b/c.jpg/220px-c.jpg -> /a/b/c.jpg
    clean_url = re.sub(r'\?.*$', '', img_url)
    req = urllib.request.Request(clean_url, headers={'User-Agent': USER_AGENT_IMG})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(out_path, 'wb') as f:
                f.write(resp.read())
            return True
    except Exception as e:
        # Fallback to original url
        try:
            req = urllib.request.Request(img_url, headers={'User-Agent': USER_AGENT_IMG})
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(out_path, 'wb') as f:
                    f.write(resp.read())
                return True
        except Exception:
            return False

def main():
    print(f"Checking posters in {DEST_DIR}...")
    success_count = 0
    missing = []

    for movie_id, slug in SPECIFIC_SLUGS.items():
        out_path = os.path.join(DEST_DIR, f"{movie_id}.jpg")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            success_count += 1
            print(f"  ✓ {movie_id} (already cached)")
            continue

        # Try specific slug first
        slugs_to_try = [slug]
        if not slug.endswith('(film)'):
            slugs_to_try.append(f"{slug}_(film)")

        img_url = None
        for s in slugs_to_try:
            img_url = fetch_wiki_thumbnail(s)
            if img_url:
                break
            time.sleep(0.5)

        if img_url:
            ok = download_image(img_url, out_path)
            if ok:
                success_count += 1
                size_kb = os.path.getsize(out_path) // 1024
                print(f"  ✓ {movie_id} downloaded ({size_kb} KB)")
            else:
                missing.append(movie_id)
                print(f"  ✗ {movie_id}: download failed for {img_url}")
        else:
            missing.append(movie_id)
            print(f"  ✗ {movie_id}: no thumbnail found for {slug}")

        time.sleep(0.8) # respect Wikipedia rate limits

    print(f"\nCompleted: {success_count}/80 posters downloaded.")
    if missing:
        print(f"Missing ({len(missing)}): {missing}")

if __name__ == '__main__':
    main()
