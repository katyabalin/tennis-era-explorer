# 🎾 Tennis Era Explorer

I play Division 1 college tennis, so the sport is pretty much always on my mind. At some point I started wondering whether the best players today are actually different from the best players a decade ago — not just different names, but a different kind of player. Younger? Taller? Built around a different game?

I had the question, so I built something to answer it.

## What It Does

Pick any two years between 2010 and 2024 and the app shows you:

- The top 10 ATP players for each year side by side
- Average age, height, and ranking points with year-over-year deltas
- Charts comparing how each metric shifted
- An AI-generated analysis (powered by Claude) that puts the numbers in context — referencing actual players and explaining what the shift means for the sport

## What I Found

The 2024 top 10 is about 2-3 years younger and nearly 2 inches taller on average than the 2015 top 10. That's not random — it reflects a real structural shift in how the game is played at the elite level. The serve has become more decisive, and the new generation of players like Sinner and Alcaraz broke through earlier than anyone from the previous era.

## Stack

- Python, Streamlit, pandas, matplotlib
- Claude API for AI-generated analysis
- Data from Jeff Sackmann's open-source [tennis_atp](https://github.com/JeffSackmann/tennis_atp) dataset

## Running It Locally

```bash
git clone https://github.com/katyabalin/tennis-era-explorer.git
cd tennis-era-explorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your-key-here
```

Download these files from [Jeff Sackmann's repo](https://github.com/JeffSackmann/tennis_atp) and put them in a `data/` folder:
- `atp_players.csv`
- `atp_rankings_10s.csv`
- `atp_rankings_20s.csv`
- `atp_rankings_current.csv`

Then:
```bash
streamlit run app.py
```

## What I'd Add Next

- WTA data so I can compare the women's tour across the same eras
- A player search feature to track individual career arcs over time
- Surface breakdown — do top player profiles differ on clay vs hard court?
- Deploy it so anyone can use it without running it locally