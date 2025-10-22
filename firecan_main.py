from firecan_fx import fx_scrape_donneqc,fx_qc_processfiredata,fx_filter_fires_data,fx_download_json,fx_download_csv# type: ignore
from flask import Flask, request # type: ignore
from datetime import datetime




print('Starting data pre-loading. This may take a few minutes...')                                      # This section here loads in the data, it uses the scrap donne quebec function and the process qc fire data fuction

url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_zipname = 'FEUX_PROV_GPKG.zip'                                                          # In this case both zip names are the same but must still specify it in the fuctino so we can use the fuction for other datasets like the watershed data
qcfires_after76_gpkgname = 'FEUX_PROV.gpkg'
url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_before76_zipname = 'FEUX_PROV_GPKG.zip'
qcfires_before76_gpkgname = 'FEUX_ANCIENS_PROV.gpkg'
qcfires_before76_unzipped_file_path = fx_scrape_donneqc('qcfires_before76', url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
qcfires_after76_unzipped_file_path = fx_scrape_donneqc('qcfires_after76', url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)


gdf_qc_fires, gdf_qc_watershed_data = fx_qc_processfiredata(qcfires_before76_unzipped_file_path,qcfires_after76_unzipped_file_path)


print('Data pre-loading complete. The app is now ready to serve requests.')








# =========================================================
# FLASK
# =========================================================
app = Flask(__name__, static_folder='static')                                                      # This starts FLASK which allows me to talk back and forth with my web page and my java script

@app.route('/fx_main', methods=['GET'])
def fx_main():                                                                                    # This is the main fuctino that is run when my python is called by Flask 
    min_year = request.args.get('min_year', None)                                                    # This section here assings varibales for all the user inputed filtering conditions
    max_year = request.args.get('max_year', None)                                     
    min_size = request.args.get('min_size', None)
    max_size = request.args.get('max_size', None)
    distance_coords = request.args.get('distance_coords', None)
    distance_radius = request.args.get('distance_radius', None)
    watershed_name = request.args.get('watershed_name', None)
    is_download_requested = request.args.get('download', '0') == '1'                                      # Checks if we should be displaying data or downloading it
    jsondownlaod = request.args.get('jsondownload', None)

    print('Filtering Data')                                                                                 # Uses the filtering fire function to return a dataset with only the fires the user wants 
    filtered_data = fx_filter_fires_data(
                                            gdf_qc_fires,
                                            gdf_qc_watershed_data,
                                            min_year=min_year,
                                            max_year=max_year,
                                            min_size=min_size,
                                            max_size=max_size,
                                            distance_coords=distance_coords,
                                            distance_radius=distance_radius,
                                            watershed_name=watershed_name
                                        )
    print('Done Filtering Data')

    

    
    if is_download_requested:                                                                                 # If downlaod request is tru we are going to run one of the downloading fucntions
        if jsondownlaod == 'true':
            return fx_download_json(filtered_data)
        else:
            return fx_download_csv(filtered_data)
    else:    
        now = datetime.now().strftime('%H:%M:%S')                                                                                                 # IF download request is not true we are going to convert ot geojson and return it (send it) to my java script
        print('Converting to geojson (',now,')',filtered_data.shape)
        filtered_data["geometry"] = filtered_data["geometry"].simplify(tolerance=0.001, preserve_topology=True)         # add precision option to change how good the polygons look vs load time
        geojson_str = filtered_data.to_json()
        now = datetime.now().strftime('%H:%M:%S')                                                     # BOTTLENECK
        print('Done Converting to geojson (',now,')')
        return geojson_str
                                   

@app.route('/')
def serve_html():
    return app.send_static_file('firecan_web.html')

if __name__ == '__main__':
    app.run(debug=True)



