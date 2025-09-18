import os
import zipfile
import requests
import geopandas as gpd
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import fiona
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
        print("Zipped Data Exists For", dataname)
    
    if not unzipped_file_path.exists():
        print("Unzipping the Data now")
        with zipfile.ZipFile(savepath, 'r') as zip_ref:
            zip_ref.extractall(savefolder)
        print("DONE! unzipping the data, data is located in", savepath)
    else:
        print("Unzipped Data Exists For", dataname)

    return unzipped_file_path
################################################################################################







############## LOAD IN AND MERGE BEFORE AND AFTER QC FIRE DATASET ##################################################################################
def fx_qc_firedata_loadmerge(afterpath, beforepath):
    print("Loading in the Data")
    after = gpd.read_file(afterpath, layer="feux_prov")
    after = after.rename(columns={"geoc_fmj": "geoc"})
    after = after.drop(columns=["perturb", "an_perturb", "part_str"])

    before = gpd.read_file(beforepath, layer="feux_anciens_prov")
    before = before.rename(columns={"geoc_fan": "geoc"})
    print("merging the data")
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








############ FILTERING DATA #############################################################################################################
def fx_filter_by_year(gdf):
    min_year = int(input("Input the minimum year: "))
    max_year = int(input("Input the maximum year: "))

    gdf = gdf[(gdf["an_origine"] >= min_year) & (gdf["an_origine"] <= max_year)]
    
    return gdf


def fx_filter_by_size(gdf):
    min_size = int(input("Input the minimum size: "))
    max_size = int(input("Input the maximum size: "))

    gdf = gdf[(gdf["superficie"] >= min_size) & (gdf["superficie"] <= max_size)]

    return gdf


def fx_filter_by_yearandsize(gdf):
    min_year = int(input("Input the minimum year: "))
    max_year = int(input("Input the maximum year: "))
    min_size = int(input("Input the minimum size: "))
    max_size = int(input("Input the maximum size: "))

    gdf = gdf[(gdf["superficie"] >= min_size) & (gdf["superficie"] <= max_size) & ("an_origine" >= min_year) & (gdf["an_origine"] <= max_year)]
    
    return gdf


def fx_filter_by_distance(gdf):
    cord = input("Enter the coordiates of center point: ")
    radius = float(input("Enter radius in meters: "))

    lat, lon = map(float, cord.split(","))


    user_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")
    user_point_proj = user_point.to_crs(gdf.crs)
    buffer_geom = user_point_proj.buffer(radius)

    gdf = gdf[gdf.geometry.intersects(buffer_geom.iloc[0])]
    # possible_idx = list(gdf.sindex.intersection(buffer_geom.iloc[0].bounds))
    # gdf_candidate = gdf.iloc[possible_idx]
    # gdf = gdf_candidate[gdf_candidate.geometry.intersects(buffer_geom.iloc[0])]

    return gdf


def fx_filter_by_watershed(fire_gdf, watershed_gdf):
    user_watershed = input('Enter the name of the watershed: ')
    selected_ws = watershed_gdf[watershed_gdf['NOM_COURS_DEAU'] == user_watershed]

    if selected_ws.empty:
        print(f"No watershed found with name '{user_watershed}'.")

    ws_geom = selected_ws.geometry.unary_union 

    fires_in_ws = fire_gdf[fire_gdf.geometry.within(ws_geom)]

    return fires_in_ws
########################################################################################################################




# Loading in and merging all QC fire data
url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_before76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_before76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
qcfires_before76_unzipped_file_path = fx_get_qc_data("qcfires_before76", url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
qcfires_after76_unzipped_file_path = fx_get_qc_data("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)
gdf_qc_fires = fx_qc_firedata_loadmerge(qcfires_after76_unzipped_file_path, qcfires_before76_unzipped_file_path)


action = input("What would you like to do \n 1: Filter by year \n 2: Filter by size \n 3: Filter by year and size \n 4: Filter by distance \n 5: Filter By watershed \n input: ")
if action == "1":
    gdf_qc_fires_filtered_by_year = fx_filter_by_year(gdf_qc_fires)
    download_action_1 = input("Would you like to download the filtered data? (Y/N): ") 
    if download_action_1 == "Y":
        gdf_qc_fires_filtered_by_year.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_year.csv", index=False)
elif action == "2":
    gdf_qc_fires_filtered_by_size = fx_filter_by_size(gdf_qc_fires)
    download_action_2 = input("Would you like to download the filtered data? (Y/N): ") 
    if download_action_2 == "Y":
        gdf_qc_fires_filtered_by_size.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_size.csv", index=False)
elif action == "3":
    gdf_qc_fires_filtered_by_yearandsize = fx_filter_by_yearandsize(gdf_qc_fires)
    download_action_3 = input("Would you like to download the filtered data? (Y/N): ") 
    if download_action_3 == "Y":
        gdf_qc_fires_filtered_by_yearandsize.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_yearandsize.csv", index=False)
elif action == "4":
    gdf_qc_fires_filtered_by_distance = fx_filter_by_distance(gdf_qc_fires)
    download_action_4 = input("Would you like to download the filtered data? (Y/N): ") 
    if download_action_4 == "Y":
        gdf_qc_fires_filtered_by_distance.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_distance.csv", index=False)
elif action == "5":
    url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
    watersheddata_zipname = "CE_bassin_multi.gdb.zip"
    watersheddata_fgdbname = "CE_bassin_multi.gdb"
    watersheddata_unzipped_file_path = fx_get_qc_data("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)
    
    gdf_qc_watershed = fx_qc_watersheddata_load(watersheddata_unzipped_file_path)
   
    gdf_qc_fires_filtered_by_watershed = fx_filter_by_watershed(gdf_qc_fires, gdf_qc_watershed)
    download_action_5 = input("Would you like to download the filtered data? (Y/N): ") 
    if download_action_5 == "Y":
        gdf_qc_fires_filtered_by_watershed.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_watershed.csv", index=False)
