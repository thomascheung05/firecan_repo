import os
import zipfile
import requests
import geopandas as gpd
from pathlib import Path
import pandas as pd
work_dir  = Path.cwd()




########## GETTING QUEBEC DATA AFTER 1976 ############################################################################

qcfires_after76_savefolder = work_dir / "qcfires_after76"
qcfires_after76_zip_path = qcfires_after76_savefolder / "FEUX_PROV_GPKG.zip"
qcfires_after76_unzipped_file = qcfires_after76_savefolder / "FEUX_PROV.gpkg"
url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_savepath = os.path.join(qcfires_after76_savefolder, 'FEUX_PROV_GPKG.zip')


if not qcfires_after76_savefolder.exists():
    qcfires_after76_savefolder.mkdir(parents=True, exist_ok=True)
    print("Created folder:", qcfires_after76_savefolder)
else:
    print("YAY Folder already exists:", qcfires_after76_savefolder)

if not qcfires_after76_zip_path.exists():
    print('QC Fire Data after 76 is not downloaded, downloading now, this may take a few minutes')
    response = requests.get(url_qcfires_after76)
    with open(qcfires_after76_savepath, 'wb') as f:
        f.write(response.content)
    print("DONE! Downloading the Data")
else:
    print("YAY ZIP QC fires after 76 already exists:", qcfires_after76_zip_path)

if not qcfires_after76_unzipped_file.exists():
    print("Unzipping the Data now")
    with zipfile.ZipFile(qcfires_after76_savepath, 'r') as zip_ref:
        zip_ref.extractall(qcfires_after76_savefolder)
    print("DONE! unzipping the data data is located in", qcfires_after76_savepath)
else:
    print("YAY Unzipped QC fires after 76 file already exists:", qcfires_after76_unzipped_file)

#####################################################################################################################

########## GETTING QUEBEC DATA BEFORE 1976 ############################################################################

qcfires_before76_savefolder = work_dir / "qcfires_before76"
qcfires_before76_zip_path = qcfires_before76_savefolder / "FEUX_PROV_GPKG.zip"
qcfires_before76_unzipped_file = qcfires_before76_savefolder / "FEUX_ANCIENS_PROV.gpkg"
url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_before76_savepath = os.path.join(qcfires_before76_savefolder, 'FEUX_PROV_GPKG.zip')


if not qcfires_before76_savefolder.exists():
    qcfires_before76_savefolder.mkdir(parents=True, exist_ok=True)
    print("Created folder:", qcfires_before76_savefolder)
else:
    print("YAY Folder already exists:", qcfires_before76_savefolder)

if not qcfires_before76_zip_path.exists():
    print('QC Fire Data before 76 is not downloaded, downloading now, this may take a few minutes')
    response = requests.get(url_qcfires_before76)
    with open(qcfires_before76_savepath, 'wb') as f:
        f.write(response.content)
    print("DONE! Downloading the Data")
else:
    print("YAY ZIP QC fires before 76 already exists:", qcfires_before76_zip_path)

if not qcfires_before76_unzipped_file.exists():
    print("Unzipping the Data now")
    with zipfile.ZipFile(qcfires_before76_savepath, 'r') as zip_ref:
        zip_ref.extractall(qcfires_before76_savefolder)
    print("DONE! unzipping the data data is located in", qcfires_before76_savepath)
else:
    print("YAY Unzipped QC fires before 76 file already exists:", qcfires_before76_unzipped_file)

#####################################################################################################################


######## LOADING IN AND MERGING QC FIRE DATA ##########################################################################################
gdf_qcfire_after76 = gpd.read_file(qcfires_after76_unzipped_file, layer="feux_prov")
gdf_qcfire_after76 = gdf_qcfire_after76.rename(columns={"geoc_fmj": "geoc"})
gdf_qcfire_after76 = gdf_qcfire_after76.drop(columns=["perturb", "an_perturb", "part_str"])

gdf_qcfire_before76 = gpd.read_file(qcfires_before76_unzipped_file, layer="feux_anciens_prov")
gdf_qcfire_before76 = gdf_qcfire_before76.rename(columns={"geoc_fan": "geoc"})

gdf_qcfire = gpd.GeoDataFrame(
    pd.concat([gdf_qcfire_before76, gdf_qcfire_after76], ignore_index=True),
    geometry="geometry"  # make sure the geometry column is correctly recognized
)

print(gdf_qcfire_after76.shape)   
print(gdf_qcfire_before76.shape)     
print(gdf_qcfire.shape)     
########################################################################################################################
