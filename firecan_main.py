import os
import zipfile
import requests
import geopandas as gpd
from pathlib import Path
import pandas as pd
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
        print("YAY Folder already exists:", savefolder)

    if not zip_path.exists():
        print(dataname, "is not downloaded, downloading now, this may take a few minutes")
        response = requests.get(url)
        with open(savepath, 'wb') as f:
            f.write(response.content)
        print("DONE Downloading the Data for", dataname)
    else:
        print("YAY ZIP", dataname,"already exists:", zip_path)
    
    if not unzipped_file_path.exists():
        print("Unzipping the Data now")
        with zipfile.ZipFile(savepath, 'r') as zip_ref:
            zip_ref.extractall(savefolder)
        print("DONE! unzipping the data, data is located in", savepath)
    else:
        print("YAY Unzipped",dataname, "file already exists:", unzipped_file_path)

    return unzipped_file_path


url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
qcfires_after76_unzipped_file_path = fx_get_qc_data("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)

url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_after76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
qcfires_before76_unzipped_file_path = fx_get_qc_data("qcfires_before76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)

################################################################################################















############## LOAD IN AND MERGE BEFORE AND AFTER QC FIRE DATASET ##################################################################################
def fx_qc_loadmerge_data(afterpath, beforepath):
    after = gpd.read_file(afterpath, layer="feux_prov")
    after = after.rename(columns={"geoc_fmj": "geoc"})
    after = after.drop(columns=["perturb", "an_perturb", "part_str"])

    before = gpd.read_file(beforepath, layer="feux_anciens_prov")
    before = before.rename(columns={"geoc_fan": "geoc"})

    merged = gpd.GeoDataFrame(
        pd.concat([before, after], ignore_index=True),
        geometry="geometry"  
    )
    print(after.head())
    print(before.head())

    return merged

gdf_qc_fires = fx_qc_loadmerge_data(qcfires_after76_unzipped_file_path, qcfires_before76_unzipped_file_path)

print(gdf_qc_fires.shape)


########################################################################################################################




############ FILTERING DATA #############################################################################################################

def fx_filter_by_year(gdf):
    min_year = input("Input the minimum year")
    max_year = input("Input the maximum year")
    year_filtered_data = gdf[gdf["TYPE"] > min_year and gdf["TYPE"] < max_year]

def fx_filter_by_size(gdf):
    min_size = input("Input the minimum size")
    max_size = input("Input the maximum size")
    size_filtered_data = gdf[gdf["TYPE"] > min_size and gdf["TYPE"] < max_size]



########################################################################################################################
