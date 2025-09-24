from firecan_fx import fx_get_qc_data, fx_qc_firedata_loadmerge, fx_qc_watersheddata_load, fx_filter_fires_data # type: ignore

from flask import Flask, jsonify, request # type: ignore
import json






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


url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
watersheddata_zipname = "CE_bassin_multi.gdb.zip"
watersheddata_fgdbname = "CE_bassin_multi.gdb"

watersheddata_unzipped_file_path = fx_get_qc_data("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)
gdf_qc_watershed = fx_qc_watersheddata_load(watersheddata_unzipped_file_path)






# https://gemini.google.com/app/8afc07553070e9f7

# =========================================================
# Initialize Flask app and load data once
# =========================================================
app = Flask(__name__)

# =========================================================
# API Endpoint for Filtering
# =========================================================
@app.route('/fx_get_fires', methods=['GET'])
def fx_get_fires():
    # Get filter parameters from the URL query string
    min_year = request.args.get('min_year', 'None')
    max_year = request.args.get('max_year', 'None')
    min_size = request.args.get('min_size', 'None')
    max_size = request.args.get('max_size', 'None')
    distance_coords = request.args.get('distance_coords', 'None')
    distance_radius = request.args.get('distance_radius', 'None')
    watershed_name = request.args.get('watershed_name', 'None')


    # Call your filtering function with the request parameters
    filtered_data = fx_filter_fires_data(
        gdf_qc_fires,
        gdf_qc_watershed,
        min_year=min_year,
        max_year=max_year,
        min_size=min_size,
        max_size=max_size,
        distance_coords=distance_coords,
        distance_radius=distance_radius,
        watershed_name=watershed_name
    )

    # Convert the filtered GeoDataFrame to GeoJSON
    # Use to_json() with a custom GeoJSON writer for better control
    geojson_data = json.loads(filtered_data.to_json())
    
    # Return the GeoJSON data as a JSON response
    return jsonify(geojson_data)

# =========================================================
# Run the Flask app
# =========================================================
if __name__ == '__main__':
    # Add a catch-all route to serve the static HTML and CSS files
    @app.route('/')
    def serve_html():
        return app.send_static_file('firecan_web.html')

    app.run(debug=True)






















# # User inputs
# min_year = input("Input the minimum year: ")
# max_year = input("Input the maximum year: ")
# min_size = input("Input the minimum size: ")
# max_size = input("Input the maximum size: ")
# cord = input("Enter the coordiates of center point: ")
# radius = input("Enter radius in meters: ")
# user_watershed = input('Enter the name of the watershed: ')
# download_data = "Y" #input('Would you like to download the data?(Y/N): ')

# gdf_filtered_fires = fx_filter_fires_data(gdf_qc_fires, gdf_qc_watershed, min_year, max_year, min_size, max_size, cord, radius, user_watershed)

# if download_data == 'Y':
#     gdf_filtered_fires.drop(columns="geometry").to_csv("gdf_filtered_fires.csv", index=False)




































































# # Loading in and merging all QC fire data
# url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
# qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
# qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
# url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
# qcfires_before76_zipname = "FEUX_PROV_GPKG.zip"
# qcfires_before76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
# qcfires_before76_unzipped_file_path = fx_get_qc_data("qcfires_before76", url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
# qcfires_after76_unzipped_file_path = fx_get_qc_data("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)
# gdf_qc_fires = fx_qc_firedata_loadmerge(qcfires_after76_unzipped_file_path, qcfires_before76_unzipped_file_path)


# action = input("What would you like to do \n 1: Filter by year \n 2: Filter by size \n 3: Filter by year and size \n 4: Filter by distance \n 5: Filter By watershed \n input: ")
# if action == "1":
#     gdf_qc_fires_filtered_by_year = fx_filter_by_year(gdf_qc_fires)
#     download_action_1 = input("Would you like to download the filtered data? (Y/N): ") 
#     if download_action_1 == "Y":
#         gdf_qc_fires_filtered_by_year.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_year.csv", index=False)
# elif action == "2":
#     gdf_qc_fires_filtered_by_size = fx_filter_by_size(gdf_qc_fires)
#     download_action_2 = input("Would you like to download the filtered data? (Y/N): ") 
#     if download_action_2 == "Y":
#         gdf_qc_fires_filtered_by_size.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_size.csv", index=False)
# elif action == "3":
#     gdf_qc_fires_filtered_by_yearandsize = fx_filter_by_yearandsize(gdf_qc_fires)
#     download_action_3 = input("Would you like to download the filtered data? (Y/N): ") 
#     if download_action_3 == "Y":
#         gdf_qc_fires_filtered_by_yearandsize.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_yearandsize.csv", index=False)
# elif action == "4":
#     gdf_qc_fires_filtered_by_distance = fx_filter_by_distance(gdf_qc_fires)
#     download_action_4 = input("Would you like to download the filtered data? (Y/N): ") 
#     if download_action_4 == "Y":
#         gdf_qc_fires_filtered_by_distance.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_distance.csv", index=False)
# elif action == "5":
#     url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
#     watersheddata_zipname = "CE_bassin_multi.gdb.zip"
#     watersheddata_fgdbname = "CE_bassin_multi.gdb"
#     watersheddata_unzipped_file_path = fx_get_qc_data("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)
    
#     gdf_qc_watershed = fx_qc_watersheddata_load(watersheddata_unzipped_file_path)
   
#     gdf_qc_fires_filtered_by_watershed = fx_filter_by_watershed(gdf_qc_fires, gdf_qc_watershed)
#     download_action_5 = input("Would you like to download the filtered data? (Y/N): ") 
#     if download_action_5 == "Y":
#         gdf_qc_fires_filtered_by_watershed.drop(columns="geometry").to_csv("gdf_qc_fires_filtered_by_watershed.csv", index=False)
