import os
import zipfile
import requests
import geopandas as gpd



########### Scrapping Data from Donne Quebec" ############################################################################
# url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'

# # Makes a folder to save the data into 
# qcfires_after76_savefolder = 'qcfires_after76'
# os.makedirs(qcfires_after76_savefolder, exist_ok=True)

# # Creates the path to save the data into
# qcfires_after76_savepath = os.path.join(qcfires_after76_savefolder, 'FEUX_PROV_GPKG.zip')

# # pulls the zip file from donne quebec
# response = requests.get(url_qcfires_after76)
# with open(qcfires_after76_savepath, 'wb') as f:
#     f.write(response.content)

# # Extract the zip file
# with zipfile.ZipFile(qcfires_after76_savepath, 'r') as zip_ref:
#     zip_ref.extractall(qcfires_after76_savefolder)
#####################################################################################################################



######## Loading in the Data ##########################################################################################
path_qcfire_after76 = "/Users/tom/Documents/464/firecan/qcfire_after76"

gdf_qcfire_after76 = gpd.read_file(path_qcfire_after76)

print(gdf_qcfire_after76.columns)
########################################################################################################################
