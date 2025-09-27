from firecan_fx import fx_get_qc_data, fx_qc_firedata_loadmerge, fx_qc_watersheddata_load, fx_filter_fires_data # type: ignore
from flask import Flask, jsonify, request, send_file  # type: ignore
import json
from shapely.geometry import MultiPolygon 
from shapely.ops import transform
import io


#### Loading in data, just QC at this point 

# print("Starting data pre-loading. This may take a few minutes...")

# url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
# qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
# qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
# url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
# qcfires_before76_zipname = "FEUX_PROV_GPKG.zip"
# qcfires_before76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
# qcfires_before76_unzipped_file_path = fx_get_qc_data("qcfires_before76", url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
# qcfires_after76_unzipped_file_path = fx_get_qc_data("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)
# gdf_qc_fires = fx_qc_firedata_loadmerge(qcfires_after76_unzipped_file_path, qcfires_before76_unzipped_file_path)



# url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
# watersheddata_zipname = "CE_bassin_multi.gdb.zip"
# watersheddata_fgdbname = "CE_bassin_multi.gdb"
# watersheddata_unzipped_file_path = fx_get_qc_data("watershed_data", url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)
# gdf_qc_watershed = fx_qc_watersheddata_load(watersheddata_unzipped_file_path)

# print("Data pre-loading complete. The app is now ready to serve requests.")








# =========================================================
# Initialize Flask app and define routes
# =========================================================
app = Flask(__name__, static_folder='static') # Specify the static folder

@app.route('/fx_main', methods=['GET'])
def fx_main():
    # Get filter parameters from the URL query string
    min_year = request.args.get('min_year', None)
    max_year = request.args.get('max_year', None)
    min_size = request.args.get('min_size', None)
    max_size = request.args.get('max_size', None)
    distance_coords = request.args.get('distance_coords', None)
    distance_radius = request.args.get('distance_radius', None)
    watershed_name = request.args.get('watershed_name', None)
    is_download_requested = request.args.get('download', '0') == '1'
    jsondownlaod = request.args.get('jsondownload', None)

    # # Filtering the data 
    # filtered_data = fx_filter_fires_data(
    #                                         gdf_qc_fires,
    #                                         gdf_qc_watershed,
    #                                         min_year=min_year,
    #                                         max_year=max_year,
    #                                         min_size=min_size,
    #                                         max_size=max_size,
    #                                         distance_coords=distance_coords,
    #                                         distance_radius=distance_radius,
    #                                         watershed_name=watershed_name
    #                                     )

    
    # filtered_data = filtered_data.to_crs(epsg=4326)                       # Reprojecting the data

    
    # if is_download_requested:
    #     if jsondownlaod == "true":
    #         geojson_data = json.loads(filtered_data.to_json())                    # Convert the filtered GeoDataFrame to GeoJSON
    #         geojson_string = json.dumps(geojson_data) 
        
    #         geojson_buffer = io.BytesIO(geojson_string.encode('utf-8'))                         # Create an in-memory buffer to hold the file content
    #         geojson_buffer.seek(0)
            
    #         return send_file(                                               # Send the file back to the browser as an attachment

    #             geojson_buffer,
                
    #             mimetype='application/json',                    # CRITICAL: Change MIME type to 'application/json' or 'application/geo+json'
    #             as_attachment=True,
    #             download_name='firecan_filtered_data.geojson'                   # CRITICAL: Change file extension to '.geojson'

    #         )
        # else:
        #     csv_buffer = io.BytesIO()
        #     filtered_data.to_csv(csv_buffer, index=False, encoding="utf-8")
        #     csv_buffer.seek(0)
            
        #     return send_file(                                                   # Return the file as an attachment to the user's Downloads folder

        #         csv_buffer,
        #         mimetype='text/csv',
        #         as_attachment=True,
        #         download_name='firecan_filtered_data.csv'
        #     ) 
    # else:       
    #     geojson_data = json.loads(filtered_data.to_json())                    # Convert the filtered GeoDataFrame to GeoJSON

    #     return jsonify(geojson_data)                                          # Return the GeoJSON data as a JSON response

@app.route('/')
def serve_html():
    return app.send_static_file('firecan_web.html')

if __name__ == '__main__':
    app.run(debug=True)