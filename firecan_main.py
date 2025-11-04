from firecan_fx import convert_m_4326deg,fx_merge_provincial_fires,timenow,fx_get_on_fire_data,create_data_folder,fx_get_qc_fire_data,fx_filter_fires_data,fx_download_json,fx_download_csv,timenow, fx_download_gpkg, fx_get_qc_watershed_data
from flask import Flask, request # type: ignore
import json
import sys
import geopandas as gpd

create_data_folder()
MAX_SIZE_MB = 8
print('------------------------Starting data pre-loading. This may take a few minutes...', timenow(),'------------------------')                                      # This section here loads in the data, it uses the scrap donne quebec function and the process qc fire data fuction
gdf_qc_fires = fx_get_qc_fire_data()
gdf_qc_watershed_data = fx_get_qc_watershed_data()

gdf_on_fires = fx_get_on_fire_data()


gdf_fires = fx_merge_provincial_fires(gdf_qc_fires, gdf_on_fires)



print('---------------Data pre-loading complete. The app is now ready to serve requests.', timenow(),'------------------------')




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
    qcprovinceflag = request.args.get('qcprovinceflag', None)
    onprovinceflag = request.args.get('onprovinceflag', None)    
    is_download_requested = request.args.get('download', '0') == '1'                                      # Checks if we should be displaying data or downloading it
    downloadformat = request.args.get('downloadFormat', None)

    


    print(timenow(),'Filtering Data')                                                                                 # Uses the filtering fire function to return a dataset with only the fires the user wants 
    results= fx_filter_fires_data(
                                            gdf_fires,
                                            gdf_qc_watershed_data,
                                            qcprovinceflag,
                                            onprovinceflag,
                                            min_year=min_year,
                                            max_year=max_year,
                                            min_size=min_size,
                                            max_size=max_size,
                                            distance_coords=distance_coords,
                                            distance_radius=distance_radius,
                                            watershed_name=watershed_name
                                        )
    print(timenow(),'Done Filtering Data')

    filtered_data = results["filtered_gdf"]
    watershed_polygon = results["watershed_polygon"]
    userpoint = results["user_point"]
    bufferdeg = results["buffer_geom"]

        
    if is_download_requested:                                                                                 # If downlaod request is tru we are going to run one of the downloading fucntions
        if downloadformat == 'json':

            return fx_download_json(filtered_data)
        elif downloadformat == 'csv':
            return fx_download_csv(filtered_data)
        elif downloadformat == 'gpkg':
            return fx_download_gpkg(filtered_data)
    else:                                                                                       # IF download request is not true we are going to convert ot geojson and return it (send it) to my java script
        print(timenow(),'Converting to geojson',filtered_data.shape)

        polygon_tol = request.args.get('polygon_tol', None)
        polygon_tol = float(polygon_tol)
        polygon_tol_deg = convert_m_4326deg(polygon_tol, 45)

        filtered_data["geometry"] = filtered_data["geometry"].simplify(tolerance=polygon_tol_deg, preserve_topology=True)         # add precision option to change how good the polygons look vs load time
        geojson_fires = json.loads(filtered_data.to_json())                                                     # BOTTLENECK
        print(timenow(),'Done Converting to geojson')    

        geojson_point = json.loads(userpoint.to_json()) if userpoint is not None else None
        geojson_buffer = json.loads(bufferdeg.to_json()) if bufferdeg is not None else None
        
        if watershed_polygon is not None:
            ws_gs = gpd.GeoSeries([watershed_polygon], crs=gdf_qc_watershed_data.crs)
            ws_gs = ws_gs.to_crs("EPSG:4326")
            geojson_watershedpolygon = json.loads(ws_gs.to_json())
        else:
            geojson_watershedpolygon = None

        combined_geojson = {
            "fires": geojson_fires,
            "user_point": geojson_point,
            "user_buffer": geojson_buffer,
            "watershed_polygon" : geojson_watershedpolygon
        }


        MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
        geojson_bytes = len(json.dumps(combined_geojson).encode('utf-8'))
        if geojson_bytes > MAX_SIZE_BYTES:
            print(f'{geojson_bytes/1000000} is too big')
            return {"error": f"Data too large to load ({geojson_bytes / 1024 / 1024:.2f} MB). Please re-fresh and narrow your filter."}, 413


        return json.dumps(combined_geojson)

                                
@app.route('/')
def serve_html():
    return app.send_static_file('firecan_web.html')

if __name__ == '__main__':
    app.run(debug=False)



