import os
import zipfile
import json
import requests
import geopandas as gpd
from flask import Flask, jsonify, request, send_file  # type: ignore
import io
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import fiona # type: ignore
import numpy as np

work_dir  = Path.cwd()



##################### GET QC FIRE DATA ################################################################################################################################################################################################################################################################################################################################################################################################
def fx_get_qc_data(dataname, url, zipname, gpkgname):
    savefolder = work_dir / dataname
    zip_path = savefolder / zipname # zipname = "FEUX_PROV_GPKG.zip" OR "FEUX_PROV_GPKG.zip"
    unzipped_file_path = savefolder / gpkgname # gpkgname = "FEUX_PROV.gpkg" OR "FEUX_ANCIENS_PROV.gpkg"
    savepath = os.path.join(savefolder, zipname)

    if not savefolder.exists():
        savefolder.mkdir(parents=True, exist_ok=True)
        print("Created folder:", savefolder)
    else:
        print("Folder Exists for", dataname)

    if not zip_path.exists():
        print(dataname, "is not downloaded, downloading now, this may take a few minutes")
        response = requests.get(url)
        with open(savepath, 'wb') as f:
            f.write(response.content)
        print("DONE Downloading the Data for", dataname)
    else:
        print(".....Zipped Data Exists For", dataname)
    
    if not unzipped_file_path.exists():
        print("Unzipping the Data now")
        with zipfile.ZipFile(savepath, 'r') as zip_ref:
            zip_ref.extractall(savefolder)
        print("DONE! unzipping the data, data is located in", savepath)
    else:
        print("..........Unzipped Data Exists For", dataname)

    return unzipped_file_path
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################







############## LOAD IN AND MERGE BEFORE AND AFTER QC FIRE DATASET ##################################################################################################################################################################################################################################################################################################################################################################################
def fx_qc_firedata_loadmerge(afterpath, beforepath):

    print(".....................................................................Loading in the Data")
    after = gpd.read_file(afterpath, layer="feux_prov")
    after = after.rename(columns={"geoc_fmj": "geoc"})
    after = after.drop(columns=["perturb", "an_perturb", "part_str"])

    before = gpd.read_file(beforepath, layer="feux_anciens_prov")
    before = before.rename(columns={"geoc_fan": "geoc"})

    print(".....................................................................Merging and Reprojecting the data")

    merged = gpd.GeoDataFrame(
        pd.concat([before, after], ignore_index=True),
        geometry="geometry"  
    )

    merged["an_origine"] = pd.to_numeric(merged["an_origine"], errors="coerce")
    merged["superficie"] = pd.to_numeric(merged["superficie"], errors="coerce")
        


    return merged
########################################################################################################################################################################################################################################################################################################################






############# LOAD QC WATERSHED DATA ###########################################################################################################
def fx_qc_watersheddata_load(fgdb_path):
    layers = fiona.listlayers(fgdb_path)
    gdf = gpd.read_file(fgdb_path, layer=layers[1])  # or the layer name
########################################################################################################################







############ NEW FILTERING DATA #############################################################################################################
def fx_filter_fires_data(
    fire_gdf,
    watershed_gdf,
    min_year,
    max_year,
    min_size,
    max_size,
    distance_coords,
    distance_radius,
    watershed_name
):

    filtered_gdf = fire_gdf.copy()
    conditions = []

    if min_year  != "" and max_year  != "":
        min_year = int(min_year)
        max_year = int(max_year)
        conditions.append((filtered_gdf["an_origine"] >= min_year) & (filtered_gdf["an_origine"] <= max_year))

    if min_size  != "" and max_size  != "":
        min_size= int(min_size)
        max_size= int(max_size)
        conditions.append((filtered_gdf["superficie"] >= min_size) & (filtered_gdf["superficie"] <= max_size))

    if distance_coords  != "" and distance_radius  != "":
            lat, lon = map(float, distance_coords.split(","))
            distance_radius = float(distance_radius)
            user_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")
            user_point_proj = user_point.to_crs(filtered_gdf.crs)
            buffer_geom = user_point_proj.buffer(distance_radius)
            conditions.append(filtered_gdf.geometry.intersects(buffer_geom.iloc[0]))

    if watershed_name  != "":
            selected_ws = watershed_gdf[watershed_gdf['NOM_COURS_DEAU'] == watershed_name]
            if not selected_ws.empty:
                ws_geom = selected_ws.geometry.unary_union
                conditions.append(filtered_gdf.geometry.within(ws_geom))
            else:
                print(f"No watershed found with name '{watershed_name}'. Filter will be ignored.")

    if conditions:
        combined_mask = np.logical_and.reduce(conditions)
        filtered_gdf = filtered_gdf[combined_mask]
        
    return filtered_gdf
#############################################################################################################




def fx_download_json(filtered_data):
        geojson_data = json.loads(filtered_data.to_json())                    # Convert the filtered GeoDataFrame to GeoJSON
        geojson_string = json.dumps(geojson_data) 
    
        geojson_buffer = io.BytesIO(geojson_string.encode('utf-8'))                         # Create an in-memory buffer to hold the file content
        geojson_buffer.seek(0)
        
        return send_file(                                               # Send the file back to the browser as an attachment

            geojson_buffer,
            
            mimetype='application/json',                    # CRITICAL: Change MIME type to 'application/json' or 'application/geo+json'
            as_attachment=True,
            download_name='firecan_filtered_data.geojson'                   # CRITICAL: Change file extension to '.geojson'

        )


def fx_download_csv(filtered_data):
    csv_buffer = io.BytesIO()
    filtered_data.to_csv(csv_buffer, index=False, encoding="utf-8")
    csv_buffer.seek(0)
    
    return send_file(                                                   # Return the file as an attachment to the user's Downloads folder

        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='firecan_filtered_data.csv'
    ) 