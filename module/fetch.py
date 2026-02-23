import random
import time

from curl_cffi import requests
from pymongo import MongoClient

import constants.headers as config
import query

def match_stats(client: MongoClient, comp_id: int, season_id: int, match_ids: list[int], save_to_db=True):
    session = requests.Session()
    
    db = client['sofascore_data']
    collection = db['match_stats']
    
    final_results = [] # Untuk return fungsi
    max_retries = 3 

    for match_id in match_ids:
        # Perhatikan: hilangkan koma di ujung URL agar tidak menjadi tuple
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/statistics'
        
        match_stats_groups = None
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil match statistics {match_id} (Percobaan {attempt + 1})...", end=" ")
                
                # Gunakan response dari session
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    stats_list = data.get('statistics', [])
                    
                    # Cari grup statistik yang "ALL" (Full Time)
                    # Ini lebih aman daripada menggunakan indeks [0]
                    full_time_stats = next((s for s in stats_list if s.get('period') == 'ALL'), None)
                    
                    if full_time_stats:
                        match_stats_groups = full_time_stats.get('groups')
                        print("Berhasil.")
                        break
                    else:
                        print("Gagal: Key 'groups' tidak ditemukan.")
                        break
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        home_team_id, away_team_id = query.get_team_id(client, match_id)
        
        # Jika data berhasil diambil, proses simpan per player
        if match_stats_groups is not None:
            unique_stats = {}
            for group in match_stats_groups:
                for item in group["statisticsItems"]:
                    # Menggunakan 'key' sebagai pengidentifikasi unik
                    stat_key = item["key"]
                    if stat_key not in unique_stats:
                        unique_stats[stat_key] = item
            
            match_stats_dict = {
                'match_id': match_id,
                'comp_id': comp_id,
                'season_id': season_id, 
                'home_team_id': home_team_id, 
                'away_team_id': away_team_id, 
                'statistics': list(unique_stats.values())
            }
            
            final_results.append(match_stats_dict)

            if save_to_db:
                collection.update_one(
                        {
                            "match_id": match_stats_dict["match_id"],
                            "comp_id": match_stats_dict["comp_id"],
                            "season_id": match_stats_dict["season_id"]
                        }, # Filter unik (Player ID + Match ID)
                        {"$set": match_stats_dict}, upsert=True)
                    
                print(f"Berhasil menyimpan statistik pertandingan untuk pertandingan {match_id}.")

        time.sleep(random.uniform(1, 2))
        
    return final_results

def match_incidents(client, match_ids, save_to_db=True):
    session = requests.Session()

    db = client['sofascore_data']
    collection = db['match_incidents']

    final_results = [] 
    max_retries = 3 

    for match_id in match_ids:
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/incidents'

        match_stats_groups = None

        for attempt in range(max_retries):
            try:
                print(f"Mengambil match incidents {match_id} (Percobaan {attempt + 1})...", end=" ")

                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    incident_list = data.get('incidents', [])
                    break
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        if incident_list:
            match_incidents_dict = {
                'match_id': match_id,
                'incidents': incident_list
            }

            final_results.append(match_incidents_dict)

            if save_to_db:
                collection.update_one(
                        {"match_id": match_incidents_dict["match_id"]}, 
                        {"$set": match_incidents_dict}, upsert=True)

                print(f"Berhasil menyimpan incidents pertandingan untuk pertandingan {match_id}.")

        time.sleep(random.uniform(1, 2))

    return final_results

def player_match_stats(client: MongoClient, comp_id: int, season_id: int, match_ids: list, save_to_db=True):
    session = requests.Session()
    
    db = client['sofascore_data']
    collection = db['player_match_stats']
    
    max_retries = 3 

    for match_id in match_ids:
        # Perhatikan: hilangkan koma di ujung URL agar tidak menjadi tuple
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/lineups'
        
        home_players_data_list = []
        away_players_data_list = []
        success = False
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil player match statistics {match_id} (Percobaan {attempt + 1})...", end=" ")
                
                # Gunakan response dari session
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    impersonate='chrome120',
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    home_players_data = data.get('home', {}).get('players', [])
                    away_players_data = data.get('away', {}).get('players', [])
                    success = True
                    print("Berhasil.")
                    break
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        if not success:
            continue
        
        for home_player_data in home_players_data:
            home_player_info_dict = {
                'name': home_player_data.get('player', {}).get('name'),
                'player_id': home_player_data.get('player', {}).get('id'),
                'slug': home_player_data.get('player', {}).get('slug'),
                'position': home_player_data.get('player', {}).get('position'),
                'jerseyNumber': home_player_data.get('player', {}).get('jerseyNumber'),
                'height': home_player_data.get('player', {}).get('height'),
                'substitute': home_player_data.get('substitute'),
                'statistics': home_player_data.get('statistics', {}),
                'is_home': 1,
                'team_id': home_player_data.get('teamId'),
                'match_id': match_id,
                'comp_id': comp_id,
                'season_id': season_id
            }
            home_players_data_list.append(home_player_info_dict)

        for away_player_data in away_players_data:
            away_player_info_dict = {
                'name': away_player_data.get('player', {}).get('name'),
                'player_id': away_player_data.get('player', {}).get('id'),
                'slug': away_player_data.get('player', {}).get('slug'),
                'position': away_player_data.get('player', {}).get('position'),
                'jerseyNumber': away_player_data.get('player', {}).get('jerseyNumber'),
                'height': away_player_data.get('player', {}).get('height'),
                'substitute': away_player_data.get('substitute'),
                'statistics': away_player_data.get('statistics', {}),
                'is_home': 0,
                'team_id': away_player_data.get('teamId'),
                'match_id': match_id,
                'comp_id': comp_id,
                'season_id': season_id
            }
            away_players_data_list.append(away_player_info_dict)
        
        match_stats = home_players_data_list + away_players_data_list
        
        if save_to_db:
            saved_count = 0
            for player_stats in match_stats:
                # CEK DISINI: Hanya simpan jika statistics tidak kosong
                if player_stats.get('statistics'): 
                    collection.update_one(
                        {
                            "player_id": player_stats["player_id"], 
                            "match_id": player_stats["match_id"],
                            "season_id": player_stats["season_id"]
                        },
                        {"$set": player_stats}, 
                        upsert=True
                    )
                    saved_count += 1
            
            print(f"Berhasil menyimpan {saved_count} data pemain (mengabaikan stats kosong).")

        time.sleep(random.uniform(2.5, 4))
        
    return match_stats

def player_match_heatmap(client, match_id, player_ids, save_to_db=True):
    session = requests.Session()
    
    db = client["sofascore_data"]
    collection = db["player_match_heatmap"]
    
    final_results = [] # Untuk return fungsi
    failed_players = []
    max_retries = 3 

    print(f'Mengambil heatmap untuk pertandingan {match_id}')
    
    for player_id in player_ids:
        # Perhatikan: hilangkan koma di ujung URL agar tidak menjadi tuple
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/player/{player_id}/heatmap'
        
        heatmap_points = None
        success = False
        
        resp = None
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil heatmap player {player_id} (Percobaan {attempt + 1})...", end=" ")
                
                # Gunakan response dari session
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    heatmap_points = data.get('heatmap', [])
                    print("Berhasil.")
                    success = True ### Tandai berhasil
                    break 
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 3
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        if not success and resp.status_code != 404:
            failed_players.append({
                'player_id': player_id,
                'match_id': match_id,
                'last_error': f"Status {resp.status_code}" if 'resp' in locals() else "Connection Error"
            })
        
        # Jika data berhasil diambil, proses simpan per player
        if heatmap_points is not None:
            player_data = {
                'player_id': player_id,
                'match_id': match_id,
                'heatmap': heatmap_points,
            }
            
            final_results.append(player_data)

            if save_to_db:
                # Simpan langsung di dalam loop agar jika error di tengah, data sebelumnya aman
                collection.update_one(
                    {
                        "player_id": player_id, 
                        "match_id": match_id
                    }, 
                    {"$set": player_data}, 
                    upsert=True
                )
    
    print(f"\nSelesai. Total data sukses: {len(final_results)}")
    if failed_players:
        print(f"TOTAL GAGAL: {len(failed_players)}")
        for f in failed_players:
            print(f"  - Player {f['player_id']} di Match {f['match_id']} (Gagal setelah {max_retries}x percobaan)")
    
    return final_results, failed_players

def player_match_action(client, match_id, player_id, save_to_db=True):
    # Memilih database dan collection
    db = client["sofascore_data"]
    collection = db["player_match_action"]
    
    player_heatmap_resp = requests.get(
        f'https://www.sofascore.com/api/v1/event/{match_id}/player/{player_id}/rating-breakdown',
        headers=config.SS_HEADERS,
        impersonate="chrome120", 
        timeout=30
        )

    data = player_heatmap_resp.json()
                    
    # Simpan semua poin aksi ke dalam satu dictionary
    player_action_data = {
        'player_id': player_id,
        'match_id': match_id,
        'passing': data.get('passes', []),
        'dribble': data.get('dribbles', []),
        'defensive': data.get('defensive', []),
        'ball_carries': data.get('ball-carries', []),
        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
        }

    if save_to_db:
        collection.update_one(
            {
                "player_id": player_id, 
                "match_id": match_id
            }, 
            {
                "$set": player_action_data
            }, 
                upsert=True)
    
    return player_action_data

def all_player_match_action(client, match_id, player_ids, save_to_db=True):
    session = requests.Session()
    
    db = client["sofascore_data"]
    collection = db["player_match_action"]
    
    final_results = []
    max_retries = 3 

    for player_id in player_ids:
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/player/{player_id}/rating-breakdown'
        
        # Inisialisasi data sebagai None untuk mengecek keberhasilan fetch
        player_action_data = None
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil data aksi player {player_id} (Percobaan {attempt + 1})...", end=" ")
                
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS,
                    impersonate="chrome120",
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Simpan semua poin aksi ke dalam satu dictionary
                    player_action_data = {
                        'player_id': player_id,
                        'match_id': match_id,
                        'passing': data.get('passes', []),
                        'dribble': data.get('dribbles', []),
                        'defensive': data.get('defensive', []),
                        'ball_carries': data.get('ball-carries', []),
                        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    print("Berhasil.")
                    break 
                
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        # Jika data berhasil diambil (tidak None)
        if player_action_data:
            final_results.append(player_action_data)

            if save_to_db:
                collection.update_one(
                    {
                        "player_id": player_id, 
                        "match_id": match_id
                    }, 
                    {"$set": player_action_data}, 
                    upsert=True
                )
        
        # Tambahkan delay kecil antar pemain agar lebih sopan terhadap server
        time.sleep(0.5)
    
    print(f"\nSelesai. Total data aksi diproses: {len(final_results)}")
    return final_results

# Finished
def match_round(client: MongoClient, comp_id: int, season_id: int, save_to_db=True):
    db = client['sofascore_data']
    collection = db['matches']

    next_round, scraped_round = query.get_rounds(client, comp_id, season_id)
    
    url = f'https://www.sofascore.com/api/v1/unique-tournament/{comp_id}/season/{season_id}/events/round/{next_round}'
    matches_resp = requests.get(
        url, 
        headers=config.SS_HEADERS, 
        impersonate="chrome120", 
        timeout=30
    )
    
    if matches_resp.status_code != 200:
        print(f"Gagal mengambil data: Status {matches_resp.status_code}")
        return []

    matches_data = matches_resp.json().get('events', [])
    matches_datalist = []

    for match_data in matches_data:
        if match_data.get('status').get('type') == 'finished':
            # Mapping data pertandingan
            matches_dict = {
                'match_id': match_data.get('id'),
                'comp_name': match_data.get('season', {}).get('name'),
                'comp_id': match_data.get('tournament', {}).get('uniqueTournament', {}).get('id'),
                'comp_season': match_data.get('season', {}).get('year'),
                'season_id': match_data.get('season', {}).get('id'),
                'round': match_data.get('roundInfo', {}).get('round'),
                'comp_status_desc': match_data.get('status', {}).get('description'),
                'comp_status_type': match_data.get('status', {}).get('type'),
                'home_team': match_data.get('homeTeam', {}).get('name'),
                'home_team_id': match_data.get('homeTeam', {}).get('id'),
                'home_team_colors': match_data.get('homeTeam', {}).get('teamColors'),
                'home_score': match_data.get('homeScore', {}).get('display'),
                'away_team': match_data.get('awayTeam', {}).get('name'),
                'away_team_id': match_data.get('awayTeam', {}).get('id'),
                'away_team_colors': match_data.get('awayTeam', {}).get('teamColors'),
                'away_score': match_data.get('awayScore', {}).get('display'),
            }
            
        else:
            matches_dict = {
                'match_id': match_data.get('id'),
                'comp_name': match_data.get('season', {}).get('name'),
                'comp_id': match_data.get('tournament', {}).get('id'),
                'comp_season': match_data.get('season', {}).get('year'),
                'season_id': match_data.get('season', {}).get('id'),
                'round': match_data.get('roundInfo', {}).get('round'),
                'comp_status_desc': match_data.get('status', {}).get('description'),
                'comp_status_type': match_data.get('status', {}).get('type'),
                'home_team': match_data.get('homeTeam', {}).get('name'),
                'home_team_id': match_data.get('homeTeam', {}).get('id'),
                'away_team': match_data.get('awayTeam', {}).get('name'),
                'away_team_id': match_data.get('awayTeam', {}).get('id'),
            }
            
        if save_to_db:
            # Perbaikan: Menggunakan match_id sebagai filter unik
            collection.update_one(
                {"match_id": matches_dict["match_id"]}, 
                {"$set": matches_dict}, 
                upsert=True
            )
            
        matches_datalist.append(matches_dict)

    
    print(f"Berhasil memproses {len(matches_datalist)} pertandingan untuk round {next_round}.")
    
    return matches_datalist

# Finished
def all_round_finished_match(client, comp_id, season_id, save_to_db=True):
    db = client['sofascore_data']
    collection = db['matches']
    
    # Gunakan session agar koneksi TCP lebih stabil (reuse connection)
    session = requests.Session()

    all_matches_data = []
    max_retries = 3  # Jumlah percobaan jika terjadi connection reset
    
    round_num = 1
    while True:
        url = f'https://www.sofascore.com/api/v1/unique-tournament/{comp_id}/season/{season_id}/events/round/{round_num}'
        success = False
        not_found = False

        for attempt in range(max_retries):
            try:
                print(f"Mengambil Round {round_num} (Percobaan {attempt + 1})...", end=" ")
                resp = session.get(url, headers=config.SS_HEADERS, impersonate="chrome120", timeout=30)

                if resp.status_code == 200:
                    all_matches_data.append(resp.json()['events'])
                    print("Berhasil.")
                    success = True
                    break # Keluar dari loop retry karena berhasil

                elif resp.status_code == 404:
                    print("Gagal: 404. Data tidak tersedia. Menghentikan scraping ronde.")
                    not_found = True # Sinyal bahwa ronde sudah habis
                    break # Keluar dari loop retry

                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 3
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        # CEK APAKAH HARUS BERHENTI TOTAL
        if not_found:
            # Jika ketemu 404, kita langsung keluar dari 'while True'
            break

        if not success:
            print(f"Gagal mengambil Round {round_num} setelah {max_retries} kali percobaan. Lanjut?")
            # Di sini kamu bisa pilih mau 'break' atau 'continue' ke ronde berikutnya
            break 

        # JIKA BERHASIL, LANJUT KE RONDE BERIKUTNYA
        round_num += 1
        time.sleep(random.uniform(3.5, 7.0))

    print(f"Scraping selesai. Total ronde yang didapat: {round_num - 1}")

    print(f"Total data: {len(all_matches_data)} rounds.")

    matches_datalist = []

    for matches_data in all_matches_data:
        for match_data in matches_data:
            if match_data.get('status').get('type') == 'finished':
                matches_dict = {
                    'match_id': match_data.get('id'),
                    'comp_name': match_data.get('season').get('name'),
                    'comp_id': match_data.get('tournament').get('uniqueTournament').get('id'),
                    'comp_season': match_data.get('season').get('year'),
                    'season_id': match_data.get('season').get('id'),
                    'round': match_data.get('roundInfo').get('round'),
                    'comp_status_desc': match_data.get('status').get('description'),
                    'comp_status_type': match_data.get('status').get('type'),
                    'home_team': match_data.get('homeTeam').get('name'),
                    'home_team_id': match_data.get('homeTeam').get('id'),
                    'home_team_colors': match_data.get('homeTeam').get('teamColors'),
                    'home_score': match_data.get('homeScore', {}).get('display'),
                    'away_team': match_data.get('awayTeam').get('name'),
                    'away_team_id': match_data.get('awayTeam').get('id'),
                    'away_team_colors': match_data.get('awayTeam').get('teamColors'),
                    'away_score': match_data.get('awayScore', {}).get('display'),
                }

                if save_to_db:
                    # Perbaikan: Menggunakan match_id sebagai filter unik
                    collection.update_one(
                        {"match_id": matches_dict["match_id"]}, 
                        {"$set": matches_dict}, 
                        upsert=True
                    )
                
                matches_datalist.append(matches_dict)
                
    return matches_datalist

# Finished

def team_in_comp(client, comp_id, season_id, save_to_db=True):
    db = client['sofascore_data']
    collection = db['teams']
    
    # Library ini akan meniru perilaku Chrome secara identik
    team_resp = requests.get(
        f'https://www.sofascore.com/api/v1/unique-tournament/{comp_id}/season/{season_id}/teams', 
        headers=config.SS_HEADERS, 
        impersonate="chrome120", # Meniru TLS Chrome 120
        timeout=30
    )

    data = team_resp.json()
    team_list = data.get('teams', [])
    
    for team in team_list:
        team_id = team.get('id')
        team_name = team.get('name')
        team_slug = team.get('slug')
        team_name_code = team.get('nameCode')
        team_type = team.get('type')
        country = team.get('country')
        team_colors = team.get('teamColors')
        
        teams_entry = {
            'team_id': team_id,
            'team_name': team_name,
            'team_slug': team_slug,
            'team_name_code': team_name_code,
            'team_type': team_type,
            'country': country,
            'team_colors': team_colors,
            'team_logo': f'https://img.sofascore.com/api/v1/team/{team_id}/image' 
        }
            
        # 3. Penyimpanan Database
        if save_to_db:
            collection.update_one(
                {"team_id": team_id},
                {"$set": teams_entry}, 
                upsert=True
            )
            print(f"Berhasil menyimpan tim {team_id}.")
    
    return teams_entry

def player_in_team(client: MongoClient, team_id: int, save_to_db: bool = True):
    db = client['sofascore_data']
    collection = db['players']
    
    try:
        resp = requests.get(
            f'https://www.sofascore.com/api/v1/team/{team_id}/players',
            headers=config.SS_HEADERS,
            impersonate="chrome120", 
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error saat mengambil data: {e}")
        return []

    player_list = data.get('players', [])
    cleaned_players = []
    
    for item in player_list:
        # Sofascore membungkus info pemain di dalam key 'player'
        player_info = item.get('player', {})
        
        # 1. Hapus key yang tidak diinginkan
        keys_to_remove = ['firstName', 'lastName', 'team', 'fieldTranslations']
        for key in keys_to_remove:
            player_info.pop(key, None)

        # 2. Tambahkan metadata team_id agar tahu pemain ini dari tim mana
        player_info['current_team_id'] = team_id

        # 3. Penyimpanan Database
        if save_to_db and player_info.get('id'):
            collection.update_one(
                {"id": player_info['id']}, # Filter berdasarkan ID unik pemain
                {"$set": player_info}, 
                upsert=True
            )
            print(f"Berhasil update player: {player_info.get('name')} ({player_info.get('id')})")
        
        cleaned_players.append(player_info)
    
    return cleaned_players

def players_in_all_team(client, team_ids, save_to_db=True):
    session = requests.Session()
    db = client['sofascore_data']
    collection = db['players']
    
    final_output = [] 
    max_retries = 3 

    for team_id in team_ids:
        url = f'https://www.sofascore.com/api/v1/team/{team_id}/players'
        success = False
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil players dari tim {team_id} (Percobaan {attempt + 1})...", end=" ")
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    impersonate='chrome120', # Fitur curl_cffi
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    player_list = data.get('players', [])
                    
                    if player_list:
                        success = True
                        print("Berhasil.")
                    else:
                        print("Data kosong.")
                    break
                
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        # Skip jika gagal atau data benar-benar kosong
        if not success:
            continue

        for item in player_list:
            # Sofascore membungkus info pemain di dalam key 'player'
            player_info = item.get('player', {})
            
            # 1. Hapus key yang tidak diinginkan
            keys_to_remove = ['firstName', 'lastName', 'team', 'fieldTranslations']
            for key in keys_to_remove:
                player_info.pop(key, None)

            # 2. Tambahkan metadata team_id agar tahu pemain ini dari tim mana
            player_info['current_team_id'] = team_id

            # 3. Penyimpanan Database
            if save_to_db and player_info.get('id'):
                collection.update_one(
                    {"id": player_info['id']}, # Filter berdasarkan ID unik pemain
                    {"$set": player_info}, 
                    upsert=True
                )
                print(f"Berhasil update player: {player_info.get('name')} ({player_info.get('id')})")
            
            final_output.append(player_info)

        # Anti-Bot Delay yang lebih natural
        time.sleep(random.uniform(2.0, 3.0))
    
    return final_output

def comps_info(client, comp_id, season_id, save_to_db=True):
    db = client['sofascore_data']
    collection = db['comps']
    
    # 1. Ambil data Seasons
    try:
        print(f"Mengambil data seasons untuk kompetisi {comp_id}...")
        seasons_resp = requests.get(
            f'https://www.sofascore.com/api/v1/unique-tournament/{comp_id}/seasons',
            headers=config.SS_HEADERS, 
            impersonate='chrome120',
            timeout=30
        )
        seasons_resp.raise_for_status()
        seasons_data = seasons_resp.json().get('seasons', [])
    except Exception as e:
        print(f"Gagal mengambil seasons: {e}")
        return None

    # --- JEDA ANTAR API ---
    # Memberikan jeda acak agar tidak terdeteksi bot
    wait_time = random.uniform(1.0, 2.0)
    print(f"Menunggu {wait_time:.2f} detik sebelum mengambil data tim...")
    time.sleep(wait_time)

    # 2. Ambil data Teams
    try:
        print(f"Mengambil data tim untuk season {season_id}...")
        teams_resp = requests.get(
            f'https://www.sofascore.com/api/v1/unique-tournament/{comp_id}/season/{season_id}/teams', 
            headers=config.SS_HEADERS, 
            impersonate='chrome120',
            timeout=30
        )
        teams_resp.raise_for_status()
        teams_data = teams_resp.json().get('teams', [])
    except Exception as e:
        print(f"Gagal mengambil teams: {e}")
        teams_data = []

    final_teams_data = []
    for team_data in teams_data:
        team_dict = {
            'team_name': team_data.get('name'),
            'team_id': team_data.get('id'),
        }
        final_teams_data.append(team_dict)
    
    
    # 3. Gabungkan data
    for season in seasons_data:
        if season.get('id') == int(season_id):
            final_entry = {
                'season_id': season_id,
                'comp_id': comp_id,
                'comp_name': season.get('name'),
                'year': season.get('year'),
                'teams': final_teams_data,
            }
            break

    # 4. Simpan ke Database (opsional)
    if save_to_db:
        collection.update_one(
            {"season_id": season_id}, 
            {"$set": final_entry}, 
            upsert=True
        )
        print(f"Berhasil menyimpan info kompetisi/season {season_id} ke DB.")

    return final_entry

def match_lineups(client: MongoClient, match_ids: list[str | int], save_to_db=True):
    # Gunakan session dari curl_cffi dengan benar
    session = requests.Session()
    db = client['sofascore_data']
    collection = db['match_lineups']
    
    final_output = [] 
    max_retries = 3 

    for match_id in match_ids:
        # Endpoints Sofascore berbeda untuk lineups dan incidents
        url_lineups = f'https://www.sofascore.com/api/v1/event/{match_id}/lineups'
        url_incidents = f'https://www.sofascore.com/api/v1/event/{match_id}/incidents'
        
        success = False
        data_lineups = {}
        data_incidents = {}

        for attempt in range(max_retries):
            try:
                print(f"Mengambil data match {match_id} (Percobaan {attempt + 1})...", end=" ")
                
                # 1. Ambil Lineups
                resp_l = session.get(url_lineups, headers=config.SS_HEADERS, impersonate='chrome120', timeout=30)
                # 2. Ambil Incidents (Substitusi ada di sini)
                resp_i = session.get(url_incidents, headers=config.SS_HEADERS, impersonate='chrome120', timeout=30)

                if resp_l.status_code == 200 and resp_i.status_code == 200:
                    data_lineups = resp_l.json()
                    data_incidents = resp_i.json()
                    success = True
                    print("Berhasil.")
                    break
                else:
                    print(f"Gagal status: L:{resp_l.status_code} I:{resp_i.status_code}")
                    if resp_l.status_code == 404: break # Jika 404 jangan retry
                
            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time}s...")
                time.sleep(wait_time)

        if not success:
            continue

        # Proses Lineups (Home & Away)
        teams = ['home', 'away']
        processed_data = {}

        for team in teams:
            team_data = data_lineups.get(team, {})
            players = team_data.get('players', [])
            
            starting = []
            bench = []
            
            for p in players:
                player_info = {
                    'name': p.get('player', {}).get('name'),
                    'id': p.get('player', {}).get('id'),
                    'position': p.get('player', {}).get('position'),
                    'jerseyNumber': p.get('jerseyNumber')
                }
                if p.get('substitute') is False:
                    starting.append(player_info)
                else:
                    bench.append(player_info)
            
            processed_data[f'{team}_starting'] = starting
            processed_data[f'{team}_bench'] = bench
            processed_data[f'{team}_formation'] = team_data.get('formation', '')

        # Proses Substitusi (dari incidents)
        home_subs = []
        away_subs = []
        incidents = data_incidents.get('incidents', [])

        for inc in incidents:
            # PERBAIKAN: Gunakan 'and', bukan '&' (bitmask)
            if inc.get('incidentType') == 'substitution':
                sub_data = {
                    'player_in_name': inc.get('playerIn', {}).get('name'),
                    'player_in_id': inc.get('playerIn', {}).get('id'),
                    'player_out_name': inc.get('playerOut', {}).get('name'),
                    'player_out_id': inc.get('playerOut', {}).get('id'),
                    'time': inc.get('time'),
                    'is_home': inc.get('isHome')
                }
                if inc.get('isHome'):
                    home_subs.append(sub_data)
                else:
                    away_subs.append(sub_data)

        # Gabungkan semua
        lineup_entry = {
            'match_id': match_id,
            **processed_data,
            'home_subs': home_subs,
            'away_subs': away_subs,
            'last_updated': time.time()
        }
        
        final_output.append(lineup_entry)
        
        if save_to_db:
            collection.update_one(
                {"match_id": match_id},
                {"$set": lineup_entry}, 
                upsert=True
            )

        time.sleep(random.uniform(1.5, 2.5))
    
    return final_output

def match_shotmaps(client: MongoClient, match_ids: list[int], save_to_db=True):
    session = requests.Session()
    db = client['sofascore_data']
    collection = db['match_shotmaps']

    # 1. Pindahkan ke luar loop agar data terkumpul dari semua match_ids
    final_output = [] 
    max_retries = 3 

    for match_id in match_ids:
        url = f'https://www.sofascore.com/api/v1/event/{match_id}/shotmap'

        match_shotmaps = []
        success = False

        for attempt in range(max_retries):
            try:
                print(f"Mengambil match shotmaps {match_id} (Percobaan {attempt + 1})...", end=" ")
                resp = session.get(
                    url, 
                    headers=config.SS_HEADERS, 
                    impersonate='chrome120',
                    timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    # Sofascore return list di dalam key 'shotmap'
                    match_shotmaps = data.get('shotmap', [])
                    success = True
                    print("Berhasil.")
                    break
                elif resp.status_code == 404:
                    print("Data tidak tersedia (404).")
                    break
                else:
                    print(f"Gagal status {resp.status_code}")

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"Error: {e}. Menunggu {wait_time} detik...")
                time.sleep(wait_time)

        if not success or not match_shotmaps:
            continue

        shotmaps_list = []
        for match_shotmap in match_shotmaps:
            shotmap_data = {
                'player_name': match_shotmap.get('player', {}).get('name'),
                'player_id': match_shotmap.get('player', {}).get('id'),
                'player_pos': match_shotmap.get('player', {}).get('position'),
                'player_num': match_shotmap.get('player', {}).get('jerseyNumber'),
                'is_home': match_shotmap.get('isHome'),
                'shot_type': match_shotmap.get('shotType'),
                'goal_type': match_shotmap.get('goalType'),
                'situation': match_shotmap.get('situation'),
                'body_part': match_shotmap.get('bodyPart'),
                'goal_mouth_location': match_shotmap.get('goalMouthLocation'),
                'xg': match_shotmap.get('xg', 0),
                'xgot': match_shotmap.get('xgot', 0),
                'time': match_shotmap.get('time', 0),
                'added_time': match_shotmap.get('addedTime', 0),
                'player_coor': match_shotmap.get('playerCoordinates', {}),
                'goal_mouth_coor': match_shotmap.get('goalMouthCoordinates', {}),
                'block_coor': match_shotmap.get('blockCoordinates', {}),
                'draw': match_shotmap.get('draw', {}),
            }
            shotmaps_list.append(shotmap_data)
        
        query.update_player_shots(client, match_id, shotmaps_list)
        
        shotmap_entry = {
            'match_id': match_id,
            'shotmap': shotmaps_list,
            'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        final_output.append(shotmap_entry)

        # 3. Penyimpanan Database
        if save_to_db:
            collection.update_one(
                {"match_id": match_id},
                {"$set": shotmap_entry}, 
                upsert=True
            )
            print(f"Berhasil menyimpan {len(shotmaps_list)} tembakan untuk match {match_id}.")

        # Anti-Bot Delay
        time.sleep(random.uniform(2.5, 4.0))

    return final_output