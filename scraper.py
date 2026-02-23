import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

import module.fetch as fetch
import module.query as query

# 1. Load env dan koneksi (Singleton pattern)
# Di bagian atas setelah load_dotenv()
load_dotenv()

# Gunakan os.getenv tanpa default 'mongodb://mongodb:27017/' 
# agar GitHub Actions wajib membaca dari Secrets
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    print("ERROR: MONGO_URI tidak ditemukan di Environment Variables!")
    exit(1)

client = MongoClient(mongo_uri)

def main_fetcher():
    """
    Menjalankan proses fetch dan update data secara langsung (One-off execution).
    """
    try:
        # Cek koneksi ke MongoDB
        client.admin.command('ping')
        print(f"[{datetime.now()}] Koneksi DB OK. Memulai fetch data...")
        
        # Ambil data kompetisi
        comps_data = query.get_comp_season_id(client)
        
        if not comps_data:
            print("Tidak ada data kompetisi yang ditemukan.")
            return

        for comp_id, season_id in comps_data.items():
            print(f"\n--- Memproses Comp ID: {comp_id} (Season: {season_id}) ---")
            
            next_round, scraped_round = query.get_rounds(client, comp_id, season_id)
            
            # 1. Fetch match data dasar
            match_list = fetch.match_round(client=client, comp_id=comp_id, season_id=season_id)
            
            # 2. Ambil ID match untuk ronde yang sedang diproses
            round_match_ids = query.get_match_ids_per_round(
                client=client, 
                comp_id=comp_id, 
                season_id=season_id, 
                round_num=next_round
            )
            
            if not round_match_ids:
                print(f"Tidak ada match ID baru untuk ronde {next_round}.")
                continue

            # 3. Fetch Detail Data (Lineups, Stats, Shotmaps)
            fetch.match_lineups(client=client, match_ids=round_match_ids)
            fetch.match_incidents(client=client, match_ids=round_match_ids)
            fetch.match_stats(client=client, comp_id=comp_id, season_id=season_id, match_ids=round_match_ids)
            fetch.player_match_stats(client=client, comp_id=comp_id, season_id=season_id, match_ids=round_match_ids)
            fetch.match_shotmaps(client=client, match_ids=round_match_ids)
            
            # 4. Fetch Heatmap per Player
            for match_id in round_match_ids:
                player_ids = query.get_match_player_ids(client, match_id)
                if player_ids:
                    fetch.player_match_heatmap(client, match_id, player_ids)
            
            # 5. Update Status Ronde
            query.update_rounds(
                client=client, 
                comp_id=comp_id, 
                season_id=season_id, 
                next_round=next_round, 
                scraped_round=scraped_round
            )
            
            print(f"Selesai memproses {len(round_match_ids)} match untuk Comp ID: {comp_id}")
        
        print(f"\n[{datetime.now()}] Semua proses selesai. Data sudah terbaru.")

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")
    finally:
        client.close()
        print("Koneksi Database ditutup.")

if __name__ == "__main__":
    main_fetcher()