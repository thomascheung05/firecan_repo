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
import math

work_dir  = Path.cwd()



def fx_scrape_donneqc(dataname, url, zipname, gpkgname): # Downloads the data (if not already) and returns the path to the file
    savefolder = work_dir / dataname
    zip_path = savefolder / zipname # zipname = "FEUX_PROV_GPKG.zip" OR "FEUX_PROV_GPKG.zip"
    unzipped_file_path = savefolder / gpkgname # gpkgname = "FEUX_PROV.gpkg" OR "FEUX_ANCIENS_PROV.gpkg"

    if not unzipped_file_path.exists():
        print("Data does not exist, Downloading now, this may take several minutes ...")
        savefolder.mkdir(parents=True, exist_ok=True)
        print("Created folder:", savefolder)
        response = requests.get(url)
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print("DONE Downloading the Data for", dataname) 
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(savefolder)
        print("DONE! unzipping the data, data is located in", zip_path)
    else:
        print("..........Unzipped Data Exists For", dataname)

    return unzipped_file_path




def fx_qc_processfiredata(beforepath, afterpath): 

    qc_processed_data_folder_path = work_dir / "qc_processed_data"
    qc_processed_data_path = qc_processed_data_folder_path / "qc_processed_data.parquet"

    if not qc_processed_data_path.exists():
        # Loads in before+after data, renames column to merge, merges, downlaods watersehd data, reproject data, merges fires and watershed data
        # Skip this code and load data direclty IF it exists AND It is reprojected AND it has watershed column 
        qc_processed_data_folder_path.mkdir(parents=True, exist_ok=True)
        print("Loading in unprocessed fire data ... This may take a few minutes ...")
        before_data = gpd.read_file(beforepath, layer= "feux_anciens_prov")
        after_data = gpd.read_file(afterpath, layer= "feux_prov")



        print("Merging the data")
        before_data = before_data.rename(columns={"geoc_fan": "geoc"})
        after_data = after_data.rename(columns={"geoc_fmj": "geoc"})
        after_data = after_data.drop(columns=["perturb", "an_perturb", "part_str"])
        merged_data = gpd.GeoDataFrame(
            pd.concat([before_data, after_data], ignore_index=True),
            geometry="geometry"  
        )
        merged_data["an_origine"] = pd.to_numeric(merged_data["an_origine"], errors="coerce")
        merged_data["superficie"] = pd.to_numeric(merged_data["superficie"], errors="coerce")
        merged_data = merged_data.drop(columns=["exercice", "origine", "met_at_str", "shape_length", "shape_area"]) # might want shape length and share area later



        print("Reprojecting Fire data")
        is_wgs84 = merged_data.crs.to_epsg() == 4326
        if is_wgs84:
            print("The data is already in EPSG:4326 (WGS 84).")
        else:
            merged_data = merged_data.to_crs(epsg=4326)    


        print("Saving processed QC data to load in later")
        merged_data.to_parquet(qc_processed_data_path)

    else:
        print("The QC data is already processed, loading in now ...")
        merged_data = gpd.read_parquet(qc_processed_data_path)



    return merged_data




def fx_get_watershed_data():
    print("Getting Watershed Data")
    url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
    watersheddata_zipname = "CE_bassin_multi.gdb.zip"
    watersheddata_fgdbname = "CE_bassin_multi.gdb"

    qcwatershed_unzipped_file_path = fx_scrape_donneqc("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)                   
        
    layers = fiona.listlayers(qcwatershed_unzipped_file_path)
    watershed_data = gpd.read_file(qcwatershed_unzipped_file_path, layer=layers[1])
    watershed_data = watershed_data.drop(columns=["NO_COURS_DEAU", "NOM_COURS_DEAU_MINUSCULE", "NIVEAU_BASSIN", "ECHELLE", "SUPERF_KM2", "NO_SEQ_BV_PRIMAIRE", "NOM_BV_PRIMAIRE", "NO_REG_HYDRO", "NOM_REG_HYDRO_ABREGE", "Shape_Length", "Shape_Area"]) # might want shape length and share area later

    print("Reprojecting Watershed data")
    is_wgs84 = watershed_data.crs.to_epsg() == 4326
    if is_wgs84:
        print("The data is already in EPSG:4326 (WGS 84).")
    else:
        watershed_data = watershed_data.to_crs(epsg=4326)  
    return watershed_data



def fx_filter_fires_data(
    fire_gdf,
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

    if min_year  != "" or max_year  != "":
        if min_year  != "":
            min_year = int(min_year)
        else:
             min_year = 0
        if max_year  != "":
            max_year= int(max_year)
        else:
             max_year = 100000
        conditions.append((filtered_gdf["an_origine"] >= min_year) & (filtered_gdf["an_origine"] <= max_year))

    if min_size  != "" or max_size  != "":
        if min_size  != "":
            min_size = int(min_size)
        else:
             min_size = 0
        if min_size  != "":
            max_size= int(max_size)
        else:
             min_size = 100000
        conditions.append((filtered_gdf["superficie"] >= min_size) & (filtered_gdf["superficie"] <= max_size))

    if distance_coords  != "" and distance_radius  != "":

            lat, lon = map(float, distance_coords.split(","))
            distance_radius = float(distance_radius)
            user_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")
            utm_crs = user_point.estimate_utm_crs()  # automatically picks the UTM zone for your point
            user_point_m = user_point.to_crs(utm_crs)
            buffer_m = user_point_m.buffer(distance_radius)
            buffer_deg = buffer_m.to_crs("EPSG:4326")
            conditions.append(filtered_gdf.geometry.intersects(buffer_deg.iloc[0]))

    if watershed_name  != "": # This shit dont work
            gdf_watershed = fx_get_watershed_data()
            selected_ws = gdf_watershed[gdf_watershed['NOM_COURS_DEAU'] == watershed_name]
            if not selected_ws.empty:
                ws_geom = selected_ws.geometry.unary_union
                conditions.append(filtered_gdf.geometry.within(ws_geom))
            else:
                print(f"No watershed found with name '{watershed_name}'. Filter will be ignored.")

    if conditions:
        combined_mask = np.logical_and.reduce(conditions)
        filtered_gdf = filtered_gdf[combined_mask]
        
    return filtered_gdf

 


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



