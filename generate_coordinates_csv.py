import csv
from datetime import datetime
from dotenv import load_dotenv
from supabase_client import get_sitreps

# Load .env for Supabase credentials
load_dotenv()

OUTPUT_PATH = "sitreps_coordinates_upsert.csv"

# Default Congo region center; slight offset per id to avoid overlap
DEFAULT_LON = 15.2827
DEFAULT_LAT = -4.2634
OFFSET_STEP = 0.01  # ~1.1km at equator


def compute_coord(value, default, idx_offset):
    try:
        if value is None:
            raise ValueError
        # String to float if necessary
        return float(value)
    except Exception:
        return default + idx_offset


def main():
    sitreps = get_sitreps() or []
    rows = []
    for s in sitreps:
        sid = s.get("id")
        # Prefer lat/lon keys, fall back to latitude/longitude
        lon_val = s.get("lon", s.get("longitude"))
        lat_val = s.get("lat", s.get("latitude"))
        # Use a deterministic offset based on id to avoid overlapping
        idx = (sid or 0) % 100
        lon = compute_coord(lon_val, DEFAULT_LON, idx * OFFSET_STEP)
        lat = compute_coord(lat_val, DEFAULT_LAT, idx * OFFSET_STEP)
        rows.append({
            "id": sid,
            "latitude": lat,
            "longitude": lon,
        })

    # Write minimal upsert CSV: id, latitude, longitude
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "latitude", "longitude"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()