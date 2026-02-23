import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium", layout_file="layouts/match_viz.grid.json")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import os
    import pymongo
    import pandas as pd
    import numpy as np

    from dotenv import load_dotenv
    from mplsoccer import VerticalPitch, Pitch
    from matplotlib.colors import LinearSegmentedColormap

    return load_dotenv, mo, os, pymongo


@app.cell
def _():
    import module.viz as viz
    import module.query as query
    import constants.theme as theme
    import module.fonts as fonts

    return query, viz


@app.cell
def _(load_dotenv, os, pymongo):
    # 1. Load file .env
    load_dotenv()

    # 2. Ambil variabel dari .env
    mongo_uri = os.getenv("MONGO_URI")

    # 3. Buat koneksi ke MongoDB
    try:
        client = pymongo.MongoClient(mongo_uri)
        # Cek apakah koneksi berhasil
        client.admin.command('ping')

    except Exception as e:
        print(f"Gagal terhubung: {e}")
    return (client,)


@app.cell
def _(client, mo, query):
    available_comp = query.get_comp_manual(client)
    select_competition = mo.ui.dropdown(options=available_comp, value='Indonesia Super League', full_width=True)
    return (select_competition,)


@app.cell
def _(select_competition):
    selected_competition = select_competition.value
    return (selected_competition,)


@app.cell
def _(client, mo, query, selected_competition):
    season_comp_dict = query.get_comp_seasons(client, selected_competition)

    if season_comp_dict:
        select_season = mo.ui.dropdown(options=season_comp_dict, value=list(season_comp_dict.keys())[0], full_width=True)
    else:
        select_season = mo.ui.dropdown(options=[], full_width=True)
    return (select_season,)


@app.cell
def _(select_season):
    selected_season = select_season.value
    return (selected_season,)


@app.cell
def _(client, mo, query, selected_competition, selected_season):
    teams_comp_dict = query.get_teams_comp(client, selected_competition, selected_season)

    if teams_comp_dict:
        select_team = mo.ui.dropdown(options=teams_comp_dict, value=list(teams_comp_dict.keys())[0], full_width=True)
    else:
        select_team = mo.ui.dropdown(options=[], full_width=True)
    return (select_team,)


@app.cell
def _(select_team):
    selected_team = select_team.value
    return (selected_team,)


@app.cell
def _(client, mo, query, selected_competition, selected_season, selected_team):
    matches_team_dict = query.get_matches_by_team(client, selected_competition, selected_season, selected_team)

    if matches_team_dict:
        select_match = mo.ui.dropdown(options=matches_team_dict, value=list(matches_team_dict.keys())[0], full_width=True, searchable=True)
    else:
        select_match = mo.ui.dropdown(options=[], full_width=True)
    return (select_match,)


@app.cell
def _(select_match):
    selected_match = select_match.value
    return (selected_match,)


@app.cell
def _(mo, select_competition, select_match, select_season, select_team):
    menu_kontrol = mo.vstack([
        mo.md("#### Choose Competition:"),
        mo.style(select_competition, {"margin-left": "15px", "width": "230px"}),
        mo.md("#### Choose Season:"),
        mo.style(select_season, {"margin-left": "15px", "width": "230px"}),
        mo.md("#### Choose Team:"),
        mo.style(select_team, {"margin-left": "15px", "width": "230px"}),
        mo.md("#### Choose Match:"),
        mo.style(select_match, {"margin-left": "15px", "width": "230px"}),
    ], gap=0.5) 

    sidebar = mo.sidebar([menu_kontrol])
    sidebar
    return


@app.cell(hide_code=True)
def _(mo):
    mo.center(mo.md("# Football Visualization"))
    return


@app.cell
def _(client, query, selected_match):
    home_pl, away_pl = query.get_match_player(client, selected_match)
    return away_pl, home_pl


@app.cell(hide_code=True)
def _(mo):
    mo.center(mo.md("## Match Heatmap"))
    return


@app.cell
def _(client, selected_match, viz):
    viz.match_heatmaps(client, selected_match)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Home Shotmaps"), 
        {"margin-left": "20px"}
    )
    return


@app.cell
def _(client, selected_match, viz):
    home_shotmaps, away_shotmaps = viz.match_shotmaps(client, selected_match)
    return away_shotmaps, home_shotmaps


@app.cell
def _(home_shotmaps):
    home_shotmaps
    return


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Away Shotmaps"), 
        {"margin-left": "20px"}
    )
    return


@app.cell
def _(away_shotmaps):
    away_shotmaps
    return


@app.cell
def _():
    # viz.gk_profile_shots(
    #     client=client,
    #     match_id=14214896,
    #     home_color=theme.PLUM,
    #     away_color=theme.DEEP_WALLNUT
    # )
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Home Player Stats"), 
        {"margin-left": "10px"}
    )
    return


@app.cell
def _(home_pl, mo):
    select_home_pl = mo.ui.dropdown(options=home_pl, value=list(home_pl.keys())[0], full_width=True)
    # Memberi margin kiri dan kanan
    styled_select_home_pl = mo.style(
        select_home_pl, 
        {
            "margin-left": "10px", 
            "margin-right": "10px",
            # "width": "fit-content" # Agar dropdown tidak melebar memenuhi layar jika tidak diinginkan
        }
    )

    styled_select_home_pl
    return (select_home_pl,)


@app.cell
def _(select_home_pl):
    selected_home_pl = select_home_pl.value
    return (selected_home_pl,)


@app.cell
def _(client, selected_home_pl, selected_match, viz):
    viz.player_stats(client, selected_match, selected_home_pl)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Away Player Stats"), 
        {"margin-left": "10px"}
    )
    return


@app.cell
def _(away_pl, mo):
    select_away_pl = mo.ui.dropdown(options=away_pl, value=list(away_pl.keys())[0], full_width=True)
    # Memberi margin kiri dan kanan
    styled_select_away_pl = mo.style(
        select_away_pl, 
        {
            "margin-left": "10px", 
            "margin-right": "10px",
            # "width": "fit-content" # Agar dropdown tidak melebar memenuhi layar jika tidak diinginkan
        }
    )

    styled_select_away_pl
    return (select_away_pl,)


@app.cell
def _(select_away_pl):
    selected_away_pl = select_away_pl.value
    return (selected_away_pl,)


@app.cell
def _(client, selected_away_pl, selected_match, viz):
    viz.player_stats(client, selected_match, selected_away_pl)
    return


@app.cell
def _(client, query, selected_match):
    home_gk, away_gk = query.get_match_gk(client, selected_match)
    return away_gk, home_gk


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Home GK Stats"), 
        {"margin-left": "10px"}
    )
    return


@app.cell
def _(home_gk, mo):
    select_home_gk = mo.ui.dropdown(options=home_gk, value=list(home_gk.keys())[0], full_width=True)
    styled_select_home_gk = mo.style(
        select_home_gk, 
        {
            "margin-left": "10px", 
            "margin-right": "10px",
            # "width": "fit-content" # Agar dropdown tidak melebar memenuhi layar jika tidak diinginkan
        }
    )

    styled_select_home_gk
    return (select_home_gk,)


@app.cell
def _(select_home_gk):
    selected_home_gk = select_home_gk.value
    return (selected_home_gk,)


@app.cell
def _(client, selected_home_gk, selected_match, viz):
    viz.gk_stats(client, selected_match, selected_home_gk)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.style(
        mo.md("## Away GK Stats"), 
        {"margin-left": "10px"}
    )
    return


@app.cell
def _(away_gk, mo):
    select_away_gk = mo.ui.dropdown(options=away_gk, value=list(away_gk.keys())[0], full_width=True)
    styled_select_away_gk = mo.style(
        select_away_gk, 
        {
            "margin-left": "10px", 
            "margin-right": "10px",
        }
    )

    styled_select_away_gk
    return (select_away_gk,)


@app.cell
def _(select_away_gk):
    selected_away_gk = select_away_gk.value
    return (selected_away_gk,)


@app.cell
def _(client, selected_away_gk, selected_match, viz):
    viz.gk_stats(client, selected_match, selected_away_gk)
    return


if __name__ == "__main__":
    app.run()
