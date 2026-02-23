import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import module.query as query
import module.fonts as fonts
import constants.theme as theme

from mplsoccer import VerticalPitch, Pitch
from matplotlib.colors import LinearSegmentedColormap

def player_heatmap(client, match_id, player_id, vertical_pitch=True, pitch_color='#ffffff', line_color='#000000'):
    # 1. Ambil data koordinat (Pastikan fungsi ini mengembalikan list x dan y)
    # x_points, y_points harus berupa array-like (list/numpy array)
    try:
        x_points, y_points = query.get_player_heatmap(client, match_id, player_id)
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return None
    
    try:
        player_name = query.get_player_name(client, player_id)
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return None

    # 2. Cek apakah data tersedia
    if len(x_points) == 0 or len(y_points) == 0:
        print(f"Tidak ada data heatmap untuk pemain {player_id}")
        return None

    # 3. Setup Colormap (Putih ke Merah dengan transparansi awal agar pitch terlihat)
    customcmap = LinearSegmentedColormap.from_list('custom cmap', [pitch_color, 'red'])

    # 4. Inisialisasi Pitch
    if vertical_pitch:
        pitch = VerticalPitch(
            pitch_type='opta', # Gunakan 'opta' jika koordinat 0-100
            pitch_color=pitch_color,
            line_color=line_color,
            line_zorder=2
        )
    else:
        pitch = Pitch(
            pitch_type='opta', # Gunakan 'opta' jika koordinat 0-100
            pitch_color=pitch_color,
            line_color=line_color,
            line_zorder=2
        )

    fig, ax = pitch.draw(figsize=(8, 12)) # Ukuran disesuaikan untuk pitch vertikal
    fig.set_facecolor(pitch_color)

    # 5. Gambar KDE Plot (Heatmap)
    # n_levels tinggi (100) membuat gradasi sangat halus
    kde = pitch.kdeplot(
        x_points, y_points, 
        ax=ax, 
        cmap=customcmap, 
        fill=True, 
        n_levels=100, 
        zorder=1,
        thresh=0.05 # Menghilangkan warna di area yang densitasnya sangat rendah
    )

    arrow = pitch.arrows(40, 5, 60, 5, 
                         ax=ax, 
                         width=2, 
                         color='black', 
                         clip_on=False) # Agar tidak terpotong jika di luar batas axis

    # Tambahkan teks keterangan arah serangan jika perlu
    if vertical_pitch:
        arrow_txt = ax.text(8, 50, "Arah Serangan", rotation=90, verticalalignment='center')
    else:
        arrow_txt = ax.text(43, 8, "Arah Serangan", rotation=0, verticalalignment='center')

    match_name = query.get_match_name(client, match_id)

    plt.title(f"{match_name} \nPlayer Heatmap: {player_name}", color=line_color, size=15, pad=-20)

    return fig

def match_shotmaps(client, match_id, home_color=theme.PETAL_PINK, away_color=theme.STEEL_BLUE):
    # 1. Ambil data koordinat (Pastikan fungsi ini mengembalikan list x dan y)
    # x_points, y_points harus berupa array-like (list/numpy array)
    try:
        shotmaps_data = query.get_match_shotmaps(client, match_id)
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return None

    shotmap_df = pd.json_normalize(shotmaps_data)

    df_home_goal = shotmap_df[(shotmap_df['shot_type'] == 'goal') & (shotmap_df['is_home'] == True)]
    df_away_goal = shotmap_df[(shotmap_df['shot_type'] == 'goal') & (shotmap_df['is_home'] == False)]

    df_home_shot_on_goal = shotmap_df[(shotmap_df['shot_type'] == 'save') & (shotmap_df['is_home'] == True)]
    df_away_shot_on_goal = shotmap_df[(shotmap_df['shot_type'] == 'save') & (shotmap_df['is_home'] == False)]

    df_home_shot_off_goal = shotmap_df[(shotmap_df['shot_type'] == 'miss') & (shotmap_df['is_home'] == True)]
    df_away_shot_off_goal = shotmap_df[(shotmap_df['shot_type'] == 'miss') & (shotmap_df['is_home'] == False)]

    df_home_blocked_shots = shotmap_df[(shotmap_df['shot_type'] == 'block') & (shotmap_df['is_home'] == True)]
    df_away_blocked_shots = shotmap_df[(shotmap_df['shot_type'] == 'block') & (shotmap_df['is_home'] == False)]

    home_xg = float(shotmap_df[shotmap_df['is_home'] == True]['xG'].sum())
    away_xg = float(shotmap_df[shotmap_df['is_home'] == False]['xG'].sum())
    home_shots = len(shotmap_df[shotmap_df['is_home'] == True])
    away_shots = len(shotmap_df[shotmap_df['is_home'] == False])

    try:
        match_info = query.get_match_info(client, match_id)
    except Exception as er:
        print(f"Gagal mengambil data: {er}")
        return None
        
    home_pitch = VerticalPitch(
        pitch_type='opta', 
        pad_bottom=0.5, 
        half=True,  
        goal_alpha=0.8
    )

    home_fig, home_ax = home_pitch.draw(figsize=(12, 10))

    home_ax.set_xlim(105, -30)
    
    home_goal_scatter = home_pitch.scatter(
        list(map(lambda x: 99 - x, df_home_goal['draw_start_y'])), 
        list(map(lambda x: 100- x, df_home_goal['draw_start_x'])),
        s=(df_home_goal['xG'] * 900) +150,
        c=home_color,
        # edgecolors=theme.GRAPHITE,  # give the markers a charcoal border
        marker='o',
        ax=home_ax)

    home_shot_on_goal_scatter = home_pitch.scatter(
        list(map(lambda x: 99 - x, df_home_shot_on_goal['draw_start_y'])), 
        list(map(lambda x: 100 - x, df_home_shot_on_goal['draw_start_x'])),
        s=(df_home_shot_on_goal['xG'] * 900) + 150,
        edgecolors=home_color,  # give the markers a charcoal border
        c='None',  # no facecolor for the markers
        hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=home_ax)

    home_shot_off_goal_scatter = home_pitch.scatter(
        list(map(lambda x: 99 - x, df_home_shot_off_goal['draw_start_y'])), 
        list(map(lambda x: 100 - x, df_home_shot_off_goal['draw_start_x'])),
        s=(df_home_shot_off_goal['xG'] * 900) + 150,
        edgecolors=home_color,  # give the markers a charcoal border
        c='none',  # no facecolor for the markers
        # hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=home_ax)

    home_blocked_shots_scatter = home_pitch.scatter(
        list(map(lambda x: 99 - x, df_home_blocked_shots['draw_start_y'])), 
        list(map(lambda x: 100- x, df_home_blocked_shots['draw_start_x'])),
        s=(df_home_blocked_shots['xG'] * 900) + 150,
        c='None',
        edgecolors=home_color,  # give the markers a charcoal border
        marker='X',
        ax=home_ax)

    home_goal_legend_scatter = home_pitch.scatter(
        90, 
        -5,
        s=400,
        c=home_color,
        marker='o',
        ax=home_ax)
    
    home_goal_legend_txt = home_ax.text(
        x=-10, 
        y=90, 
        s=f'= Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    home_SonG_legend_scatter = home_pitch.scatter(
        85, 
        -5,
        s=400,
        edgecolors=home_color,  # give the markers a charcoal border
        c='None',  # no facecolor for the markers
        hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=home_ax)
    
    home_SonG_legend_txt = home_ax.text(
        x=-10, 
        y=85, 
        s=f'= Shots On Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    home_SoffG_legend_scatter = home_pitch.scatter(
        80, 
        -5,
        s=400,
        edgecolors=home_color,  # give the markers a charcoal border
        c='none',  # no facecolor for the markers
        marker='o',
        ax=home_ax)
    
    home_SoffG_legend_txt = home_ax.text(
        x=-10, 
        y=80, 
        s=f'= Shots Off Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    home_blocked_legend_scatter = home_pitch.scatter(
        75, 
        -5,
        s=400,
        c='None',
        edgecolors=home_color,  # give the markers a charcoal border
        marker='X',
        ax=home_ax)
    
    home_blocked_legend_txt = home_ax.text(
        x=-10, 
        y=75, 
        s=f'= Blocked Shots',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    home_team = match_info.get('home_team')

    home_txt = home_ax.text(
        x=50, 
        y=103, 
        s=f'{home_team}\'s Shotmaps',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='center')
    
    home_stats_txt = home_ax.text(
        x=50, 
        y=62, 
        s=f'xG: {home_xg:.2f} | total shots: {home_shots}',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=home_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='center')

    away_pitch = VerticalPitch(
        pitch_type='opta', 
        pad_bottom=0.5, 
        half=True,  
        goal_alpha=0.8
    )

    away_fig, away_ax = away_pitch.draw(figsize=(12, 10))

    away_ax.set_xlim(105, -30)
    
    away_goal_scatter = away_pitch.scatter(
        list(map(lambda x: 99 - x, df_away_goal['draw_start_y'])), 
        list(map(lambda x: 100- x, df_away_goal['draw_start_x'])),
        s=(df_away_goal['xG'] * 900) + 150,
        c=away_color,
        # edgecolors=theme.GRAPHITE,  # give the markers a charcoal border
        marker='o',
        ax=away_ax)

    away_shot_on_goal_scatter = away_pitch.scatter(
        list(map(lambda x: 99 - x, df_away_shot_on_goal['draw_start_y'])), 
        list(map(lambda x: 100 - x, df_away_shot_on_goal['draw_start_x'])),
        s=(df_away_shot_on_goal['xG'] * 900) + 150,
        edgecolors=away_color,  # give the markers a charcoal border
        c='None',  # no facecolor for the markers
        hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=away_ax)

    away_shot_off_goal_scatter = away_pitch.scatter(
        list(map(lambda x: 99 - x, df_away_shot_off_goal['draw_start_y'])), 
        list(map(lambda x: 100 - x, df_away_shot_off_goal['draw_start_x'])),
        s=(df_away_shot_off_goal['xG'] * 900) + 150,
        edgecolors=away_color,  # give the markers a charcoal border
        c='none',  # no facecolor for the markers
        # hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=away_ax)

    away_blocked_shots_scatter = away_pitch.scatter(
        list(map(lambda x: 99 - x, df_away_blocked_shots['draw_start_y'])), 
        list(map(lambda x: 100- x, df_away_blocked_shots['draw_start_x'])),
        s=(df_away_blocked_shots['xG'] * 900) + 150,
        c='None',
        edgecolors=away_color,  # give the markers a charcoal border
        marker='X',
        ax=away_ax)

    away_goal_legend_scatter = away_pitch.scatter(
        90, 
        -5,
        s=400,
        c=away_color,
        marker='o',
        ax=away_ax)
    
    away_goal_legend_txt = away_ax.text(
        x=-10, 
        y=90, 
        s=f'= Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    away_SonG_legend_scatter = away_pitch.scatter(
        85, 
        -5,
        s=400,
        edgecolors=away_color,  # give the markers a charcoal border
        c='None',  # no facecolor for the markers
        hatch='///',  # the all important hatch (triple diagonal lines)
        marker='o',
        ax=away_ax)
    
    away_SonG_legend_txt = away_ax.text(
        x=-10, 
        y=85, 
        s=f'= Shots On Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    away_SoffG_legend_scatter = away_pitch.scatter(
        80, 
        -5,
        s=400,
        edgecolors=away_color,  # give the markers a charcoal border
        c='none',  # no facecolor for the markers
        marker='o',
        ax=away_ax)
    
    away_SoffG_legend_txt = away_ax.text(
        x=-10, 
        y=80, 
        s=f'= Shots Off Goal',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')
    
    away_blocked_legend_scatter = away_pitch.scatter(
        75, 
        -5,
        s=400,
        c='None',
        edgecolors=away_color,  # give the markers a charcoal border
        marker='X',
        ax=away_ax)
    
    away_blocked_legend_txt = away_ax.text(
        x=-10, 
        y=75, 
        s=f'= Blocked Shots',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='left')

    away_team = match_info.get('away_team')
    away_txt = away_ax.text(
        x=50, 
        y=103, 
        s=f'{away_team}\'s Shotmaps',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='center')
    
    away_stats_txt = away_ax.text(
        x=50, 
        y=62, 
        s=f'xG: {away_xg:.2f} | total shots: {away_shots}',
        size=20,
        # here i am using a downloaded font from google fonts instead of passing a fontdict
        color=away_pitch.line_color,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        va='center', ha='center')


    return home_fig, away_fig

def gk_profile_shots(client, match_id, home_color, away_color):
    
    home_team, away_team = query.get_match_team_name(client, match_id)
    
    shots_on_goal_data = query.get_shots_on_goal(client, match_id)
    shots_on_goal_df = pd.json_normalize(shots_on_goal_data)
    
    shots_data = query.get_shot_stats(client, match_id)
    shots_df = pd.json_normalize(shots_data)
    
    hShotsdf = shots_on_goal_df[shots_on_goal_df['is_home']==True].copy()
    aShotsdf = shots_on_goal_df[shots_on_goal_df['is_home']==False].copy()

    # converting the datapoints according to the pitch dimension, because the goalposts are being plotted inside the pitch using pitch's dimension
    hShotsdf.loc[:, 'goal_mouth_coord_z'] = hShotsdf['goal_mouth_coord_z']*0.75
    aShotsdf.loc[:, 'goal_mouth_coord_z'] = (aShotsdf['goal_mouth_coord_z']*0.75) + 40

    # Mengubah data list atau kolom dataframe
    hShotsdf.loc[:, 'goal_mouth_coord_y'] = np.interp(
        hShotsdf['goal_mouth_coord_y'], 
        [45, 55],       # Rentang asal
        [97.5, 7.5]      # Rentang tujuan
    )
    # Mengubah data list atau kolom dataframe
    aShotsdf.loc[:, 'goal_mouth_coord_y'] = np.interp(
        aShotsdf['goal_mouth_coord_y'], 
        [45, 55],       # Rentang asal
        [97.5, 7.5]     # Rentang tujuan
    )

    # plotting an invisible pitch using the pitch color and line color same color, because the goalposts are being plotted inside the pitch using pitch's dimension
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(22, 10))
    goal_pitch = Pitch(pitch_type='uefa', corner_arcs=True, pitch_color=theme.SNOW, line_color=theme.SNOW, linewidth=2)
    goal_pitch.draw(ax=axs[0])

    stats_pitch = Pitch(pitch_type='uefa', corner_arcs=True, pitch_color=theme.SNOW, line_color=theme.SNOW, linewidth=2)
    stats_pitch.draw(ax=axs[1])

    axs[0].set_ylim(-5, 78) 
    axs[0].set_xlim(-0.5, 105.5)

    axs[1].set_ylim(-5, 78) 
    axs[1].set_xlim(-0.5, 105.5)


    # away goalpost bars
    axs[0].plot([7.5, 7.5], [0, 30], color='#000000', linewidth=5)
    axs[0].plot([7.5, 97.5], [30, 30], color='#000000', linewidth=5)
    axs[0].plot([97.5, 97.5], [30, 0], color='#000000', linewidth=5)
    axs[0].plot([5, 100], [-0.15, -0.15], color='#000000', linewidth=3)


    # home goalpost bars
    axs[0].plot([7.5, 7.5], [40, 70], color='#000000', linewidth=5)
    axs[0].plot([7.5, 97.5], [70, 70], color='#000000', linewidth=5)
    axs[0].plot([97.5, 97.5], [70, 40], color='#000000', linewidth=5)
    axs[0].plot([5, 100], [39.85, 39.85], color='#000000', linewidth=3)


    # --- AWAY GOALPOST (Bawah) ---
    # Rentang y adalah 0 sampai 30
    y_values_away = np.linspace(0, 30, 3) 

    # Rentang x adalah 7.5 sampai 97.5
    x_values_away = np.linspace(7.5, 97.5, 4)

    for y in y_values_away:
        axs[0].plot([7.5, 97.5], [y, y], color='#000000', linewidth=2, alpha=0.2, linestyle='--')

    for x in x_values_away:
        axs[0].plot([x, x], [0, 30], color='#000000', linewidth=2, alpha=0.2, linestyle='--')


    # --- HOME GOALPOST (Atas) ---
    # Rentang y adalah 40 sampai 70
    y_values_home = np.linspace(40, 70, 3)

    x_values_home = np.linspace(7.5, 97.5, 4)

    for y in y_values_home:
        axs[0].plot([7.5, 97.5], [y, y], color='#000000', linewidth=2, alpha=0.2, linestyle='--')

    for x in x_values_home:
        axs[0].plot([x, x], [40, 70], color='#000000', linewidth=2, alpha=0.2, linestyle='--')

    # filtering different types of shots
    hSavedf = hShotsdf[(hShotsdf['shot_type']=='save')] 
    hGoaldf = hShotsdf[(hShotsdf['shot_type']=='goal')]
    hPostdf = hShotsdf[(hShotsdf['shot_type']=='post')]
    aSavedf = aShotsdf[(aShotsdf['shot_type']=='save')] 
    aGoaldf = aShotsdf[(aShotsdf['shot_type']=='goal')] 
    aPostdf = aShotsdf[(aShotsdf['shot_type']=='post')]

    # scattering those shots
    sc1 = goal_pitch.scatter(hSavedf.goal_mouth_coord_y, hSavedf.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolor=home_color, hatch='/////', s=400, ax=axs[0])
    sc2 = goal_pitch.scatter(hGoaldf.goal_mouth_coord_y, hGoaldf.goal_mouth_coord_z, marker='football', c=theme.SNOW, zorder=3, edgecolors='#000000', s=400, ax=axs[0])
    sc3 = goal_pitch.scatter(hPostdf.goal_mouth_coord_y, hPostdf.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolors=theme.GOLDEN_SAND, hatch='/////', s=400, ax=axs[0])
    sc4 = goal_pitch.scatter(aSavedf.goal_mouth_coord_y, aSavedf.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolor=away_color, hatch='/////', s=400, ax=axs[0])
    sc5 = goal_pitch.scatter(aGoaldf.goal_mouth_coord_y, aGoaldf.goal_mouth_coord_z, marker='football', c=theme.SNOW, zorder=3, edgecolors='#000000', s=400, ax=axs[0])
    sc6 = goal_pitch.scatter(aPostdf.goal_mouth_coord_y, aPostdf.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolors=theme.GOLDEN_SAND, hatch='/////', s=400, ax=axs[0])

    a_high_left = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'high-left'])
    a_high_center = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'high-centre'])
    a_high_right = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'high-right'])
    a_low_left = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'low-left'])
    a_low_center = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'low-centre'])
    a_low_right = len(aShotsdf[aShotsdf['goal_mouth_location'] == 'low-right'])

    h_high_left = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'high-left'])
    h_high_center = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'high-centre'])
    h_high_right = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'high-right'])
    h_low_left = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'low-left'])
    h_low_center = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'low-centre'])
    h_low_right = len(hShotsdf[hShotsdf['goal_mouth_location'] == 'low-right'])

    home_txt = axs[0].text(
        x=52, 
        y=74, 
        s=f'{home_team}\'s Goal Profile',
        size=20,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')
    away_txt = axs[0].text(
        x=52, 
        y=34, 
        s=f'{away_team}\'s Goal Profile',
        size=20,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')

    a_high_left_txt = axs[0].text(
        x=22, 
        y=24, 
        s=f'High Left',
        size=20,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        color='#000000',
        va='center', 
        ha='center')
    a_high_left_val_text = axs[0].text(
        x=22, 
        y=20, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_high_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_high_center_txt = axs[0].text(
        x=52, 
        y=24, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_high_center_val_txt = axs[0].text(
        x=52, 
        y=20, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_high_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_high_right_txt = axs[0].text(
        x=82, 
        y=24, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Right',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_high_right_val_txt = axs[0].text(
        x=82, 
        y=20, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_high_right}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_left_txt = axs[0].text(
        x=22, 
        y=9, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Left',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_left_val_txt = axs[0].text(
        x=22, 
        y=5, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_low_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_center_txt = axs[0].text(
        x=52, 
        y=9, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_center_val_txt = axs[0].text(
        x=52, 
        y=5, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_low_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_right_txt = axs[0].text(
        x=82, 
        y=9, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Right',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    a_low_right_val_txt = axs[0].text(
        x=82, 
        y=5, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{h_low_right}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')

    # Home Text
    h_high_left_txt = axs[0].text(
        x=22, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Left',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_left_val_txt = axs[0].text(
        x=22, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_center_txt = axs[0].text(
        x=52, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_center_val_txt = axs[0].text(
        x=52, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_right_txt = axs[0].text(
        x=82, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Right',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_right_val_txt = axs[0].text(
        x=82, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_right}',
        size=20,
        color='#000000',
        va='center', ha='center')
    h_low_left_txt = axs[0].text(
        x=22, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Left',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_left_val_txt = axs[0].text(
        x=22, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_center_txt = axs[0].text(
        x=52, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_center_val_txt = axs[0].text(
        x=52, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_right_txt = axs[0].text(
        x=82, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Right',
        size=20,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')
    h_low_right_val_txt = axs[0].text(
        x=82, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_right}',
        size=20,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')

    # Tambahkan parameter pad untuk mengatur margin keseluruhan
    plt.tight_layout(pad=1.0)
    shot_stats_txt = axs[1].text(52.5,70, "Shot Stats", ha='center', va='center', color=theme.GRAPHITE, fontsize=25, fontproperties=fonts.GOOGLE_SANS_FONT)

    # Fungsi pembantu agar kode lebih bersih dan aman jika data kosong
    def get_val(df, key, side):
        val = df[df['key'] == key][side]
        return float(val.iloc[0]) if not val.empty else 0.0

    # Ambil nilai sebagai skalar (angka tunggal)
    h_total_shots = get_val(shots_df, 'totalShotsOnGoal', 'homeValue')
    a_total_shots = get_val(shots_df, 'totalShotsOnGoal', 'awayValue')

    h_shots_on_target = get_val(shots_df, 'shotsOnGoal', 'homeValue')
    a_shots_on_target = get_val(shots_df, 'shotsOnGoal', 'awayValue')

    h_hit_woodwork = get_val(shots_df, 'hitWoodwork', 'homeValue')
    a_hit_woodwork = get_val(shots_df, 'hitWoodwork', 'awayValue')

    h_shots_off_goal = get_val(shots_df, 'shotsOffGoal', 'homeValue')
    a_shots_off_goal = get_val(shots_df, 'shotsOffGoal', 'awayValue')

    h_blocked_shots = get_val(shots_df, 'blockedScoringAttempt', 'homeValue')
    a_blocked_shots = get_val(shots_df, 'blockedScoringAttempt', 'awayValue')

    h_shot_inside_box = get_val(shots_df, 'totalShotsInsideBox', 'homeValue')
    a_shot_inside_box = get_val(shots_df, 'totalShotsInsideBox', 'awayValue')

    h_shot_outside_box = get_val(shots_df, 'totalShotsOutsideBox', 'homeValue')
    a_shot_outside_box = get_val(shots_df, 'totalShotsOutsideBox', 'awayValue')

    h_gk_saves = get_val(shots_df, 'goalkeeperSaves', 'homeValue')
    a_gk_saves = get_val(shots_df, 'goalkeeperSaves', 'awayValue')

    # Stats bar diagram
    stats_title = [58, 58-(1*6), 58-(2*6), 58-(3*6), 58-(4*6), 58-(5*6), 58-(6*6), 58-(7*6)] # y co-ordinate values of the bars
    stats_home = [h_total_shots, h_shots_on_target, h_hit_woodwork, h_shots_off_goal, h_blocked_shots, h_shot_inside_box, h_shot_outside_box, h_gk_saves]
    stats_away = [a_total_shots, a_shots_on_target, a_hit_woodwork, a_shots_off_goal, a_blocked_shots, a_shot_inside_box, a_shot_outside_box, a_gk_saves]

    # Fungsi untuk melakukan normalisasi proporsional
    def normalize_stat(home_val, away_val, scale=40):
        total = home_val + away_val
        if total == 0:
            return 0, 0
        # Home menjadi negatif (ke kiri), Away positif (ke kanan)
        home_norm = -(home_val / total) * scale
        away_norm = (away_val / total) * scale
        return home_norm, away_norm

    # List untuk menampung hasil akhir
    stats_norm_home = []
    stats_norm_away = []

    # Daftar pasangan variabel yang sudah Anda ambil sebelumnya
    shot_pairs = [
        (h_total_shots, a_total_shots),
        (h_shots_on_target, a_shots_on_target),
        (h_hit_woodwork, a_hit_woodwork),
        (h_shots_off_goal, a_shots_off_goal),
        (h_blocked_shots, a_blocked_shots),
        (h_shot_inside_box, a_shot_inside_box),
        (h_shot_outside_box, a_shot_outside_box),
        (h_gk_saves, a_gk_saves)
    ]

    # Proses normalisasi dalam loop
    for h, a in shot_pairs:
        h_n, a_n = normalize_stat(h, a)
        stats_norm_home.append(h_n)
        stats_norm_away.append(a_n)

    start_x = 52.5
    home_bar = axs[1].barh(stats_title, stats_norm_home, height=4, left=start_x, hatch='/////', edgecolor=home_color, color=theme.SNOW)
    away_bar = axs[1].barh(stats_title, stats_norm_away, height=4, left=start_x, hatch='/////', edgecolor=away_color, color=theme.SNOW)

    # Plotting the texts
    total_shots_txt = axs[1].text(52.5, 58, "Total Shots", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    shots_on_target_txt = axs[1].text(52.5, 58-(1*6), "Shots On Target", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    hit_woodwork_txt = axs[1].text(52.5, 58-(2*6), "Hit Woodwork", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    shots_off_goal_txt = axs[1].text(52.5, 58-(3*6), "Shots Off Goal", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    blocked_goals_txt = axs[1].text(52.5, 58-(4*6), "Blocked Shots", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    shots_inside_box_txt = axs[1].text(52.5, 58-(5*6), "Shots Inside Box", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    shots_outside_box_txt = axs[1].text(52.5, 58-(6*6), "Shots Outside Box", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    gk_saves_txt = axs[1].text(52.5, 58-(7*6), "GK Saves", color=theme.GRAPHITE, fontsize=17, ha='center', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)

    h_total_shots_val_txt = axs[1].text(5, 58, f"{int(h_total_shots)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_shots_on_target_val_txt = axs[1].text(5, 58-(1*6), f"{int(h_shots_on_target)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_hit_woodwork_val_txt = axs[1].text(5, 58-(2*6), f"{int(h_hit_woodwork)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_shots_off_goal_val_txt = axs[1].text(5, 58-(3*6), f"{int(h_shots_off_goal)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_blocked_shots_val_txt = axs[1].text(5, 58-(4*6), f"{int(h_blocked_shots)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_shot_inside_box_val_txt = axs[1].text(5, 58-(5*6), f"{int(h_shot_inside_box)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_shot_outside_box_val_txt = axs[1].text(5, 58-(6*6), f"{int(h_shot_outside_box)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    h_gk_saves_val_txt = axs[1].text(5, 58-(7*6), f"{int(h_gk_saves)}", color=theme.GRAPHITE, fontsize=20, ha='right', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)

    a_total_shots_val_txt = axs[1].text(100, 58, f"{int(a_total_shots)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_shots_on_target_val_txt = axs[1].text(100, 58-(1*6), f"{int(a_shots_on_target)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_hit_woodwork_val_txt = axs[1].text(100, 58-(2*6), f"{int(a_hit_woodwork)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_shots_off_goal_val_txt = axs[1].text(100, 58-(3*6), f"{int(a_shots_off_goal)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_blocked_shots_val_txt = axs[1].text(100, 58-(4*6), f"{int(a_blocked_shots)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_shot_inside_box_val_txt = axs[1].text(100, 58-(5*6), f"{int(a_shot_inside_box)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_shot_outside_box_val_txt = axs[1].text(100, 58-(6*6), f"{int(a_shot_outside_box)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    a_gk_saves_val_txt = axs[1].text(100, 58-(7*6), f"{int(a_gk_saves)}", color=theme.GRAPHITE, fontsize=20, ha='left', va='center', fontproperties=fonts.GOOGLE_SANS_FONT)
    
    return fig 

def gk_stats(client, match_id, player_id, pitch_color=theme.SNOW, line_color=theme.GRAPHITE):
    gk_stats = query.get_match_gk_stats(client, match_id, player_id)
    
    home_team, away_team = query.get_match_team_name(client, match_id)
    
    player_name = gk_stats.get('name', {})
    player_stats = gk_stats.get('stats', {})
    shots_conceded_data = gk_stats.get('shot_conceded', [])
    shots_conceded_df = pd.DataFrame(shots_conceded_data)
    
    # converting the datapoints according to the pitch dimension, because the goalposts are being plotted inside the pitch using pitch's dimension
    shots_conceded_df.loc[:, 'goal_mouth_coord_z'] = (shots_conceded_df['goal_mouth_coord_z']*0.75) + 40

    # Mengubah data list atau kolom dataframe
    shots_conceded_df.loc[:, 'goal_mouth_coord_y'] = np.interp(
        shots_conceded_df['goal_mouth_coord_y'], 
        [45, 55],       # Rentang asal
        [97.5, 7.5]     # Rentang tujuan
    )

    player_fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(22, 10), gridspec_kw={'wspace': -0.2})

    goal_pitch = Pitch(
        pitch_type='uefa', 
        corner_arcs=True, 
        pitch_color=theme.SNOW, 
        line_color=theme.SNOW, 
        linewidth=2)
    goal_pitch.draw(ax=axs[0])

    stats_pitch = Pitch(
        pitch_type='uefa', 
        corner_arcs=True,
        pitch_color=pitch_color, 
        line_color=pitch_color, 
        linewidth=2)
    stats_pitch.draw(ax=axs[1])

    axs[0].set_ylim(0, 100) 
    axs[0].set_xlim(-0.5, 125.5)

    # home goalpost bars
    axs[0].plot([7.5, 7.5], [40, 70], color='#000000', linewidth=5)
    axs[0].plot([7.5, 97.5], [70, 70], color='#000000', linewidth=5)
    axs[0].plot([97.5, 97.5], [70, 40], color='#000000', linewidth=5)
    axs[0].plot([5, 100], [39.85, 39.85], color='#000000', linewidth=3)

    # --- HOME GOALPOST (Atas) ---
    # Rentang y adalah 40 sampai 70
    y_values_home = np.linspace(40, 70, 3)

    x_values_home = np.linspace(7.5, 97.5, 4)

    for y in y_values_home:
        axs[0].plot([7.5, 97.5], [y, y], color='#000000', linewidth=2, alpha=0.2, linestyle='--')

    for x in x_values_home:
        axs[0].plot([x, x], [40, 70], color='#000000', linewidth=2, alpha=0.2, linestyle='--')

    # filtering different types of shots
    saved_df = shots_conceded_df[(shots_conceded_df['shot_type']=='save')] 
    goal_df = shots_conceded_df[(shots_conceded_df['shot_type']=='goal')] 
    post_df = shots_conceded_df[(shots_conceded_df['shot_type']=='post')]

    sc4 = goal_pitch.scatter(saved_df.goal_mouth_coord_y, saved_df.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolor=theme.CAMEL, hatch='/////', s=400, ax=axs[0])
    sc5 = goal_pitch.scatter(goal_df.goal_mouth_coord_y, goal_df.goal_mouth_coord_z, marker='football', c=theme.SNOW, zorder=3, edgecolors='#000000', s=400, ax=axs[0])
    sc6 = goal_pitch.scatter(post_df.goal_mouth_coord_y, post_df.goal_mouth_coord_z, marker='o', c=theme.SNOW, zorder=3, edgecolors=theme.GOLDEN_SAND, hatch='/////', s=400, ax=axs[0])

    a_high_left = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'high-left'])
    a_high_center = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'high-centre'])
    a_high_right = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'high-right'])
    a_low_left = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'low-left'])
    a_low_center = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'low-centre'])
    a_low_right = len(shots_conceded_df[shots_conceded_df['goal_mouth_location'] == 'low-right'])

    xg = float(shots_conceded_df['xG'].sum())
    xgot = float(shots_conceded_df['xGOT'].sum())
    total_saves = len(shots_conceded_df[shots_conceded_df['shot_type'] == 'save'])

    shot_save_stats_txt = axs[0].text(
        x=52, 
        y=30, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'XG: {xg:.3f} | XGOT: {xgot:.3f} | Total Saves: {total_saves}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    
    home_txt = axs[0].text(
        x=52, 
        y=74, 
        s=f'{player_name}\'s Goal Profile',
        size=20,
        fontproperties=fonts.GOOGLE_SANS_FONT,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')

    # Home Text
    h_high_left_txt = axs[0].text(
        x=22, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Left',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_left_val_txt = axs[0].text(
        x=22, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_center_txt = axs[0].text(
        x=52, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_center_val_txt = axs[0].text(
        x=52, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_right_txt = axs[0].text(
        x=82, 
        y=64, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'High Right',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_high_right_val_txt = axs[0].text(
        x=82, 
        y=60, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_high_right}',
        size=20,
        color='#000000',
        va='center', ha='center')
    h_low_left_txt = axs[0].text(
        x=22, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Left',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_left_val_txt = axs[0].text(
        x=22, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_left}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_center_txt = axs[0].text(
        x=52, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Center',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_center_val_txt = axs[0].text(
        x=52, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_center}',
        size=20,
        color='#000000',
        va='center', 
        ha='center')
    h_low_right_txt = axs[0].text(
        x=82, 
        y=49, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'Low Right',
        size=20,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')
    h_low_right_val_txt = axs[0].text(
        x=82, 
        y=45, 
        fontproperties=fonts.GOOGLE_SANS_FONT,
        s=f'{a_low_right}',
        size=20,
        color=theme.GRAPHITE,
        va='center', 
        ha='center')

    stats_title = axs[1].text(0.5, 0.95, f"{home_team} vs {away_team}", 
            verticalalignment='center', 
            horizontalalignment='center', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    stats_title = axs[1].text(0.5, 0.9, f"{player_name} Individual Stats", 
            verticalalignment='center', 
            horizontalalignment='center', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    acc_pass_txt = axs[1].text(0.05, 0.8, "Passes", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accuratePass = player_stats.get('accuratePass', 0)
    totalPass = player_stats.get('totalPass', 0)
    acc_pass_val = axs[1].text(0.45, 0.8, f"{accuratePass}/{totalPass}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    pass_in_opp_txt = axs[1].text(0.05, 0.75, "Pass in Opp. Half", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accurateOppositionHalfPasses = player_stats.get('accurateOppositionHalfPasses', 0)
    totalOppositionHalfPasses = player_stats.get('totalOppositionHalfPasses', 0)

    pass_in_opp_val = axs[1].text(0.45, 0.75, f"{accurateOppositionHalfPasses}/{totalOppositionHalfPasses}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    pass_in_own_txt = axs[1].text(0.05, 0.7, "Pass in Own Half", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accurateOwnHalfPasses = accuratePass - accurateOppositionHalfPasses
    totalOwnHalfPasses = totalPass - totalOppositionHalfPasses

    pass_in_own_val = axs[1].text(0.45, 0.7, f"{accurateOwnHalfPasses}/{totalOwnHalfPasses}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    long_ball_txt = axs[1].text(0.05, 0.65, "Long Ball", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accurateLongBalls = player_stats.get('accurateLongBalls', 0)
    totalLongBalls = player_stats.get('totalLongBalls', 0)
    long_ball_val = axs[1].text(0.45, 0.65, f"{accurateLongBalls}/{totalLongBalls}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    touches_txt = axs[1].text(0.05, 0.6, "Touches", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    touches = player_stats.get('touches', 0)
    touches_val = axs[1].text(0.45, 0.6, f"{touches}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    keypass_txt = axs[1].text(0.05, 0.55, "Key Pass", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    keyPass = player_stats.get('keyPass', 0)
    keypass_val = axs[1].text(0.45, 0.55, f"{keyPass}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    keeper_sweeper_txt = axs[1].text(0.05, 0.45, "Sweep", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accurateKeeperSweeper = player_stats.get('accurateKeeperSweeper', 0)
    totalKeeperSweeper = player_stats.get('totalKeeperSweeper', 0)
    keeper_sweeper_val = axs[1].text(0.45, 0.45, f"{accurateKeeperSweeper}/{totalKeeperSweeper}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    gk_claim_txt = axs[1].text(0.05, 0.4, "Claim", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    goodHighClaim = player_stats.get('goodHighClaim', 0)
    crossNotClaimed = player_stats.get('crossNotClaimed', 0)
    totalClaim = goodHighClaim + crossNotClaimed
    gk_claim_val = axs[1].text(0.45, 0.4, f"{goodHighClaim}/{totalClaim}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    saves_txt = axs[1].text(0.05, 0.35, "Saves", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    saves = player_stats.get('saves', 0)
    saves_val = axs[1].text(0.45, 0.35, f"{saves}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    saves_inside_txt = axs[1].text(0.05, 0.3, "Saves Fr. Inside Box", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    savedShotsFromInsideTheBox = player_stats.get('savedShotsFromInsideTheBox', 0)
    saves_inside_val = axs[1].text(0.45, 0.3, f"{savedShotsFromInsideTheBox}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    punches_txt = axs[1].text(0.05, 0.25, "Punches", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    punches = player_stats.get('punches', 0)
    punches_val = axs[1].text(0.45, 0.25, f"{punches}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    tackles_txt = axs[1].text(0.55, 0.8, "Tackles", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    wonTackle = player_stats.get('wonTackle', 0)
    totalTackle = player_stats.get('totalTackle', 0)
    tackles_val = axs[1].text(0.95, 0.8, f"{wonTackle}/{totalTackle}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    interception_txt = axs[1].text(0.55, 0.75, "Interceptions", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    interceptionWon = player_stats.get('interceptionWon', 0)
    interception_val = axs[1].text(0.95, 0.75, f"{interceptionWon}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    clearances_txt = axs[1].text(0.55, 0.7, "Clearances", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    totalClearance = player_stats.get('totalClearance', 0)
    clearances_val = axs[1].text(0.95, 0.7, f"{totalClearance}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    recoveries_txt = axs[1].text(0.55, 0.65, "Recoveries", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    ballRecovery = player_stats.get('ballRecovery', 0)
    recoveries_txt = axs[1].text(0.95, 0.65, f"{ballRecovery}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)


    aerial_txt = axs[1].text(0.55, 0.5, "Aerial Duels", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    aerialWon = player_stats.get('aerialWon', 0)
    aerialLost = player_stats.get('aerialLost', 0)
    aerial_val = axs[1].text(0.95, 0.5, f"{aerialWon}/{aerialLost + aerialWon}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    ground_duels_txt = axs[1].text(0.55, 0.55, "Ground Duels", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    duelWon = player_stats.get('duelWon', 0)
    duelLost = player_stats.get('duelLost', 0)
    groundDuelWon = duelWon - aerialWon
    groundDuelLost = duelLost - aerialLost
    totalGroundDuel = groundDuelWon + groundDuelLost
    ground_duels_val = axs[1].text(0.95, 0.55, f"{groundDuelWon}/{totalGroundDuel}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)


    dribble_past_txt = axs[1].text(0.55, 0.4, "Dribbled Past", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    challengeLost = player_stats.get('challengeLost', 0)
    dribble_past_val = axs[1].text(0.95, 0.4, f"{challengeLost}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    error_txt = axs[1].text(0.55, 0.35, "Errors Leads To Shot", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    errorLeadToAShot = player_stats.get('errorLeadToAShot', 0)
    error_val = axs[1].text(0.95, 0.35, f"{errorLeadToAShot}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    possession_lost_txt = axs[1].text(0.55, 0.3, "Possession Lost", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    possessionLostCtrl = player_stats.get('possessionLostCtrl', 0)
    possession_lost_val = axs[1].text(0.95, 0.3, f"{possessionLostCtrl}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    return player_fig

def match_heatmaps(client, match_id, pitch_color=theme.SNOW, line_color=theme.GRAPHITE):
    try:
        home_heatmaps_points, away_heatmaps_points = query.get_match_heatmaps(client, match_id)
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return None

    home_team, away_team = query.get_match_team_name(client, match_id)

    home_x_points = []
    home_y_points = []
    for home_heatmap_point in home_heatmaps_points:
        home_x_points.append(home_heatmap_point.get('x'))
        home_y_points.append(home_heatmap_point.get('y'))

    away_x_points = []
    away_y_points = []
    for away_heatmap_point in away_heatmaps_points:
        away_x_points.append(away_heatmap_point.get('x'))
        away_y_points.append(away_heatmap_point.get('y'))

    home_pitch = VerticalPitch(
        pitch_type='opta', # Gunakan 'opta' jika koordinat 0-100
        pitch_color=pitch_color,
        line_color=line_color,
        line_zorder=2
    )

    away_pitch = VerticalPitch(
        pitch_type='opta', # Gunakan 'opta' jika koordinat 0-100
        pitch_color=pitch_color,
        line_color=line_color,
        line_zorder=2
    )

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(22, 10), gridspec_kw={'wspace': -0.5})
    plt.tight_layout(pad=1.0)

    home_pitch.draw(ax=axs[0])
    away_pitch.draw(ax=axs[1])

    home_customcmap = LinearSegmentedColormap.from_list('home custom cmap', [pitch_color, theme.STEEL_BLUE])
    away_customcmap = LinearSegmentedColormap.from_list('away custom cmap', [pitch_color, theme.BROWN_RED])

    # KDE Home
    home_kde = home_pitch.kdeplot(
        list(map(lambda x: 99 - x, home_x_points)), 
        list(map(lambda x: 100 - x, home_y_points)),
        ax=axs[0], 
        cmap=home_customcmap, 
        fill=True, 
        n_levels=100, 
        zorder=1,
        thresh=0.05,
    )

    home_arrow = home_pitch.arrows(55, 5, 45, 5, 
                         ax=axs[0], 
                         width=2, 
                         color='black', 
                         clip_on=False)

    home_title = axs[0].set_title(f'{home_team}\'s Heatmap', fontsize=15, color=theme.GRAPHITE, pad=5, fontproperties=fonts.GOOGLE_SANS_FONT)

    # KDE Away
    away_kde = away_pitch.kdeplot(
        away_x_points, 
        away_y_points,
        ax=axs[1], 
        cmap=away_customcmap, 
        fill=True, 
        n_levels=100, 
        zorder=1,
        thresh=0.05,
    )

    away_arrow = away_pitch.arrows(45, 95, 55, 95, 
                         ax=axs[1], 
                         width=2, 
                         color='black', 
                         clip_on=False)

    away_title = axs[1].set_title(f'{away_team}\'s Heatmap', fontsize=15, color=theme.GRAPHITE, pad=5, fontproperties=fonts.GOOGLE_SANS_FONT)

    return fig

def player_stats(client, match_id, player_id, pitch_color=theme.SNOW, line_color=theme.GRAPHITE):
    try:
        x_points, y_points = query.get_player_heatmap(client, match_id, player_id)
    except Exception as e:
        print(f'Gagal mengambil heatmap points: {e}')
        return None

    try:
        player_data = query.get_match_player_stats(client, match_id, player_id)
    except Exception as e:
        print(f'Gagal mengambil player stats: {e}')
        return None
    
    try:
        player_name = query.get_player_name(client, player_id)
    except Exception as e:
        print(f'Gagal mengambil player name: {e}')
        return None
    
    try:
        home_team, away_team = query.get_match_team_name(client, match_id)
    except Exception as e:
        print(f'Gagal mengambil player name: {e}')
        return None
    
    customcmap = LinearSegmentedColormap.from_list('custom cmap', [pitch_color, theme.BROWN_RED])

    player_stats = player_data.get('statistics')
    player_shots = player_data.get('shots', None)
    
    pitch = VerticalPitch(
        pitch_type='opta', # Gunakan 'opta' jika koordinat 0-100
        pitch_color=pitch_color,
        line_color=line_color,
        line_zorder=2,
        linewidth=1
    )

    stats_pitch = Pitch(
        pitch_type='uefa', 
        corner_arcs=True,
        pitch_color=pitch_color, 
        line_color=pitch_color, 
        linewidth=2)

    player_fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(22, 10), gridspec_kw={'wspace': -0.2})

    pitch.draw(ax=axs[0])
    stats_pitch.draw(ax=axs[1])

    x_edges = [0, 16.6, 33.2, 49.8, 66.4, 83.0, 100]  

    # Tentukan garis pembatas manual untuk sumbu Y (0 sampai 80)
    y_edges = [0, 21, 37, 63, 79, 100]     

    bin_statistic = pitch.bin_statistic(x_points, y_points, statistic='count', 
                                    bins=(x_edges, y_edges))
    # bin_statistic = pitch.bin_statistic(x_points, y_points, statistic='count', bins=(6, 5))
    
    pcm = pitch.heatmap(bin_statistic, ax=axs[0], cmap=customcmap, edgecolor='none', alpha=0.9)
    
    pitch.label_heatmap(bin_statistic, color=line_color, fontsize=15, ax=axs[0], ha='center', va='center', str_format='{:.0f}', fontproperties=fonts.GOOGLE_SANS_FONT)
    
    arrow = pitch.arrows(45, -5, 55, -5, 
                         ax=axs[0], 
                         width=2, 
                         color='black', 
                         clip_on=False)

    if player_shots:
        shotmap_df = pd.DataFrame(player_shots)
        scored_df = shotmap_df[(shotmap_df['shot_type'] == 'goal')]
        saved_df = shotmap_df[(shotmap_df['shot_type'] == 'save')]
        missed_df = shotmap_df[(shotmap_df['shot_type'] == 'miss')]
        blocked_df = shotmap_df[(shotmap_df['shot_type'] == 'block')]

        # 1. Definisikan koordinat (lakukan transformasi sekaligus jika perlu)
        # Gunakan operasi vektor Pandas (lebih cepat & bersih)

        # 2. Plot Scatter (Titik awal tembakan)
        # Pastikan urutan (x, y) sesuai dengan pitch_type Anda
        player_goal_scatter = pitch.scatter(
            list(map(lambda x: 100 - x, scored_df['draw_start_y'])), 
            list(map(lambda x: 100 - x, scored_df['draw_start_x'])),
            s=(scored_df['xG'] * 900) +100,
            c=theme.VANILLA_CUSTARD,
            marker='o',
            ax=axs[0]
        )
        player_sog_scatter = pitch.scatter(
            list(map(lambda x: 100 - x, saved_df['draw_start_y'])), 
            list(map(lambda x: 100 - x, saved_df['draw_start_x'])),
            s=(saved_df['xG'] * 900) + 100,
            # c=theme.VANILLA_CUSTARD,  # no facecolor for the markers
            hatch='///',  # the all important hatch (triple diagonal lines)
            marker='o',
            edgecolor=theme.VANILLA_CUSTARD,
            ax=axs[0]
        )
        player_soffg_scatter = pitch.scatter(
            list(map(lambda x: 100 - x, missed_df['draw_start_y'])), 
            list(map(lambda x: 100 - x, missed_df['draw_start_x'])),
            s=(missed_df['xG'] * 900) +100,
            c='none',  # no facecolor for the markers
            marker='o',
            edgecolor=theme.VANILLA_CUSTARD,
            ax=axs[0]
        )
        player_blocked_scatter = pitch.scatter(
            list(map(lambda x: 100 - x, blocked_df['draw_start_y'])), 
            list(map(lambda x: 100 - x, blocked_df['draw_start_x'])),
            s=(blocked_df['xG'] * 900) + 100,
            c=theme.VANILLA_CUSTARD,
            marker='X',
            ax=axs[0]
        )
    
    stats_title = axs[1].text(0.5, 1.05, f"{home_team} vs {away_team}", 
            verticalalignment='center', 
            horizontalalignment='center', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    stats_title = axs[1].text(0.5, 1, f"{player_name} Individual Stats", 
            verticalalignment='center', 
            horizontalalignment='center', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    goal_txt = axs[1].text(0.05, 0.9, "Goal", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    goals = player_stats.get('goals', 0)
    goal_val = axs[1].text(0.45, 0.9, f"{goals}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    xG_txt = axs[1].text(0.05, 0.85, "Expected Goals", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    expectedGoals = player_stats.get('expectedGoals', 0)
    xG_val = axs[1].text(0.45, 0.85, f"{expectedGoals}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    assists_txt = axs[1].text(0.05, 0.8, "Assists", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    assists = player_stats.get('goalAssist', 0)
    assists_val = axs[1].text(0.45, 0.8, f"{assists}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    expected_assists_txt = axs[1].text(0.05, 0.75, "Expected Assists", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    expectedAssists = player_stats.get('expectedAssists', 0)
    expected_assists_val = axs[1].text(0.45, 0.75, f"{expectedAssists}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    total_shots_txt = axs[1].text(0.05, 0.7, "Total Shots", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    totalShots = player_stats.get('totalShots', 0)
    total_shots_val = axs[1].text(0.45, 0.7, f"{totalShots}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    sog_txt = axs[1].text(0.05, 0.65, "Shots On Target", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    sog = player_stats.get('onTargetScoringAttempt', 0)
    sog_val = axs[1].text(0.45, 0.65, f"{sog}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    sb_txt = axs[1].text(0.05, 0.6, "Shots Blocked", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    blockedScoringAttempt = player_stats.get('blockedScoringAttempt', 0)
    sb_txt = axs[1].text(0.45, 0.6, f"{blockedScoringAttempt}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    offside_txt = axs[1].text(0.05, 0.55, "Offside", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    totalOffside = player_stats.get('totalOffside', 0)
    offside_val = axs[1].text(0.45, 0.55, f"{totalOffside}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    touches_txt = axs[1].text(0.05, 0.45, "Touches", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    touches = player_stats.get('touches', 0)
    touches_val = axs[1].text(0.45, 0.45, f"{touches}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    dribble_txt = axs[1].text(0.05, 0.4, "Dribbles", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    wonContest = player_stats.get('wonContest', 0)
    totalContest = player_stats.get('totalContest', 0)
    dribble_val = axs[1].text(0.45, 0.4, f"{wonContest}/{totalContest}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    fouled_txt = axs[1].text(0.05, 0.35, "Was Fouled", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    wasFouled = player_stats.get('wasFouled', 0)
    fouled_val = axs[1].text(0.45, 0.35, f"{wasFouled}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    keypass_txt = axs[1].text(0.05, 0.25, "Key Pass", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    keyPass = player_stats.get('keyPass', 0)
    keypass_val = axs[1].text(0.45, 0.25, f"{keyPass}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    crosses_txt = axs[1].text(0.05, 0.2, "Crossess", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accurateCross = player_stats.get('accurateCross', 0)
    totalCross = player_stats.get('totalCross', 0)
    crosses_val = axs[1].text(0.45, 0.2, f"{accurateCross}/{totalCross}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    acc_pass_txt = axs[1].text(0.05, 0.15, "Passes", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    accuratePass = player_stats.get('accuratePass', 0)
    totalPass = player_stats.get('totalPass', 0)
    acc_pass_val = axs[1].text(0.45, 0.15, f"{accuratePass}/{totalPass}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    pass_in_opp_txt = axs[1].text(0.05, 0.1, "Pass in Opp. Half", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    accurateOppositionHalfPasses = player_stats.get('accurateOppositionHalfPasses', 0)
    totalOppositionHalfPasses = player_stats.get('totalOppositionHalfPasses', 0)
    
    pass_in_opp_val = axs[1].text(0.45, 0.1, f"{accurateOppositionHalfPasses}/{totalOppositionHalfPasses}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    pass_in_own_txt = axs[1].text(0.05, 0.05, "Pass in Own Half", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    accurateOwnHalfPasses = accuratePass - accurateOppositionHalfPasses
    totalOwnHalfPasses = totalPass - totalOppositionHalfPasses
    
    pass_in_own_val = axs[1].text(0.45, 0.05, f"{accurateOwnHalfPasses}/{totalOwnHalfPasses}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    long_ball_txt = axs[1].text(0.05, 0, "Long Ball", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    accurateLongBalls = player_stats.get('accurateLongBalls', 0)
    totalLongBalls = player_stats.get('totalLongBalls', 0)
    long_ball_val = axs[1].text(0.45, 0, f"{accurateLongBalls}/{totalLongBalls}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    tackles_txt = axs[1].text(0.55, 0.9, "Tackles", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    wonTackle = player_stats.get('wonTackle', 0)
    totalTackle = player_stats.get('totalTackle', 0)
    tackles_val = axs[1].text(0.95, 0.9, f"{wonTackle}/{totalTackle}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    interception_txt = axs[1].text(0.55, 0.85, "Interceptions", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    interceptionWon = player_stats.get('interceptionWon', 0)
    interception_val = axs[1].text(0.95, 0.85, f"{interceptionWon}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    clearances_txt = axs[1].text(0.55, 0.8, "Clearances", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    totalClearance = player_stats.get('totalClearance', 0)
    clearances_val = axs[1].text(0.95, 0.8, f"{totalClearance}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    blocked_txt = axs[1].text(0.55, 0.75, "Blocked Shots", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    outfielderBlock = player_stats.get('outfielderBlock', 0)
    blocked_val = axs[1].text(0.95, 0.75, f"{outfielderBlock}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    recoveries_txt = axs[1].text(0.55, 0.7, "Recoveries", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    ballRecovery = player_stats.get('ballRecovery', 0)
    recoveries_txt = axs[1].text(0.95, 0.7, f"{ballRecovery}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    aerial_txt = axs[1].text(0.55, 0.6, "Aerial Duels", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    aerialWon = player_stats.get('aerialWon', 0)
    aerialLost = player_stats.get('aerialLost', 0)
    aerial_val = axs[1].text(0.95, 0.6, f"{aerialWon}/{aerialLost + aerialWon}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    ground_duels_txt = axs[1].text(0.55, 0.65, "Ground Duels", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    duelWon = player_stats.get('duelWon', 0)
    duelLost = player_stats.get('duelLost', 0)
    groundDuelWon = duelWon - aerialWon
    groundDuelLost = duelLost - aerialLost
    totalGroundDuel = groundDuelWon + groundDuelLost
    ground_duels_val = axs[1].text(0.95, 0.65, f"{groundDuelWon}/{totalGroundDuel}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    fouls_txt = axs[1].text(0.55, 0.55, "Fouls", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    fouls = player_stats.get('fouls', 0)
    fouls_val = axs[1].text(0.95, 0.55, f"{fouls}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    unsuccess_touch_txt = axs[1].text(0.55, 0.45, "Unsuccessful Touch", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    unsuccessfulTouch = player_stats.get('unsuccessfulTouch', 0)
    unsuccess_touch_val = axs[1].text(0.95, 0.45, f"{unsuccessfulTouch}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    dribble_past_txt = axs[1].text(0.55, 0.4, "Dribbled Past", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    challengeLost = player_stats.get('challengeLost', 0)
    dribble_past_val = axs[1].text(0.95, 0.4, f"{challengeLost}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    error_txt = axs[1].text(0.55, 0.35, "Errors Leads To Shot", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    errorLeadToAShot = player_stats.get('errorLeadToAShot', 0)
    error_val = axs[1].text(0.95, 0.35, f"{errorLeadToAShot}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)

    possession_lost_txt = axs[1].text(0.55, 0.3, "Possession Lost", 
            verticalalignment='center', 
            horizontalalignment='left', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    possessionLostCtrl = player_stats.get('possessionLostCtrl', 0)
    possession_lost_val = axs[1].text(0.95, 0.3, f"{possessionLostCtrl}", 
            verticalalignment='center', 
            horizontalalignment='right', 
            fontsize=20, 
            transform=axs[1].transAxes,
            fontproperties=fonts.GOOGLE_SANS_FONT)
    
    return player_fig