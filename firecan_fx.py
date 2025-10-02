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

########################################################################################################################################################################################################################################################################################################################
# I AM CHANGING THINGS JUST FOR DEV, THIS LINE SHOULD ONLY BE IN DEV
######################################################################################################################################################################################################################################################################################################################################################################################################








##################### GET QC FIRE DATA ################################################################################################################################################################################################################################################################################################################################################################################################
def fx_get_qc_data(dataname, url, zipname, gpkgname):
    savefolder = work_dir / dataname
    zip_path = savefolder / zipname # zipname = "FEUX_PROV_GPKG.zip" OR "FEUX_PROV_GPKG.zip"
    unzipped_file_path = savefolder / gpkgname # gpkgname = "FEUX_PROV.gpkg" OR "FEUX_ANCIENS_PROV.gpkg"
    savepath = os.path.join(savefolder, zipname)

    if not unzipped_file_path.exists():
        print('Data does not exist, Downloading now, this may take several minutes ...')
        savefolder.mkdir(parents=True, exist_ok=True)
        print("Created folder:", savefolder)

        response = requests.get(url)
        with open(savepath, 'wb') as f:
            f.write(response.content)
        print("DONE Downloading the Data for", dataname)        
        
        with zipfile.ZipFile(savepath, 'r') as zip_ref:
            zip_ref.extractall(savefolder)
        print("DONE! unzipping the data, data is located in", savepath)
    else:
        print("..........Unzipped Data Exists For", dataname)

    return unzipped_file_path
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################



def fx_qc_processfiredata(path,layer):
    print("hello")
# first load both datasets in 
# then merge the datasets
# the reproject the data set
# then convert to geojson
# then save to a new specialized geojson path
# return combined geojson
# gonna have to redo filtering logic i think 
# NVM MUST CONVERT TO GEOJSON IN FLASK
# INSTEAD CREATE PROCESSING FUCTION THAT INCLUDES ALL PROCESSING STEPS load in merge, add watershed column, reproject, save
# Save the merged dataset, do if check to see if merged dataset exists if yes load it (also check if in right projection) in if not merge and do the processing



def fx_load_and_reproject_data(path,layer): # qcfires_before76_unzipped_file_path and qcfires_after76_unzipped_file_path 
    print("Loading in the Data")
    data = gpd.read_file(path, layer=layer)

    is_wgs84 = data.crs.to_epsg() == 4326
    if is_wgs84:
        print("The data is already in EPSG:4326 (WGS 84).")
        return data
    else:
        print("Reprojecting Data")
        reprojected_data = data.to_crs(epsg=4326)                       # Reprojecting the data
        reprojected_data.to_file(path, layer=layer, driver="GPKG", mode='w')
        return reprojected_data







############## LOAD IN AND MERGE BEFORE AND AFTER QC FIRE DATASET ##################################################################################################################################################################################################################################################################################################################################################################################
def fx_qc_firedata_merge(after, before):

    print(".....................................................................Loading in the Data")

    after = after.rename(columns={"geoc_fmj": "geoc"})
    after = after.drop(columns=["perturb", "an_perturb", "part_str"])


    before = before.rename(columns={"geoc_fan": "geoc"})

    print(".....................................................................Merging the data")

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
















# def fx_qc_processfiredata(after, before):
#     qc_fires_file_path = os.path.join('qc_fire_data')
#     print(qc_fires_file_path)
#     if not os.path.exists(qc_fires_file_path):
#         print(".....................................................................Loading in the Data")
#         before = gpd.read_file(before, layer="feux_anciens_prov")
#         after = gpd.read_file(after, layer="feux_prov")

#         print(".....................................................................Merging the data")
#         after = after.rename(columns={"geoc_fmj": "geoc"})
#         after = after.drop(columns=["perturb", "an_perturb", "part_str"])
#         before = before.rename(columns={"geoc_fan": "geoc"})
#         data = gpd.GeoDataFrame(
#             pd.concat([before, after], ignore_index=True),
#             geometry="geometry"  
#         )
#         data["an_origine"] = pd.to_numeric(data["an_origine"], errors="coerce")
#         data["superficie"] = pd.to_numeric(data["superficie"], errors="coerce")

#         data.to_file("qc_fire_data", driver="GPKG", mode='w')
#     else:
#         print("yes1")
#         data = gpd.read_file(qc_fires_file_path)






#     url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
#     watersheddata_zipname = "CE_bassin_multi.gdb.zip"
#     watersheddata_fgdbname = "CE_bassin_multi.gdb"
#     watersheddata_unzipped_file_path = fx_get_qc_data("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)
    
#     layers = fiona.listlayers(watersheddata_unzipped_file_path)
#     gdf_watershed = gpd.read_file(watersheddata_unzipped_file_path, layer=layers[1])  

#     if 'watershed' not in data.columns:
#         is_wgs84 = gdf_watershed.crs.to_epsg() == 4326
#         if is_wgs84:
#             print("The data is already in EPSG:4326 (WGS 84).")
#         else:
#             print("Reprojecting Data")
#             gdf_watershed = gdf_watershed.to_crs(epsg=4326)                       # Reprojecting the data
#             gdf_watershed.to_file("gdf_watershed", driver="GPKG", mode='w')
#         data = gpd.sjoin(
#             data,
#             gdf_watershed[['NOM_COURS_DEAU', 'geometry']],  # only need watershed name and geometry
#             how='left',
#             predicate='within'  # assigns watershed if fire is within the polygon
#         )
#         data = data.rename(columns={'NOM_COURS_DEAU': 'watershed'})
#         data = data.drop(columns=['index_right'])

#     cols = list(data.columns)
#     cols.insert(cols.index('shape_length'), cols.pop(cols.index('watershed')))
#     data = data[cols]






#     is_wgs84 = data.crs.to_epsg() == 4326
#     if is_wgs84:
#         print("The data is already in EPSG:4326 (WGS 84).")
#         return data
#     else:
#         print("Reprojecting Data")
#         reprojected_data = data.to_crs(epsg=4326)                       # Reprojecting the data
#         reprojected_data.to_file("data", driver="GPKG", mode='w')
#         return reprojected_data
