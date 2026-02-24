from pymongo import MongoClient
import pandas as pd

def get_comp_manual(client):
    db = client["sofascore_data"]
    collection = db["comp_manual_data"]
    
    # Ambil semua data dari koleksi
    cursor = collection.find({}, {"_id": 0, "comp_name": 1, "comp_id": 1})
    data_mongo = list(cursor)

    # Konversi kembali ke format Dictionary sederhana
    # { 'Nama Liga': ID }
    data_final = {item["comp_name"]: item["comp_id"] for item in data_mongo}

    return data_final

def get_comp_seasons(client, comp_id):
    db = client["sofascore_data"]
    collection = db["comps"]
    
    # Ambil semua data dari koleksi
    cursor = collection.find({'comp_id': comp_id}, {"_id": 0, "year": 1, "season_id": 1})
    data_mongo = list(cursor)

    # Konversi kembali ke format Dictionary sederhana
    # { 'Nama Liga': ID }
    data_final = {item["year"]: item["season_id"] for item in data_mongo}

    return data_final

def get_comp_season_id(client):
    db = client["sofascore_data"]
    collection = db["comps"]
    
    # Ambil semua data dari koleksi
    cursor = collection.find({}, {"_id": 0, "comp_id": 1, "season_id": 1})
    data_mongo = list(cursor)

    # Konversi kembali ke format Dictionary sederhana
    # { 'Nama Liga': ID }
    data_final = {item["comp_id"]: item["season_id"] for item in data_mongo}

    return data_final

def get_teams_comp(client, comp_id, season_id):
    db = client["sofascore_data"]
    collection = db["comps"]
    
    # Ambil semua data dari koleksi
    data = collection.find_one({'comp_id': comp_id, 'season_id': season_id}, {"_id": 0, "teams": 1})
    teams_data = data.get('teams')

    # Konversi kembali ke format Dictionary sederhana
    # { 'Nama Liga': ID }
    data_final = {item["team_name"]: item["team_id"] for item in teams_data}

    return data_final

def get_matches_by_team(client, comp_id, season_id, team_id):
    db = client["sofascore_data"]
    collection = db["matches"]

    query = {
        'comp_id': comp_id,
        'season_id': season_id,
        '$or': [
            {'home_team_id': team_id},
            {'away_team_id': team_id}
        ]
    }
    
    # 1. Ambil data dan langsung ubah menjadi list agar bisa diiterasi berulang kali
    matches_list = list(collection.find(query, {"_id": 0, "home_team": 1, "away_team": 1, "match_id": 1}))

    # 2. Buat dictionary final { 'Nama Pertandingan': ID }
    # Kita bisa menggabungkan proses pembuatan string 'vs' langsung di sini
    data_final = {
        f"{item['home_team']} vs {item['away_team']}": item["match_id"] 
        for item in matches_list
    }

    return data_final

def get_match_player(client, match_id):
    db = client["sofascore_data"]
    collection = db["player_match_stats"]

    query = {
        "match_id": match_id,
        "statistics": {"$exists": True, "$ne": {}},
        "position": {"$ne": "G"}
    }
    
    # 1. Ambil data dan langsung ubah menjadi list agar bisa diiterasi berulang kali
    player_list = list(collection.find(query, {"_id": 0, "name": 1, "player_id": 1, 'is_home': 1}))

    home_players = []
    away_players = []
    for player in player_list:
        if player.get('is_home') == 1:
            home_players.append(player)
        else:
            away_players.append(player)

    # 2. Buat dictionary final { 'Nama Pertandingan': ID }
    # Kita bisa menggabungkan proses pembuatan string 'vs' langsung di sini
    home_player_final = {item["name"]: item["player_id"] for item in home_players}
    away_player_final = {item["name"]: item["player_id"] for item in away_players}

    return home_player_final, away_player_final

def get_match_gk(client, match_id):
    db = client["sofascore_data"]
    collection = db["player_match_stats"]

    query = {
        "match_id": match_id,
        "statistics": {"$exists": True, "$ne": {}},
        "position": "G"
    }
    
    # 1. Ambil data dan langsung ubah menjadi list agar bisa diiterasi berulang kali
    player_list = list(collection.find(query, {"_id": 0, "name": 1, "player_id": 1, 'is_home': 1}))

    home_gks = []
    away_gks = []
    for player in player_list:
        if player.get('is_home') == 1:
            home_gks.append(player)
        else:
            away_gks.append(player)

    # 2. Buat dictionary final { 'Nama Pertandingan': ID }
    # Kita bisa menggabungkan proses pembuatan string 'vs' langsung di sini
    home_gk_final = {item["name"]: item["player_id"] for item in home_gks}
    away_gk_final = {item["name"]: item["player_id"] for item in away_gks}

    return home_gk_final, away_gk_final

def get_match_player_ids(client, match_id):
    db = client["sofascore_data"]
    collection = db['player_match_stats']

    query_hasil = collection.find(
        {"match_id": match_id}, 
        {"player_id": 1, "_id": 0}
    )

    # Kondisi jika match_id tidak ditemukan atau list kosong
    if not query_hasil:
        print(f"Peringatan: Tidak ada data ditemukan untuk match_id {match_id}")
        return [] # Kembalikan list kosong

    # Ekstrak ID menggunakan list comprehension (lebih bersih)
    player_ids = [player['player_id'] for player in query_hasil]
    
    return player_ids

def get_match_ids(client, comp_id, season_id):
    db = client["sofascore_data"]
    collection = db['matches']
    
    query = collection.find(
        {
            "comp_id": comp_id,
            "season_id": season_id
        }, 
        {
            "match_id": 1, 
            "_id": 0
        }
    )
    
    match_ids = [match['match_id'] for match in query]
    
    return match_ids

def get_match_by_player_id(client, player_id):
    db = client['sofascore_data']
    collection = db['player_match_stats']

    query = {
        'player_id': player_id
    }

    filter = {
        '_id': 0, 'match_id': 1
    }

    cursor = collection.find(query, filter)
    data = [match['match_id'] for match in cursor]
    
    return data

def get_matches_by_list_player_id(client, player_ids):
    db = client['sofascore_data']
    collection = db['player_match_stats']

    # 1. Query menggunakan $in untuk efisiensi
    query = {'player_id': {'$in': player_ids}}
    
    # Ambil player_id juga agar kita bisa mengelompokkannya
    projection = {'_id': 0, 'player_id': 1, 'match_id': 1}

    cursor = collection.find(query, projection)

    # 2. Kelompokkan match_id berdasarkan player_id menggunakan dictionary
    grouped_data = {}
    for item in cursor:
        p_id = item['player_id']
        m_id = item['match_id']
        
        if p_id not in grouped_data:
            grouped_data[p_id] = []
        
        # Hindari duplikat match_id untuk pemain yang sama jika perlu
        if m_id not in grouped_data[p_id]:
            grouped_data[p_id].append(m_id)

    # 3. Ubah format dictionary menjadi list of dictionaries sesuai permintaan
    result = [
        {'player_id': p_id, 'match_ids': m_ids} 
        for p_id, m_ids in grouped_data.items()
    ]
    
    return result

# Finished
def get_team_id(client, match_id):
    db = client["sofascore_data"]
    collection = db['matches']
    
    query = collection.find(
        {
            "match_id": match_id
        }, 
        {
            "home_team_id": 1, 
            "away_team_id": 1, 
            "_id": 0
        }
    )
    
    home_team_id = None
    away_team_id = None
    
    for match in query:
        home_team_id = match['home_team_id']
        away_team_id = match['away_team_id']
    
    return home_team_id, away_team_id

# Finished
def get_season_ball_possession(client: MongoClient, comp_id: str | int, season_id: str | int, team_id: str | int):
    db = client['sofascore_data']
    collection = db['match_stats']
    
    query = {
        'comp_id': comp_id,
        'season_id': season_id,
        '$or': [
            {'home_team_id': team_id},
            {'away_team_id': team_id}
        ]
    }

    query_result = collection.find(query)
    
    possession_list = []

    for match in query_result:
        match_id = match.get('match_id')
        is_home = match.get('home_team_id') == team_id
        
        # Masuk ke dalam list statistics
        for group in match.get('statistics', []):
            # Kita hanya butuh grup 'Match overview'
            if group.get('groupName') == "Match overview":
                for item in group.get('statisticsItems', []):
                    # Cari key ballPossession
                    if item.get('key') == "ballPossession":
                        # Ambil nilai berdasarkan posisi tim (Home/Away)
                        val = item.get('homeValue') if is_home else item.get('awayValue')
                        
                        possession_list.append({
                            'match_id': match_id,
                            'team_id': team_id,
                            'is_home': is_home,
                            'possession': val
                        })
                        break # Keluar dari statisticsItems jika sudah ketemu
                break # Keluar dari statistics group jika sudah ketemu

    return possession_list

# Finished 
def get_season_xg(client: MongoClient, comp_id: str | int, season_id: str | int, team_id: str | int):
    db = client['sofascore_data']
    collection = db['match_stats']
    
    query = {
        'comp_id': comp_id,
        'season_id': season_id,
        '$or': [
            {'home_team_id': team_id},
            {'away_team_id': team_id}
        ]
    }

    query_result = collection.find(query)
    
    xg_list = []

    for match in query_result:
        match_id = match.get('match_id')
        is_home = match.get('home_team_id') == team_id
        
        # Masuk ke dalam list statistics
        for group in match.get('statistics', []):
            # Kita hanya butuh grup 'Match overview'
            if group.get('groupName') == "Match overview":
                for item in group.get('statisticsItems', []):
                    # Cari key expectedGoals
                    if item.get('key') == "expectedGoals":
                        # Ambil nilai berdasarkan posisi tim (Home/Away)
                        val = item.get('homeValue') if is_home else item.get('awayValue')
                        
                        xg_list.append({
                            'match_id': match_id,
                            'team_id': team_id,
                            'is_home': is_home,
                            'xG': val
                        })
                        break # Keluar dari statisticsItems jika sudah ketemu
                break # Keluar dari statistics group jika sudah ketemu

    return xg_list

def get_goals_stats(client:MongoClient, comp_id: str | int, season_id: str | int, player_id: str | int):
    db = client['sofascore_data']
    collection = db['player_match_stats']
    
    query = {
        'comp_id': comp_id,
        'season_id': season_id,
        'player_id': player_id,
    }
    
    query_result = collection.find(query)
    
    player_stats_list = []
    
    for player_match_stats in query_result:
        player_stats = player_match_stats.get('statistics', {})
        player_stats_dict = {
            'goals': player_stats.get('goals', 0),
            'expectedGoals': player_stats.get('expectedGoals', 0),
            'totalShots': player_stats.get('totalShots', 0),
            'minutesPlayed': player_stats.get('minutesPlayed', 0),
        }
        player_stats_list.append(player_stats_dict)
        
    return player_stats_list

def get_player_heatmap(client, match_id, player_id):
    db = client['sofascore_data']
    collection = db['player_match_heatmap']
    
    query = {
        'match_id': match_id,
        'player_id': player_id
    }
    
    query_result = collection.find(query)
    
    x_points = []
    y_points = []
    
    for result in query_result:
        player_heatmap = result.get('heatmap', {})
        
        for heatmap_point in player_heatmap:
            x_points.append(heatmap_point.get('x'))
            y_points.append(heatmap_point.get('y'))
            
    return x_points, y_points

def get_match_name(client, match_id):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = {
        'match_id': match_id
    }
    
    query_res= collection.find(query)
    
    for result in query_res:
        comp_name = result.get('comp_name')
        home_team = result.get('home_team')
        away_team = result.get('away_team')
        res_string = f'{comp_name} - {home_team} vs {away_team}'
    
    return res_string

def get_matchId_season_by_round(client: MongoClient, season_id, round_num):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = {
        'season_id': season_id,
        'round': round_num,
    }
    
    query_res = collection.find(query)
    
    match_ids = []
    
    for result in query_res:
        match_id = result.get('match_id')
        match_ids.append(match_id)
    
    return match_ids

def get_match_ids_per_round(client: MongoClient, comp_id: str | int, season_id: str | int, round_num: int):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = {
        'comp_id': comp_id,
        'season_id': season_id,
        'round': round_num,
    }
    
    query_res = collection.find(query)
    
    match_ids = []
    
    for match_data in query_res:
        match_id = match_data.get('match_id', None)
        match_ids.append(match_id)
        
    return match_ids

def get_teams_id(client, comp_id, season_id):
    db = client['sofascore_data']
    collection = db['comps']
    
    query = {
        'comp_id': comp_id,
        'id': season_id,
    }
    
    query_res = collection.find(query)
    
    team_ids = []
    
    for res in query_res:
        for team in res.get('teams'):
            team_ids.append(team.get('team_id'))
            
    return team_ids

def get_player_name(client, player_id):
    db = client['sofascore_data']
    collection = db['players']
    
    query = {
        'id': player_id
    }
    
    query_res = collection.find(query)
    
    for res in query_res:
        name_str = res.get('name')
    
    return name_str

def get_match_shotmaps(client, match_id):
    db = client['sofascore_data']
    collection = db['match_shotmaps']
    
    query = {
        'match_id': match_id
    }
    
    query_res = collection.find_one(query)
    
    shotmaps_list = []
    for shotmap in query_res.get('shotmap'):
        shotmap_data = {
            'player_name': shotmap.get('player_name'),
            'player_pos': shotmap.get('player_pos'),
            'player_num': shotmap.get('player_num'),
            'is_home': shotmap.get('is_home'),
            'shot_type': shotmap.get('shot_type'),
            'goal_type': shotmap.get('goal_type', 'none'),
            'situation': shotmap.get('situation', 'none'),
            'body_part': shotmap.get('body_part', 'none'),
            'goal_mouth_location': shotmap.get('goal_mouth_location'),
            'body_part': shotmap.get('body_part'),
            'xG': shotmap.get('xg'),
            'xGOT': shotmap.get('xgot'),
            'time': shotmap.get('time'),
            'added_time': shotmap.get('addedTime'),
            'player_coord_x': shotmap.get('player_coor').get('x'),
            'player_coord_y': shotmap.get('player_coor').get('y'),
            'player_coord_z': shotmap.get('player_coor').get('z'),
            'goal_mouth_coord_x': shotmap.get('goal_mouth_coor').get('x'),
            'goal_mouth_coord_y': shotmap.get('goal_mouth_coor').get('y'),
            'goal_mouth_coord_z': shotmap.get('goal_mouth_coor').get('z'),
            'block_coord_x': shotmap.get('block_coor').get('x'),
            'block_coord_y': shotmap.get('block_coor').get('y'),
            'block_coord_z': shotmap.get('block_coor').get('z'),
            'draw_start_x': shotmap.get('draw').get('start').get('x'),
            'draw_start_y': shotmap.get('draw').get('start').get('y'),
            'draw_end_x': shotmap.get('draw').get('end').get('x'),
            'draw_end_y': shotmap.get('draw').get('end').get('y'),
            'draw_goal_x': shotmap.get('draw').get('goal').get('x'),
            'draw_goal_y': shotmap.get('draw').get('goal').get('y'),
            }
        shotmaps_list.append(shotmap_data)
        
    return shotmaps_list

def get_shots_on_goal(client, match_id):
    db = client['sofascore_data']
    collection = db['match_shotmaps']
    
    query = {
        'match_id': match_id
    }
    
    query_res = collection.find_one(query)
    
    shot_on_goal_list = []
    for shotmap in query_res.get('shotmap'):
        if shotmap.get('shot_type') != 'block' and shotmap.get('shot_type') != 'miss':
            shotmap_data = {
                'player_name': shotmap.get('player_name'),
                'player_pos': shotmap.get('player_pos'),
                'player_num': shotmap.get('player_num'),
                'is_home': shotmap.get('is_home'),
                'shot_type': shotmap.get('shot_type'),
                'goal_type': shotmap.get('goal_type', 'none'),
                'situation': shotmap.get('situation', 'none'),
                'body_part': shotmap.get('body_part', 'none'),
                'goal_mouth_location': shotmap.get('goal_mouth_location'),
                'body_part': shotmap.get('body_part'),
                'xG': shotmap.get('xg'),
                'xGOT': shotmap.get('xgot'),
                'time': shotmap.get('time'),
                'added_time': shotmap.get('addedTime'),
                'player_coord_x': shotmap.get('player_coor').get('x'),
                'player_coord_y': shotmap.get('player_coor').get('y'),
                'player_coord_z': shotmap.get('player_coor').get('z'),
                'goal_mouth_coord_x': shotmap.get('goal_mouth_coor').get('x'),
                'goal_mouth_coord_y': shotmap.get('goal_mouth_coor').get('y'),
                'goal_mouth_coord_z': shotmap.get('goal_mouth_coor').get('z'),
                'block_coord_x': shotmap.get('block_coor').get('x'),
                'block_coord_y': shotmap.get('block_coor').get('y'),
                'block_coord_z': shotmap.get('block_coor').get('z'),
                'draw_start_x': shotmap.get('draw').get('start').get('x'),
                'draw_start_y': shotmap.get('draw').get('start').get('y'),
                'draw_end_x': shotmap.get('draw').get('end').get('x'),
                'draw_end_y': shotmap.get('draw').get('end').get('y'),
                'draw_goal_x': shotmap.get('draw').get('goal').get('x'),
                'draw_goal_y': shotmap.get('draw').get('goal').get('y'),
                }
            shot_on_goal_list.append(shotmap_data)
        
    
    return shot_on_goal_list

def get_match_gk_stats(client, match_id, player_id):
    db = client['sofascore_data']
    collection = db['player_match_stats']
    
    combined_pipeline = [
    {
        "$match": {
            "match_id": int(match_id),
            "player_id": int(player_id)
        }
    },
    {
        "$facet": {
            # Cabang baru untuk mengambil Nama Pemain dari koleksi 'players'
            "player_info": [
                {
                    "$lookup": {
                        "from": "players",
                        "localField": "player_id",
                        "foreignField": "id",
                        "as": "details"
                    }
                },
                { "$unwind": "$details" },
                { "$project": { "_id": 0, "name": "$details.name" } }
            ],
            "stats_branch": [
                { "$project": { "_id": 0, "statistics": 1 } }
            ],
            "shots_branch": [
                {
                    "$lookup": {
                        "from": "match_lineups",
                        "let": { "p_id": "$player_id", "m_id": "$match_id" },
                        "pipeline": [
                            { "$match": { "$expr": { "$eq": ["$match_id", "$$m_id"] } } },
                            {
                                "$project": {
                                    "player_status": {
                                        "$cond": {
                                            "if": {"$in": ["$$p_id", "$home_starting.id"]}, "then": "home_start",
                                            "else": {
                                                "$cond": {
                                                    "if": {"$in": ["$$p_id", "$away_starting.id"]}, "then": "away_start",
                                                    "else": {
                                                        "$cond": {
                                                            "if": {"$in": ["$$p_id", "$home_bench.id"]}, "then": "home_sub",
                                                            "else": "away_sub"
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "relevant_sub": {
                                        "$filter": {
                                            "input": {"$concatArrays": [{"$ifNull": ["$home_subs", []]}, {"$ifNull": ["$away_subs", []]}]},
                                            "as": "sub",
                                            "cond": { "$or": [{"$eq": ["$$sub.player_out_id", "$$p_id"]}, {"$eq": ["$$sub.player_in_id", "$$p_id"]}] }
                                        }
                                    }
                                }
                            }
                        ],
                        "as": "lineup"
                    }
                },
                { "$unwind": "$lineup" },
                {
                    "$addFields": {
                        "sorted_subs": { "$sortArray": { "input": "$lineup.relevant_sub", "sortBy": { "time": 1 } } }
                    }
                },
                {
                    "$addFields": {
                        "time_range": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$and": [{"$regexMatch": {"input": "$lineup.player_status", "regex": "start"}}, {"$gt": [{"$size": "$sorted_subs"}, 0]}]}, "then": {"start": 0, "end": {"$first": "$sorted_subs.time"}}},
                                    {"case": {"$regexMatch": {"input": "$lineup.player_status", "regex": "start"}}, "then": {"start": 0, "end": 999}},
                                    {"case": {"$and": [{"$regexMatch": {"input": "$lineup.player_status", "regex": "sub"}}, {"$eq": [{"$size": "$sorted_subs"}, 2]}]}, "then": {"start": {"$arrayElemAt": ["$sorted_subs.time", 0]}, "end": {"$arrayElemAt": ["$sorted_subs.time", 1]}}},
                                    {"case": {"$regexMatch": {"input": "$lineup.player_status", "regex": "sub"}}, "then": {"start": {"$first": "$sorted_subs.time"}, "end": 999}}
                                ],
                                "default": {"start": 0, "end": 0}
                            }
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "match_shotmaps",
                        "let": {
                            "s_min": "$time_range.start",
                            "e_min": "$time_range.end",
                            "is_home_player": {"$regexMatch": {"input": "$lineup.player_status", "regex": "home"}},
                            "m_id": "$match_id"
                        },
                        "pipeline": [
                            { "$match": { "$expr": { "$eq": ["$match_id", "$$m_id"] } } },
                            { "$unwind": "$shotmap" },
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$ne": ["$shotmap.is_home", "$$is_home_player"] },
                                            { "$gte": ["$shotmap.time", "$$s_min"] },
                                            { "$lte": ["$shotmap.time", "$$e_min"] }
                                        ]
                                    }
                                }
                            },
                            { "$replaceRoot": { "newRoot": "$shotmap" } }
                        ],
                        "as": "extracted_shots"
                    }
                }
            ]
        }
    },
    {
        "$project": {
            "player_name": { "$arrayElemAt": ["$player_info.name", 0] },
            "stats": { "$arrayElemAt": ["$stats_branch.statistics", 0] },
            "shots_conceded": { "$arrayElemAt": ["$shots_branch.extracted_shots", 0] }
        }
    }
]

    result = list(collection.aggregate(combined_pipeline))
    
    shot_on_goal_list = []
    for shotmap in result[0]['shots_conceded']:
        if shotmap.get('shot_type') != 'block' and shotmap.get('shot_type') != 'miss':
            shotmap_data = {
                'player_name': shotmap.get('player_name'),
                'player_pos': shotmap.get('player_pos'),
                'player_num': shotmap.get('player_num'),
                'is_home': shotmap.get('is_home'),
                'shot_type': shotmap.get('shot_type'),
                'goal_type': shotmap.get('goal_type', 'none'),
                'situation': shotmap.get('situation', 'none'),
                'body_part': shotmap.get('body_part', 'none'),
                'goal_mouth_location': shotmap.get('goal_mouth_location'),
                'body_part': shotmap.get('body_part'),
                'xG': shotmap.get('xg'),
                'xGOT': shotmap.get('xgot'),
                'time': shotmap.get('time'),
                'added_time': shotmap.get('addedTime'),
                'player_coord_x': shotmap.get('player_coor').get('x'),
                'player_coord_y': shotmap.get('player_coor').get('y'),
                'player_coord_z': shotmap.get('player_coor').get('z'),
                'goal_mouth_coord_x': shotmap.get('goal_mouth_coor').get('x'),
                'goal_mouth_coord_y': shotmap.get('goal_mouth_coor').get('y'),
                'goal_mouth_coord_z': shotmap.get('goal_mouth_coor').get('z'),
                'draw_start_x': shotmap.get('draw').get('start').get('x'),
                'draw_start_y': shotmap.get('draw').get('start').get('y'),
                'draw_end_x': shotmap.get('draw').get('end').get('x'),
                'draw_end_y': shotmap.get('draw').get('end').get('y'),
                'draw_goal_x': shotmap.get('draw').get('goal').get('x'),
                'draw_goal_y': shotmap.get('draw').get('goal').get('y'),
                }
            shot_on_goal_list.append(shotmap_data)

    final_data = {
        "name": result[0].get('player_name'),
        "stats": result[0].get('stats'),
        "shot_conceded": shot_on_goal_list
    }
    
    return final_data

def get_shot_stats(client, match_id):
    db = client['sofascore_data']
    collection = db['match_stats']
    
    query = {
        'match_id': match_id
    }
    
    result = collection.find_one(query)
    
    # if not result or 'statistics' not in result:
    #     return []
    
    result_data = []
    
    for stats in result.get('statistics', []):
        group_name = stats.get('groupName')
        
        # Ambil semua item dari kategori "Shots"
        if group_name == "Shots":
            result_data.extend(stats.get('statisticsItems', []))
            
        # Ambil 'goalkeeperSaves' dari kategori "Goalkeeper" atau "Goal" 
        # (Tergantung struktur JSON Sofascore Anda, biasanya masuk kategori 'Goalkeeper')
        elif group_name == 'Goalkeeping':
            for item in stats.get('statisticsItems', []):
                if item.get('name') == 'Goalkeeper saves' or item.get('key') == 'goalkeeperSaves':
                    result_data.append(item)
                        
    return result_data

def get_match_info(client, match_id):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = {
        'match_id': match_id
    }
    
    query_res = collection.find_one(query)
    
    match_data = {
            'comp_name': query_res.get('comp_name'),
            'comp_season': query_res.get('comp_season'),
            'home_team': query_res.get('home_team'),
            'home_score': query_res.get('home_score'),
            'away_team': query_res.get('away_team'),
            'away_score': query_res.get('away_score'),
            'round': query_res.get('round')
    }
    
    return match_data

def get_match_heatmaps(client, match_id):
    db = client['sofascore_data']
    
    pipeline = [
        # 1. Filter heatmap berdasarkan match_id
        {"$match": {"match_id": match_id}},
        
        # 2. Join dengan collection lineups
        {
            "$lookup": {
                "from": "match_lineups",
                "localField": "match_id",
                "foreignField": "match_id",
                "as": "lineup_doc"
            }
        },
        
        # 3. Ambil dokumen pertama dari array lookup agar tidak berbentuk list
        {"$set": {"lineup": {"$first": "$lineup_doc"}}},

        # 4. Tentukan team_side dengan akses path yang benar
        {
            "$addFields": {
                "team_side": {
                    "$cond": {
                        "if": {
                            "$or": [
                                {"$in": ["$player_id", "$lineup.home_starting.id"]},
                                {"$in": ["$player_id", "$lineup.home_bench.id"]}
                            ]
                        },
                        "then": "home",
                        "else": {
                            "$cond": {
                                "if": {
                                    "$or": [
                                        {"$in": ["$player_id", "$lineup.away_starting.id"]},
                                        {"$in": ["$player_id", "$lineup.away_bench.id"]}
                                    ]
                                },
                                "then": "away",
                                "else": "unknown"
                            }
                        }
                    }
                }
            }
        },
        
        # 5. Grouping berdasarkan team_side
        {
            "$group": {
                "_id": "$team_side",
                "combined_heatmap": {"$push": "$heatmap"}
            }
        }
    ]
    
    results = list(db['player_match_heatmap'].aggregate(pipeline))
    
    # Mapping hasil
    final_data = {"home": [], "away": []}
    for res in results:
        if res['_id'] in final_data:
            # Flatten list of lists
            final_data[res['_id']] = [pt for sub in res['combined_heatmap'] for pt in sub]
            
    return final_data["home"], final_data["away"]

def get_match_team_name(client, match_id):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = {
        'match_id': match_id
    }
    
    query_res = collection.find_one(query)
    
    home_team = query_res.get('home_team')
    away_team = query_res.get('away_team')
    
    return home_team, away_team

def get_match_player_stats(client, match_id, player_id):
    db = client['sofascore_data']
    # Pastikan menggunakan koleksi yang benar (player_match_stats)
    collection = db['player_match_stats']
    
    pipeline = [
        # 1. Filter data berdasarkan match_id dan player_id
        {
            "$match": {
                "match_id": int(match_id),
                "player_id": int(player_id)
            }
        },
        # 2. Proyeksi dan Transformasi
        {
            "$project": {
                "_id": 0,
                "statistics": 1,
                "shots": {
                    "$map": {
                        "input": { "$ifNull": ["$shots", []] }, # Jaga-jaga jika shots kosong
                        "as": "s",
                        "in": {
                            "player_name": "$$s.player_name",
                            "player_pos": "$$s.player_pos",
                            "player_num": "$$s.player_num",
                            "is_home": "$$s.is_home",
                            "shot_type": "$$s.shot_type",
                            "goal_type": { "$ifNull": ["$$s.goal_type", "none"] },
                            "situation": { "$ifNull": ["$$s.situation", "none"] },
                            "body_part": { "$ifNull": ["$$s.body_part", "none"] },
                            "goal_mouth_location": "$$s.goal_mouth_location",
                            "xG": "$$s.xg",
                            "xGOT": "$$s.xgot",
                            "time": "$$s.time",
                            "added_time": "$$s.added_time",
                            # Flattening Koordinat
                            "player_coord_x": "$$s.player_coor.x",
                            "player_coord_y": "$$s.player_coor.y",
                            "player_coord_z": "$$s.player_coor.z",
                            "goal_mouth_coord_x": "$$s.goal_mouth_coor.x",
                            "goal_mouth_coord_y": "$$s.goal_mouth_coor.y",
                            "goal_mouth_coord_z": "$$s.goal_mouth_coor.z",
                            "block_coord_x": "$$s.block_coor.x",
                            "block_coord_y": "$$s.block_coor.y",
                            "block_coord_z": "$$s.block_coor.z",
                            # Flattening Draw Data
                            "draw_start_x": "$$s.draw.start.x",
                            "draw_start_y": "$$s.draw.start.y",
                            "draw_end_x": "$$s.draw.end.x",
                            "draw_end_y": "$$s.draw.end.y",
                            "draw_goal_x": "$$s.draw.goal.x",
                            "draw_goal_y": "$$s.draw.goal.y"
                        }
                    }
                }
            }
        }
    ]

    # Jalankan query pada collection yang sudah didefinisikan
    results = list(collection.aggregate(pipeline))
    
    # Mengembalikan satu dokumen saja (karena filter match_id & player_id harusnya unik)
    return results[0] if results else None

def get_substitution_details_by_match(client, match_id):
    db = client['sofascore_data']
    collection = db['match_lineups']
    
    pipeline = [
        # Tahap 1: Filter dokumen berdasarkan match_id terlebih dahulu
        {
            "$match": { "match_id": match_id }
        },
        # Tahap 2: Gabungkan array home dan away
        {
            "$project": {
                "match_id": 1,
                "all_subs": {"$concatArrays": ["$home_subs", "$away_subs"]}
            }
        },
        # Tahap 3: Pecah array menjadi dokumen individual
        {"$unwind": "$all_subs"},
        # Tahap 4: Ambil field spesifik yang dibutuhkan
        {
            "$project": {
                "_id": 0,
                "time": "$all_subs.time",
                "player_in_id": "$all_subs.player_in_id",
                "player_out_id": "$all_subs.player_out_id"
            }
        },
        # Tahap 5: Urutkan berdasarkan waktu (menit)
        {
            "$sort": { "time": 1 }
        }
    ]
    
    return list(collection.aggregate(pipeline))

def get_match_starting_players(client, match_id):
    db = client['sofascore_data']
    collection = db['match_lineups']

    query = {
        'match_id': match_id
    }

    filter = {
        'home': 1, 'away': 1, '_id': 0
    }

    query_res = collection.find_one(query, filter)

    home_players = query_res.get('home', {}).get('players', [])
    away_players = query_res.get('away', {}).get('players', [])

    home_starting = []
    for home_player in home_players:
        if home_player.get('substitute') == False:
            home_entry = {
                'name': home_player.get('player', {}).get('name'),
                'id': home_player.get('player', {}).get('id'),
                'position': home_player.get('player', {}).get('position'),
            }
            home_starting.append(home_entry)

    away_starting = []
    for away_player in away_players:
        if away_player.get('substitute') == False:
            away_entry = {
                'name': away_player.get('player', {}).get('name'),
                'id': away_player.get('player', {}).get('id'),
                'position': away_player.get('player', {}).get('position'),
            }
            away_starting.append(away_entry)

    return home_starting, away_starting

def get_substitution_details_by_match(client, match_id):
    db = client['sofascore_data']
    collection = db['match_lineups']

    pipeline = [
        # Tahap 1: Filter dokumen berdasarkan match_id terlebih dahulu
        {
            "$match": { "match_id": match_id }
        },
        # Tahap 2: Gabungkan array home dan away
        {
            "$project": {
                "match_id": 1,
                "all_subs": {"$concatArrays": ["$home_subs", "$away_subs"]}
            }
        },
        # Tahap 3: Pecah array menjadi dokumen individual
        {"$unwind": "$all_subs"},
        # Tahap 4: Ambil field spesifik yang dibutuhkan
        {
            "$project": {
                "_id": 0,
                "time": "$all_subs.time",
                "player_in_id": "$all_subs.player_in_id",
                "player_out_id": "$all_subs.player_out_id"
            }
        },
        # Tahap 5: Urutkan berdasarkan waktu (menit)
        {
            "$sort": { "time": 1 }
        }
    ]

    return list(collection.aggregate(pipeline))

def update_player_shots(client, match_id, shot_list):
    db = client['sofascore_data']
    collection = db['player_match_stats']
    
    # 1. Kelompokkan shots berdasarkan player_id di memori Python
    player_shots_map = {}
    for shot in shot_list:
        p_id = shot['player_id']
        if p_id not in player_shots_map:
            player_shots_map[p_id] = []
        player_shots_map[p_id].append(shot)

    # 2. Update ke MongoDB: Tambahkan field 'shots' ke tiap pemain
    updates_count = 0
    for player_id, shots in player_shots_map.items():
        result = collection.update_one(
            {
                "match_id": match_id, 
                "player_id": player_id
            },
            {
                "$set": { "shots": shots } # Menyimpan list shots ke field 'shots'
            },
            upsert=True # Buat dokumen baru jika pemain belum ada di collection ini
        )
        updates_count += 1

    print(f"Selesai! {updates_count} pemain telah diperbarui field 'shots'-nya.")
    
def get_rounds(client, comp_id, season_id):
    db = client['sofascore_data']
    collection = db['scheduler_round_info']

    query = {
        'comp_id': comp_id,
        'season_id': season_id
    }

    filter = {
        '_id': 0, 'scraped_round': 1, 'next_round': 1
    }

    data = collection.find_one(query, filter)

    scraped_round = data.get('scraped_round')
    next_round = data.get('next_round')

    return next_round, scraped_round

def update_rounds(client: MongoClient, comp_id: int, season_id: int, next_round: int, scraped_round: int):
    db = client['sofascore_data']
    collection = db['scheduler_round_info']
    
    collection.update_one(
        {
            "comp_id": comp_id,
            "season_id": season_id
        }, 
        {
            "$set": {"next_round": next_round + 1, "scraped_round": scraped_round + 1}
        }, 
        upsert=True
    )
    print("Berhasil mengupdate rounds")
    
def get_match_ids_per_round(client, comp_id, season_id, round_num):
    db = client['sofascore_data']
    collection = db['matches']
    
    query = collection.find(
        {
            "comp_id": comp_id,
            "season_id": season_id,
            "round": round_num, 
            "comp_status_type": "finished"
        }, 
        {
            "match_id": 1, 
            "_id": 0
        }
    )
    
    match_ids = [match['match_id'] for match in query]
    
    return match_ids

def get_gk_detailed_stats(client, player_id):
    db = client['sofascore_data']

    # Pastikan query ini mengembalikan list match_ids yang valid
    match_ids = get_match_by_player_id(client, player_id)

    pipeline = [
        {"$match": {"match_id": {"$in": match_ids}}},
        {
            "$project": {
                "match_id": 1,
                "player_status": {
                    "$cond": {
                        "if": {"$in": [player_id, "$home_starting.id"]}, "then": "home_start",
                        "else": {
                            "$cond": {
                                "if": {"$in": [player_id, "$away_starting.id"]}, "then": "away_start",
                                "else": {
                                    "$cond": {
                                        "if": {"$in": [player_id, "$home_bench.id"]}, "then": "home_sub",
                                        "else": "away_sub"
                                    }
                                }
                            }
                        }
                    }
                },
                "relevant_sub": {
                    "$filter": {
                        "input": {"$concatArrays": [{"$ifNull": ["$home_subs", []]}, {"$ifNull": ["$away_subs", []]}]},
                        "as": "sub",
                        "cond": {"$or": [{"$eq": ["$$sub.player_out_id", player_id]}, {"$eq": ["$$sub.player_in_id", player_id]}]}
                    }
                },
                "red_card": {
                    "$filter": {
                        "input": {"$ifNull": ["$incidents", []]},
                        "as": "inc",
                        "cond": {
                            "$and": [
                                {"$eq": ["$$inc.player_id", player_id]},
                                {"$eq": ["$$inc.incident_type", "card"]},
                                {"$eq": ["$$inc.card_type", "red"]}
                            ]
                        }
                    }
                }
            }
        },
        {"$addFields": { "relevant_sub": { "$sortArray": { "input": "$relevant_sub", "sortBy": { "time": 1 } } } }},
        {
            "$addFields": {
                "time_range": {
                    "$let": {
                        "vars": {
                            "sub_count": {"$size": "$relevant_sub"},
                            "rc_time": {"$ifNull": [{"$first": "$red_card.time"}, 999]},
                            "first_sub": {"$first": "$relevant_sub.time"},
                            "second_sub": {"$arrayElemAt": ["$relevant_sub.time", 1]}
                        },
                        "in": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$regexMatch": {"input": "$player_status", "regex": "start"}}, 
                                     "then": {"start": 0, "end": {"$min": [{"$ifNull": ["$$first_sub", 999]}, "$$rc_time"]}}},
                                    {"case": {"$gt": ["$$sub_count", 0]}, 
                                     "then": {"start": "$$first_sub", "end": {"$min": [{"$ifNull": ["$$second_sub", 999]}, "$$rc_time"]}}}
                                ],
                                "default": {"start": -1, "end": -1}
                            }
                        }
                    }
                }
            }
        },
        # Join dengan player_match_stats
        {
            "$lookup": {
                "from": "player_match_stats",
                "let": {"m_id": "$match_id", "p_id": player_id},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$match_id", "$$m_id"]}, {"$eq": ["$player_id", "$$p_id"]}]}}}
                ],
                "as": "raw_stats"
            }
        },
        # Join dengan match_shotmaps
        {
            "$lookup": {
                "from": "match_shotmaps",
                "let": {
                    "s_min": "$time_range.start", "e_min": "$time_range.end",
                    "gk_side": {"$regexMatch": {"input": "$player_status", "regex": "home"}},
                    "curr_m_id": "$match_id"
                },
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$match_id", "$$curr_m_id"]}}},
                    {"$unwind": "$shotmap"},
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$ne": ["$shotmap.is_home", "$$gk_side"]},
                                {"$gte": ["$shotmap.time", "$$s_min"]},
                                {"$lte": ["$shotmap.time", "$$e_min"]},
                                {"$not": [{"$in": ["$shotmap.shot_type", ["block", "miss"]]}]}
                            ]
                        }
                    }},
                    {"$replaceRoot": {"newRoot": "$shotmap"}}
                ],
                "as": "shots_conceded"
            }
        },
        # Join dengan match_stats untuk Ball Possession
        {
            "$lookup": {
                "from": "match_stats",
                "let": {
                    "curr_m_id": "$match_id",
                    "is_home_check": {"$cond": [{"$regexMatch": {"input": "$player_status", "regex": "home"}}, 1, 2]}
                },
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$match_id", "$$curr_m_id"]}}},
                    {"$project": {
                        "stat_item": {
                            "$first": {
                                "$filter": {
                                    "input": "$statistics",
                                    "as": "st",
                                    "cond": {"$eq": ["$$st.key", "ballPossession"]}
                                }
                            }
                        }
                    }},
                    {"$project": {
                        "val": {
                            "$cond": {
                                "if": {"$eq": ["$$is_home_check", 1]},
                                "then": "$stat_item.awayValue",
                                "else": "$stat_item.homeValue"
                            }
                        }
                    }}
                ],
                "as": "possession_res"
            }
        },
        {"$addFields": {"ball_possession": {"$first": "$possession_res.val"}}}
    ]

    results = db['match_lineups'].aggregate(pipeline)
    final_output = []

    for doc in results:
        # Jika kiper tidak bermain, lompati
        if doc['time_range']['start'] == -1:
            continue

        # Ekstraksi statistik dasar
        raw_stat = doc['raw_stats'][0].get('statistics', {}) if doc['raw_stats'] else {}

        xgot_pen = 0
        xgot_no_pen = 0
        goal_pen = 0
        goal_no_pen = 0
        player_scored_list = []

        for shot in doc.get('shots_conceded', []):
            # Ambil data yang sering digunakan satu kali di awal
            shot_type = shot.get('shot_type')
            situation = shot.get('situation')
            xgot_value = shot.get('xgot', 0)
        
            # Logika penghitungan Goal dan List Pemain
            if shot_type == 'goal':
                if shot.get('goal_type') == 'penalty':
                    goal_pen += 1
                else:
                    goal_no_pen += 1 
        
                player_scored_list.append({
                    'player_name': shot.get('player_name'),
                    'player_id': shot.get('player_id'),
                })
            
            # Logika penghitungan xGOT berdasarkan situasi penalti atau bukan
            if situation == 'penalty':
                xgot_pen += xgot_value
            else:
                xgot_no_pen += xgot_value


        stat_entry = {
            'min_played': raw_stat.get('minutesPlayed', 0),
            'ball_possession_opp': doc.get('ball_possession'),
            'total_pass': raw_stat.get('totalPass', 0),
            'acc_pass': raw_stat.get('accuratePass', 0),
            'total_long_pass': raw_stat.get('totalLongBalls', 0),
            'acc_long_pass': raw_stat.get('accurateLongBalls', 0),
            'total_short_pass': raw_stat.get('totalPass', 0) - raw_stat.get('totalLongBalls', 0),
            'acc_short_pass':  raw_stat.get('accuratePass', 0) - raw_stat.get('accurateLongBalls', 0),
            'duel_won': raw_stat.get('duelWon', 0),
            'total_duel': raw_stat.get('duelWon', 0) + raw_stat.get('duelLost', 0),
            'aerial_duel_won': raw_stat.get('aerialWon', 0),
            'total_aerial_duel': raw_stat.get('aerialWon', 0) + raw_stat.get('aerialLost', 0),
            'cross_claim': raw_stat.get('goodHighClaim', 0),
            'total_cross': raw_stat.get('goodHighClaim', 0) + raw_stat.get('crossNotClaimed', 0),
            'saves': raw_stat.get('saves', 0),
            'interception': raw_stat.get('interceptionWon', 0),
            'xgot_pen': xgot_pen,
            'xgot_no_pen': xgot_no_pen,
            'cd_goal_no_pen': goal_no_pen,
            'cd_goal_pen': goal_pen,
            'total_goal_concede': goal_pen + goal_no_pen
        }

        final_output.append({
            'match_id': doc['match_id'],
            'statistics': stat_entry,
        })

    return final_output

def get_gks_detailed_stats(client, player_ids):
    db = client['sofascore_data']

    # 1. Ambil list match_id yang relevan untuk semua player
    player_matches_data = get_matches_by_list_player_id(client, player_ids)
    all_match_ids = list(set([m_id for p in player_matches_data for m_id in p['match_ids']]))

    pipeline = [
        # Filter awal: Hanya ambil match yang dimainkan oleh salah satu dari player_ids
        {"$match": {"match_id": {"$in": all_match_ids}}},
        
        # Buat array berisi semua kategori pemain untuk di-unwind
        {"$project": {
            "match_id": 1,
            "home_starting": 1, "away_starting": 1, 
            "home_bench": 1, "away_bench": 1,
            "home_subs": 1, "away_subs": 1, "incidents": 1
        }},
        
        # Trick: Gunakan $concatArrays lalu $unwind agar kita bisa memproses per-pemain per-match
        {"$addFields": {
            "all_target_players": {
                "$filter": {
                    "input": {"$concatArrays": [
                        {"$ifNull": ["$home_starting", []]}, 
                        {"$ifNull": ["$away_starting", []]},
                        {"$ifNull": ["$home_bench", []]}, 
                        {"$ifNull": ["$away_bench", []]}
                    ]},
                    "as": "p",
                    "cond": {"$in": ["$$p.id", player_ids]}
                }
            }
        }},
        {"$unwind": "$all_target_players"},
        {"$addFields": {"curr_p_id": "$all_target_players.id"}},

        # 2. Penentuan Player Status secara Dinamis
        {"$addFields": {
            "player_status": {
                "$cond": {
                    "if": {"$in": ["$curr_p_id", "$home_starting.id"]}, "then": "home_start",
                    "else": {
                        "$cond": {
                            "if": {"$in": ["$curr_p_id", "$away_starting.id"]}, "then": "away_start",
                            "else": {
                                "$cond": {
                                    "if": {"$in": ["$curr_p_id", "$home_bench.id"]}, "then": "home_sub",
                                    "else": "away_sub"
                                }
                            }
                        }
                    }
                }
            }
        }},

        # 3. Filter Substitusi dan Red Card khusus untuk player yang sedang di-unwind
        {"$addFields": {
            "relevant_sub": {
                "$filter": {
                    "input": {"$concatArrays": [{"$ifNull": ["$home_subs", []]}, {"$ifNull": ["$away_subs", []]}]},
                    "as": "sub",
                    "cond": {"$or": [{"$eq": ["$$sub.player_out_id", "$curr_p_id"]}, {"$eq": ["$$sub.player_in_id", "$curr_p_id"]}]}
                }
            },
            "red_card": {
                "$filter": {
                    "input": {"$ifNull": ["$incidents", []]},
                    "as": "inc",
                    "cond": {
                        "$and": [
                            {"$eq": ["$$inc.player_id", "$curr_p_id"]},
                            {"$eq": ["$$inc.incident_type", "card"]},
                            {"$eq": ["$$inc.card_type", "red"]}
                        ]
                    }
                }
            }
        }},

        {"$addFields": { "relevant_sub": { "$sortArray": { "input": "$relevant_sub", "sortBy": { "time": 1 } } } }},

        # 4. Kalkulasi Time Range (Kapan pemain ada di lapangan)
        {"$addFields": {
            "time_range": {
                "$let": {
                    "vars": {
                        "sub_count": {"$size": "$relevant_sub"},
                        "rc_time": {"$ifNull": [{"$first": "$red_card.time"}, 999]},
                        "first_sub": {"$first": "$relevant_sub.time"},
                        "second_sub": {"$arrayElemAt": ["$relevant_sub.time", 1]}
                    },
                    "in": {
                        "$switch": {
                            "branches": [
                                {"case": {"$regexMatch": {"input": "$player_status", "regex": "start"}}, 
                                 "then": {"start": 0, "end": {"$min": [{"$ifNull": ["$$first_sub", 999]}, "$$rc_time"]}}},
                                {"case": {"$gt": ["$$sub_count", 0]}, 
                                 "then": {"start": "$$first_sub", "end": {"$min": [{"$ifNull": ["$$second_sub", 999]}, "$$rc_time"]}}}
                            ],
                            "default": {"start": -1, "end": -1}
                        }
                    }
                }
            }
        }},

        # 5. Lookups (Menggunakan curr_p_id yang dinamis)
        {
            "$lookup": {
                "from": "player_match_stats",
                "let": {"m_id": "$match_id", "p_id": "$curr_p_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$match_id", "$$m_id"]}, {"$eq": ["$player_id", "$$p_id"]}]}}},
                    # Tambahkan project di sini untuk mengambil name
                    {"$project": {"_id": 0, "name": 1, "statistics": 1}}
                ],
                "as": "raw_stats"
            }
        },
        {
            "$lookup": {
                "from": "match_shotmaps",
                "let": {
                    "s_min": "$time_range.start", "e_min": "$time_range.end",
                    "gk_side": {"$regexMatch": {"input": "$player_status", "regex": "home"}},
                    "curr_m_id": "$match_id"
                },
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$match_id", "$$curr_m_id"]}}},
                    {"$unwind": "$shotmap"},
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$ne": ["$shotmap.is_home", "$$gk_side"]},
                                {"$gte": ["$shotmap.time", "$$s_min"]},
                                {"$lte": ["$shotmap.time", "$$e_min"]},
                                {"$not": [{"$in": ["$shotmap.shot_type", ["block", "miss"]]}]}
                            ]
                        }
                    }},
                    {"$replaceRoot": {"newRoot": "$shotmap"}}
                ],
                "as": "shots_conceded"
            }
        }
    ]

    results = db['match_lineups'].aggregate(pipeline)
    
    # --- LOGIKA AGREGASI DI PYTHON ---
    players_stats = {}

    for doc in results:
        p_id = doc['curr_p_id']
        p_name = doc['raw_stats'][0].get('name', 'Unknown') if doc['raw_stats'] else 'Unknown'
        
        if p_id not in players_stats:
            players_stats[p_id] = {
                'player_id': p_id, 'name': p_name,
                'min_played': 0, 'total_pass': 0, 'acc_pass': 0,
                'total_long_pass': 0, 'acc_long_pass': 0, 'total_short_pass': 0,
                'acc_short_pass': 0, 'duel_won': 0, 'total_duel': 0, 'aerial_duel_won': 0,
                'total_aerial_duel': 0, 'cross_claim': 0, 'total_cross': 0, 'saves': 0,
                'interception': 0, 'xgot_pen': 0, 'xgot_no_pen': 0, 'cd_goal_no_pen': 0, 
                'cd_goal_pen': 0, 'total_goal_concede': 0, 'match_count': 0
            }

        if doc['time_range']['start'] == -1: continue

        stats = players_stats[p_id]
        stats['match_count'] += 1
        
        raw_stat = doc['raw_stats'][0].get('statistics', {}) if doc['raw_stats'] else {}

         # Hitung data shot untuk pertandingan ini
        current_xgot_pen = 0
        current_xgot_no_pen = 0
        current_goal_pen = 0
        current_goal_no_pen = 0
    
        for shot in doc.get('shots_conceded', []):
            shot_type = shot.get('shot_type')
            situation = shot.get('situation')
            xgot_value = shot.get('xgot', 0)
        
            if shot_type == 'goal':
                if shot.get('goal_type') == 'penalty':
                    current_goal_pen += 1
                else:
                    current_goal_no_pen += 1 
        
            if situation == 'penalty':
                current_xgot_pen += xgot_value
            else:
                current_xgot_no_pen += xgot_value
    
        # --- PROSES PENJUMLAHAN (AGREGASI) ---
        stats['min_played'] += raw_stat.get('minutesPlayed', 0)
        stats['total_pass'] += raw_stat.get('totalPass', 0)
        stats['acc_pass'] += raw_stat.get('accuratePass', 0)
        
        stats['total_long_pass'] += raw_stat.get('totalLongBalls', 0)
        stats['acc_long_pass'] += raw_stat.get('accurateLongBalls', 0)
        stats['total_short_pass'] += (raw_stat.get('totalPass', 0) - raw_stat.get('totalLongBalls', 0))
        stats['acc_short_pass'] += (raw_stat.get('accuratePass', 0) - raw_stat.get('accurateLongBalls', 0))
        
        stats['duel_won'] += raw_stat.get('duelWon', 0)
        stats['total_duel'] += (raw_stat.get('duelWon', 0) + raw_stat.get('duelLost', 0))
        stats['aerial_duel_won'] += raw_stat.get('aerialWon', 0)
        stats['total_aerial_duel'] += (raw_stat.get('aerialWon', 0) + raw_stat.get('aerialLost', 0))
        
        stats['cross_claim'] += raw_stat.get('goodHighClaim', 0)
        stats['total_cross'] += (raw_stat.get('goodHighClaim', 0) + raw_stat.get('crossNotClaimed', 0))
        
        stats['saves'] += raw_stat.get('saves', 0)
        stats['interception'] += raw_stat.get('interceptionWon', 0)
        
        stats['xgot_pen'] += current_xgot_pen
        stats['xgot_no_pen'] += current_xgot_no_pen
        stats['cd_goal_no_pen'] += current_goal_no_pen
        stats['cd_goal_pen'] += current_goal_pen
        stats['total_goal_concede'] += (current_goal_pen + current_goal_no_pen)

    return pd.DataFrame(list(players_stats.values()))