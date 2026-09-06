# Applied Linguistics CFP RSS

An automatically updated RSS feed for calls for papers/proposals/abstracts relevant
to applied linguistics.

## Current sources

1. **LINGUIST List — Calls**: the primary CFP source. LINGUIST List explicitly
   provides a dedicated Calls for Papers RSS feed and its Calls postings include
   submission information and links. 
2. **AILA**: the International Association of Applied Linguistics website RSS,
   filtered for applied-linguistics CFP terminology.

## Deploy with GitHub Pages

1. Create a GitHub repository and upload these files.
2. Replace `YOUR-USERNAME/YOUR-REPO` in `generator.py` with your repository URL.
3. Enable **Settings → Pages → Deploy from a branch → `main` / `/docs`**.
4. Run **Actions → Update Applied Linguistics CFP RSS → Run workflow** once.
5. Subscribe your RSS reader to:

   `https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml`

The GitHub Action then rebuilds the feed every day.

## Customization

Edit `KEYWORDS` in `generator.py` to make the feed narrower or broader.
The default catches applied linguistics, language education, TESOL/ELT, CALL,
language assessment/testing, multilingualism, discourse/pragmatics,
corpus/learner-corpus work, translation/interpreting, academic writing,
teacher education, language policy, and related areas.

## Important limitation

This repository creates and updates the RSS file, but it does not itself host a
public URL. GitHub Pages (or another static host) is required for a subscribable
feed URL.
