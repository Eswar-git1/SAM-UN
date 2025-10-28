from mbutil import encode

# Input directory and output MBTiles path
input_dir = r"E:\Project Folder\J&K_QGIS_App\Mapnik"
output_file = r"E:\Project Folder\J&K_QGIS_App\Mapnik.mbtiles"

# Convert tiles to MBTiles
encode(input_dir, output_file)
print(f"Successfully converted {input_dir} to {output_file}")
