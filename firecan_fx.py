import os
import zipfile
import requests
import geopandas as gpd
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import fiona # type: ignore
import numpy as np

work_dir  = Path.cwd()



##################### GET QC FIRE DATA ################################################################################################
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
################################################################################################







############## LOAD IN AND MERGE BEFORE AND AFTER QC FIRE DATASET ##################################################################################
def fx_qc_firedata_loadmergereporoject(afterpath, beforepath):

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
########################################################################################################################






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
        print(f"Value of min_size: '{min_size}'") # Add this line
        print(f"Type of min_size: {type(min_size)}") # Add this line
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

















# ############ FILTERING DATA #############################################################################################################
# def fx_filter_by_year(gdf):
#     min_year = int(input("Input the minimum year: "))
#     max_year = int(input("Input the maximum year: "))

#     gdf = gdf[(gdf["an_origine"] >= min_year) & (gdf["an_origine"] <= max_year)]
    
#     return gdf


# def fx_filter_by_size(gdf):
#     min_size = int(input("Input the minimum size: "))
#     max_size = int(input("Input the maximum size: "))

#     gdf = gdf[(gdf["superficie"] >= min_size) & (gdf["superficie"] <= max_size)]

#     return gdf





# def fx_filter_by_distance(gdf):
#     cord = input("Enter the coordiates of center point: ")
#     radius = float(input("Enter radius in meters: "))

#     lat, lon = map(float, cord.split(","))


#     user_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")
#     user_point_proj = user_point.to_crs(gdf.crs)
#     buffer_geom = user_point_proj.buffer(radius)

#     gdf = gdf[gdf.geometry.intersects(buffer_geom.iloc[0])]
#     # possible_idx = list(gdf.sindex.intersection(buffer_geom.iloc[0].bounds))
#     # gdf_candidate = gdf.iloc[possible_idx]
#     # gdf = gdf_candidate[gdf_candidate.geometry.intersects(buffer_geom.iloc[0])]

#     return gdf


# def fx_filter_by_watershed(fire_gdf, watershed_gdf):
#     user_watershed = input('Enter the name of the watershed: ')
#     selected_ws = watershed_gdf[watershed_gdf['NOM_COURS_DEAU'] == user_watershed]

#     if selected_ws.empty:
#         print(f"No watershed found with name '{user_watershed}'.")

#     ws_geom = selected_ws.geometry.unary_union 

#     fires_in_ws = fire_gdf[fire_gdf.geometry.within(ws_geom)]

#     return fires_in_ws


# def fx_filter_by_yearandsize(gdf):
#     min_year = int(input("Input the minimum year: "))
#     max_year = int(input("Input the maximum year: "))
#     min_size = int(input("Input the minimum size: "))
#     max_size = int(input("Input the maximum size: "))

#     gdf = gdf[(gdf["superficie"] >= min_size) & (gdf["superficie"] <= max_size) & ("an_origine" >= min_year) & (gdf["an_origine"] <= max_year)]
    
#     return gdf
# ########################################################################################################################



