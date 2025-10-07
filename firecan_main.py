from firecan_fx import fx_scrape_donneqc,fx_qc_processfiredata,fx_filter_fires_data,fx_download_json,fx_download_csv
from flask import Flask, jsonify, request
import json



#### Loading in data, just QC at this point 

print("Starting data pre-loading. This may take a few minutes...")

url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
qcfires_after76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_after76_gpkgname = "FEUX_PROV.gpkg"
url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
qcfires_before76_zipname = "FEUX_PROV_GPKG.zip"
qcfires_before76_gpkgname = "FEUX_ANCIENS_PROV.gpkg"
qcfires_before76_unzipped_file_path = fx_scrape_donneqc("qcfires_before76", url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
qcfires_after76_unzipped_file_path = fx_scrape_donneqc("qcfires_after76", url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)

# Processing QC Fire data
gdf_qc_fires = fx_qc_processfiredata(qcfires_before76_unzipped_file_path,qcfires_after76_unzipped_file_path)


print("Data pre-loading complete. The app is now ready to serve requests.")








# =========================================================
# Initialize Flask app and define routes
# =========================================================
app = Flask(__name__, static_folder='static') # Specify the static folder

@app.route('/fx_main', methods=['GET'])
def fx_main():
    return jsonify(gdf_qc_fires)         # Return the GeoJSON data as a JSON response

@app.route('/')
def serve_html():
    return app.send_static_file('firecan_web.html')

if __name__ == '__main__':
    app.run(debug=True)



