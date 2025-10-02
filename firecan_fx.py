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
    # Loads in before+after data, renames column to merge, merges, downlaods watersehd data, reproject data, merges fires and watershed data
    # Skip this code and load data direclty IF it exists AND It is reprojected AND it has watershed column 
    print("Loading in unprocessed data ... This may take a few minutes ...")
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



    print("Reprojecting the data")
    is_wgs84 = merged_data.crs.to_epsg() == 4326
    if is_wgs84:
        print("The data is already in EPSG:4326 (WGS 84).")
    else:
        print("Reprojecting Data")
        merged_data = merged_data.to_crs(epsg=4326)    



    print("Getting Watershed Data")
    url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
    watersheddata_zipname = "CE_bassin_multi.gdb.zip"
    watersheddata_fgdbname = "CE_bassin_multi.gdb"
    qcwatershed_unzipped_file_path = fx_scrape_donneqc("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)                   
    
    layers = fiona.listlayers(qcwatershed_unzipped_file_path)
    watershed_data = gpd.read_file(qcwatershed_unzipped_file_path, layer=layers[1])
    watershed_data = watershed_data.drop(columns=["NO_COURS_DEAU", "NOM_COURS_DEAU_MINUSCULE", "NIVEAU_BASSIN", "ECHELLE", "SUPERF_KM2", "NO_SEQ_BV_PRIMAIRE", "NOM_BV_PRIMAIRE", "NO_REG_HYDRO", "NOM_REG_HYDRO_ABREGE", "Shape_Length", "Shape_Area"]) # might want shape length and share area later



    print("Reprojecting the data")
    is_wgs84 = merged_data.crs.to_epsg() == 4326
    if is_wgs84:
        print("The data is already in EPSG:4326 (WGS 84).")
    else:
        print("Reprojecting Data")
        merged_data = merged_data.to_crs(epsg=4326)  

    is_wgs84 = watershed_data.crs.to_epsg() == 4326
    if is_wgs84:
        print("The data is already in EPSG:4326 (WGS 84).")
    else:
        print("Reprojecting Data")
        watershed_data = watershed_data.to_crs(epsg=4326)  


    # THIS TAKES SOOOOOOO LONG
    # print("Adding watershed column to fires")
    # merged_data = gpd.sjoin(
    # merged_data, 
    # watershed_data[['NOM_COURS_DEAU', 'geometry']],  # keep only watershed name & geometry
    # how="left",                                      # keep all fires
    # predicate="intersects"                           # or "within" if fires are fully inside watersheds
    # )
    # merged_data.drop(columns=["geometry"]).head(10).to_csv("merged_data.csv", index=False)





 





url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_before76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_before76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
qcfires_before76_unzipped_file_path = fx_scrape_donneqc("qcfires_before76", url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
qcfires_after76_unzipped_file_path = fx_scrape_donneqc("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)

fx_qc_processfiredata(qcfires_before76_unzipped_file_path,qcfires_after76_unzipped_file_path)