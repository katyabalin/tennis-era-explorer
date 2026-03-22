# 🎾 Tennis Era Explorer

**Live app → https://tennis-era-explorer.streamlit.app**

I play Division 1 college tennis, so the sport is pretty much always on my mind. At some point I started wondering whether the best players today are actually different from the best players a decade ago — not just different names, but a different kind of player. Younger? Taller? Built around a different game?

I had the question, so I built something to answer it.

## What It Does

Pick any two years between 2010 and 2024 and the app shows you:

- The top 10 ATP or WTA players for each year side by side
- Average age, height, and ranking points with year-over-year deltas
- Charts comparing how each metric shifted
- An AI-generated analysis powered by Claude that puts the numbers in context — referencing actual players and explaining what the data means for the sport

## What I Found

The ATP and WTA tell very different stories across the same time period — I'll let the data speak for itself. Try it and see what you find.

## Stack

- Python, Streamlit, pandas, matplotlib
- Claude API (Anthropic) for AI-generated analysis
- Data from Jeff Sackmann's open-source [tennis_atp](https://github.com/JeffSackmann/tennis_atp) and [tennis_wta](https://github.com/JeffSackmann/tennis_wta) datasets

## What I'd Add Next

- Player search — look up any individual player's career arc over time
- Surface breakdown — do top player profiles differ on clay vs hard court?
- Shareable links so you can send a specific year comparison to someone
- Deploy with more historical data going back to the 1990s

## Run It Locally

If you want to run it yourself:

```bash
git clone https://github.com/katyabalin/tennis-era-explorer.git
cd tennis-era-explorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Download the ATP and WTA data files from [Jeff Sackmann's repos](https://github.com/JeffSackmann) into a `data/` folder, then:

```bash
streamlit run app.py
```