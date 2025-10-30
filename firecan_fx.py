import zipfile
import json
import requests
import geopandas as gpd
from datetime import datetime
from flask import request, send_file   # type: ignore
import io
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import fiona  # type: ignore
import numpy as np
import requests
import json
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from pathlib import Path
from datetime import datetime
import sys
import math
work_dir  = Path.cwd()

                                                                                        # A lot of the code here is pretty simple data manipulaiton mostly filtering
                                                                                        # AI was used for the general 'how do i do this' stuff but the code has been changed so much not a lot of still left over form the AI with the eception of the downloading functions, which are mostly AI as they are pretty straightforward and there wasnt much to change
                                                                                        # Almost all of the structure of this code is mine, like the download only if it doesnt exist and the process if it the processesed data doenst already exist
                                                                                        # AI showed me how to apply multiple filters at once which is a pretty integral part of the script



def timenow():
    return datetime.now().strftime('%H:%M:%S')


def repojectdata(data, targetcrs):
    is_targercrs = data.crs.to_epsg() == targetcrs

    if is_targercrs:
        print(f'The data is already in {targetcrs}')
        return data
    else:
        data = data.to_crs(targetcrs)    
        print('The data has been reprojectd')    
        return data


def create_data_folder():
    data_folder_path = work_dir / 'data'
    if not data_folder_path.exists(): 
        data_folder_path.mkdir(parents=True, exist_ok=True)



def convert_m_4326deg(meters, lat):
    deg_lat = meters / 111320.0
    deg_lon = meters / (111320.0 * math.cos(math.radians(lat)))

    larger = max(deg_lat, deg_lon)
    return larger





def fx_scrape_donneqc(dataname, url, zipname, gpkgname):                                           # Scraps donne quebec to get quebef fire data, outputs the path to the data file
    print(f'.. {timenow()} Downloading From Donne Quebec')    
    savefolder = work_dir / "data" / dataname
    zip_path = savefolder / zipname                                                                # Name of zip file depends on the data being dowloaded, for fire data its the same but not for watershed data
    unzipped_file_path = savefolder / gpkgname                                                     # This differs between quebec fire data, and also watershed data set

    if not unzipped_file_path.exists():        # Checks if the GPKG file exists, if not it will create a folder and downlaod it 
        print(f'.... {timenow()} The data does not exist for {dataname} Downloading now')         
        savefolder.mkdir(parents=True, exist_ok=True)
        response = requests.get(url)                                                                # AI showed me how to do this
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:                                            # The data come in a zipfile so must unzip it
            zip_ref.extractall(savefolder)
        print(f'...... {timenow()} The data for {dataname} has been dowloaded')
    else:                                                                                          # If it already exists we do nothing as we already created the path that needs to be returned outside of the IF 
        print(f'...... {timenow()} The data for {dataname} is already downloaded')                

    return unzipped_file_path


def fx_get_qc_fire_data():   
    print('Getting QC Fire Data')                                               # Loads in QC fire data (beofre and after), merges the two datasets, reprojects it, then saves it as a parquet so we only have to do this once 
    url_qcfires_after76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_PROV_GPKG.zip'
    qcfires_after76_zipname = 'FEUX_PROV_GPKG.zip'                                                          # In this case both zip names are the same but must still specify it in the fuctino so we can use the fuction for other datasets like the watershed data
    qcfires_after76_gpkgname = 'FEUX_PROV.gpkg'
    url_qcfires_before76 = 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/FEUX_ANCIENS_PROV_GPKG.zip'
    qcfires_before76_zipname = 'FEUX_PROV_GPKG.zip'
    qcfires_before76_gpkgname = 'FEUX_ANCIENS_PROV.gpkg'
    qcfires_before76_unzipped_file_path = fx_scrape_donneqc('qcfires_before76', url_qcfires_before76, qcfires_before76_zipname, qcfires_before76_gpkgname)
    qcfires_after76_unzipped_file_path = fx_scrape_donneqc('qcfires_after76', url_qcfires_after76, qcfires_after76_zipname, qcfires_after76_gpkgname)

    qc_processed_data_folder_path = work_dir / "data" / 'qc_processed_data'
    qc_processed_data_path = qc_processed_data_folder_path / 'qc_processed_fire_data.parquet'

    if not qc_processed_data_path.exists():
        print(f'........ {timenow()} Pre-Processing data now')
        qc_processed_data_folder_path.mkdir(parents=True, exist_ok=True)
        print(f'.......... {timenow()} Loading and Merging QC data')
        before_data = gpd.read_file(qcfires_before76_unzipped_file_path, layer= 'feux_anciens_prov')
        after_data = gpd.read_file(qcfires_after76_unzipped_file_path, layer= 'feux_prov')

        after_data = after_data.drop(columns=['geoc_fmj','exercice', 'origine', 'met_at_str', 'shape_length', 'shape_area'])        # might want shape length and share area later
        before_data = before_data.drop(columns=['geoc_fan','exercice', 'origine', 'met_at_str', 'shape_length', 'shape_area'])        # might want shape length and share area later



        after_data = after_data.drop(columns=['perturb', 'an_perturb', 'part_str'])
        merged_data = gpd.GeoDataFrame(pd.concat([before_data, after_data], ignore_index=True),geometry='geometry'  )
        merged_data['an_origine'] = pd.to_numeric(merged_data['an_origine'], errors='coerce')
        merged_data['superficie'] = pd.to_numeric(merged_data['superficie'], errors='coerce')
        merged_data = merged_data.rename(columns={'an_origine': 'fire_year'})
        merged_data = merged_data.rename(columns={'superficie': 'fire_size'})
        merged_data["province"] = "qc"
        
        print(f'.......... {timenow()} Re-Projecting Data')
        merged_data = repojectdata(merged_data, 4326)

        print(f'............ {timenow()} Done Pre-Processing saving for later use')
        merged_data.to_parquet(qc_processed_data_path)

    else:               
        print(f'........ {timenow()} The QC data is already processed Loading in now')                                                                                                # If there fire data is already processed we just load it in here
        merged_data = gpd.read_parquet(qc_processed_data_path)

    return merged_data


def fx_get_qc_watershed_data():                                                                                        # This function gets the watershed data by using the scrap donne quebec function, it then reads it in, drops some columns, and reprojects it
    print('Getting Watershed Data')
    url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
    watersheddata_zipname = 'CE_bassin_multi.gdb.zip'
    watersheddata_fgdbname = 'CE_bassin_multi.gdb'

    qcwatershed_unzipped_file_path = fx_scrape_donneqc('qcwatershed_data', url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)                   
        
    qc_processed_data_folder_path = work_dir / "data" / 'qc_processed_data'
    qc_watershed_data_path = qc_processed_data_folder_path / 'qc_watershed_data.parquet'
    qc_watershed_data_path_json = work_dir/ 'static' / 'qc_watershed_data.geojson'

    if not qc_watershed_data_path.exists() or not qc_watershed_data_path_json.exists():
        print(f'...... {timenow()} Pre-Processing the Watershed Data') 
        layers = fiona.listlayers(qcwatershed_unzipped_file_path)
        watershed_data = gpd.read_file(qcwatershed_unzipped_file_path, layer=layers[1])
        watershed_data = watershed_data[watershed_data['NIVEAU_BASSIN'] == 1]
        watershed_data = watershed_data.drop(columns=['NO_COURS_DEAU','NO_SEQ_COURS_DEAU','IDENTIFICATION_COMPLETE', 'NOM_COURS_DEAU_MINUSCULE', 'NIVEAU_BASSIN', 'ECHELLE', 'SUPERF_KM2', 'NO_SEQ_BV_PRIMAIRE', 'NOM_BV_PRIMAIRE', 'NO_REG_HYDRO', 'NOM_REG_HYDRO_ABREGE', 'Shape_Length', 'Shape_Area']) # might want shape length and share area later
        watershed_data = watershed_data[watershed_data['NOM_COURS_DEAU'].notna() & (watershed_data['NOM_COURS_DEAU'].str.strip() != "")]
        

        print(f'........ {timenow()} Reprojecting Watershed data') 
        watershed_data = repojectdata(watershed_data, 4326)
 

        print(f'.......... {timenow()} Saving Watershed Data (Parquet and GeoJson) For Later') 
        watershed_data.to_file(qc_watershed_data_path_json, driver="GeoJSON")
        watershed_data.to_parquet(qc_watershed_data_path)  
        
    else:
        print(f'...... {timenow()} The Watershed data is alredy processed, Loading in now')
        watershed_data = gpd.read_parquet(qc_watershed_data_path)

    return watershed_data









def fx_scrape_ontariogeohub(url, dataname):
    print(f'.. {timenow()} Scrapping Ontario Geohub')
    savefolder = work_dir / "data" / dataname
    data_path = savefolder / f"unprocessed_{dataname}.parquet"

    if not data_path.exists(): 
        print(f'.... {timenow()} The data does not exist, trying to download now')
        try:
            ids_response = requests.get(
                url,
                params={
                    "where": "1=1",
                    "returnIdsOnly": "true",
                    "f": "json"
                }
            )
            ids = ids_response.json()["objectIds"]
        except:
            print("Could Not acces Ontario Geohub, their API sucks :(, Unprocessed Ontario Fire Data is available on the git hub, put the .parquet file in the data/ontario_fires folder and run again))")
            sys.exit()

        
        all_feats = []
        chunk_size = 500

        for i in range(0, len(ids), chunk_size):
            batch = ids[i:i + chunk_size]
            res = requests.post(
                url,
                data={
                    "objectIds": ",".join(map(str, batch)),
                    "outFields": "*",
                    "outSR": 4326,
                    "returnGeometry": "true",
                    "f": "json"
                }
            ).json()



            features = res.get("features", [])
            for feat in features:
                geom_data = feat.get("geometry")
                props = feat.get("attributes", {})

                # Convert Esri JSON → Shapely geometry
                geom = None
                if geom_data:
                    try:
                        if "rings" in geom_data:  # Polygon
                            geom = Polygon(geom_data["rings"][0])
                        elif "paths" in geom_data:  # Polyline
                            geom = shape({"type": "LineString", "coordinates": geom_data["paths"][0]})
                        elif "x" in geom_data and "y" in geom_data:  # Point
                            geom = shape({"type": "Point", "coordinates": [geom_data["x"], geom_data["y"]]})
                    except Exception as e:
                        print("⚠️ Geometry conversion failed for one feature:", e)
                        continue

                if geom:
                    props["geometry"] = geom
                    all_feats.append(props)
        print(f'...... {timenow()} The Data is downloaded saving now for later use')

        savefolder.mkdir(parents=True, exist_ok=True)

        gdf = gpd.GeoDataFrame(all_feats, geometry="geometry", crs="EPSG:4326")

        gdf.to_parquet(data_path) 
    else:
        print(f'.... {timenow()} The Data is already downlaoded ')

    return data_path


def fx_get_on_fire_data():
    print('Getting ON Fire Data')                                               # Loads in QC fire data (beofre and after), merges the two datasets, reprojects it, then saves it as a parquet so we only have to do this once 

    ontario_fires_URL = "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/LIO_Open09/MapServer/28/query"
    data_path = fx_scrape_ontariogeohub(ontario_fires_URL, 'ontario_fires')

    on_processed_data_folder_path = work_dir / "data" / 'on_processed_data'
    on_processed_data_path = on_processed_data_folder_path / 'on_processed_fire_data.parquet'

    if not on_processed_data_path.exists():
        print(f'...... {timenow()} Pre-Processing the Data')

        on_processed_data_folder_path.mkdir(parents=True, exist_ok=True)
        data = gpd.read_parquet(data_path)
        data = data[["FIRE_YEAR", "FIRE_FINAL_SIZE", "geometry"]]
        data = data.rename(columns={"FIRE_YEAR": "fire_year"})
        data = data.rename(columns={"FIRE_FINAL_SIZE": "fire_size"})
        data["province"] = "on"
        data = repojectdata(data, 4326)
        print(f'........ {timenow()} Done Pre-Processing Saving For Later')

        data.to_parquet(on_processed_data_path) 
    else:
        print(f'...... {timenow()} The Data Is Already Pre-Processed Loading In Now')
        data = gpd.read_parquet(on_processed_data_path)
    return data















def fx_merge_provincial_fires(qcfires, onfires):
    combined_gdf = pd.concat([qcfires, onfires], ignore_index=True)

    combined_gdf = gpd.GeoDataFrame(combined_gdf, geometry='geometry', crs=qcfires.crs)
    return combined_gdf













def fx_filter_fires_data(                                                                             # This is the function that actually filters the data, it takes in fire data (and watershed but removed it cause brocken for now), as well as user inputs for filtering 
    fire_gdf,      
    watershed_data, 
    qcprovinceflag,
    onprovinceflag,                                                                                                                                                                    # Nore sure if i already mentioned this but i used AI to help apply all the filters at once / apply only the ones the user inputed
    min_year,
    max_year,
    min_size,
    max_size,
    distance_coords,
    distance_radius,
    watershed_name
    ):
    filtered_gdf = fire_gdf[fire_gdf['province'].isin([qcprovinceflag, onprovinceflag])]
    conditions = []     # This is a list of the filtering conditions so they can all be applied at once 
    
    if min_year == '' and max_year == '' and min_size == '' and max_size == '' and distance_coords == '' and distance_radius == '' and watershed_name == '':                                                                             
        min_year = 1903
        max_year = 1903
        conditions.append((filtered_gdf['fire_year'] >= min_year) & (filtered_gdf['fire_year'] <= max_year)) 
        combined_mask = np.logical_and.reduce(conditions)                                                         
        filtered_gdf = filtered_gdf[combined_mask]
        return filtered_gdf, None, None
    
    else:
        if min_year  != '' or max_year  != '':                                                                  # This IFs for all of these check if the filtering box on the site has a value inputed in it for this one and the next one we use OR becuase wse want the use to be able to input only a max or a min and not HAVE to input both 
            if min_year  != '':
                min_year = int(min_year)
            else:                                                                                               # If this field was empty (and the other was not as the IF is running) then we assing the min year to 0, if we dont do this it tryus to convert NULL to an int
                min_year = 0
            if max_year  != '':
                max_year= int(max_year)
            else:
                max_year = 100000
            conditions.append((filtered_gdf['fire_year'] >= min_year) & (filtered_gdf['fire_year'] <= max_year))      # This appends the condition to the filtering list to be applied later 

        if min_size  != '' or max_size  != '':
            if min_size  != '':
                min_size = int(min_size)
            else:
                min_size = 0
            if min_size  != '':
                max_size= int(max_size)
            else:
                min_size = 100000
            conditions.append((filtered_gdf['fire_size'] >= min_size) & (filtered_gdf['fire_size'] <= max_size))

        if distance_coords  != '' and distance_radius  != '':                                                     # The is the distance radius filtering that only selects fires within a radius of a point 
                lat, lon = map(float, distance_coords.split(','))       
                distance_radius = float(distance_radius)
                distance_radius = distance_radius*1000
                user_point = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326')                                    # This creates the point based ont he user inputed coords 
                utm_crs = user_point.estimate_utm_crs()                             
                user_point_m = user_point.to_crs(utm_crs)                                                             # This chanes the point to a projection that makes sense for its locatoin, we cannot have it in EPSG: 4326 becuase this projection cant measure distances in metres only in degrees 
                buffer_m = user_point_m.buffer(distance_radius)                                                         # This creates a buffer around the point with a radius that the user inputed 
                buffer_deg = buffer_m.to_crs('EPSG:4326')                                                             # Here we reproject the buffer back to EPSG:4326 so leaflet can display it, AI helped me construct this process but the logic behind it was mine, at first it wanted me to do a very roundabout way
                conditions.append(filtered_gdf.geometry.intersects(buffer_deg.iloc[0]))

        if watershed_name  != '':                                                                             # This shit dont work
                selected_ws = watershed_data[watershed_data['NOM_COURS_DEAU'] == watershed_name]
                if not selected_ws.empty:
                    print('Starting Watershed Filtering', timenow())
                    watershed_polygon = selected_ws.geometry.unary_union  
                    conditions.append(filtered_gdf.geometry.within(watershed_polygon))
                    print('Done Watershed Filtering', timenow())
                else:
                    print(f'No watershed found with name "{watershed_name}". Filter will be ignored.')

        if conditions:
            combined_mask = np.logical_and.reduce(conditions)                                                         # The combined filtered conditions
            filtered_gdf = filtered_gdf[combined_mask]                                                                # Filtering the dataset and returning with the right fitlers 

        results = {
                "filtered_gdf": filtered_gdf,
                "user_point": None,
                "buffer_geom": None,
                "watershed_polygon": None
            }

        # Fill in whichever geometry applies
        if distance_coords != '' and distance_radius != '':
            results["user_point"] = user_point
            results["buffer_geom"] = buffer_deg

        if watershed_name != '' and watershed_polygon is not None:
            results["watershed_polygon"] = watershed_polygon

        return results




def fx_createexploremap(data, map_name):
    m = data.explore()
    m.save(f'static/{map_name}.html')



 


def fx_download_json(filtered_data):    
                                                                            # This function is to dowload the filtered data as a geojson, AI showed me how to do this as it is not as simple as just regularly saving the file as it must go through flask 
        geojson_data = json.loads(filtered_data.to_json())                                                            # converst the filtered data to geojson
        geojson_string = json.dumps(geojson_data) 
        geojson_buffer = io.BytesIO(geojson_string.encode('utf-8'))   
        geojson_buffer.seek(0)
        
        return send_file(                                                                                       # Send the file back to the browser as an attachment

            geojson_buffer,
            
            mimetype='application/json',                   
            as_attachment=True,
            download_name='firecan_filtered_data.geojson'                   

        )


def fx_download_csv(filtered_data):     # Exact same thing as the last function but downloads as csv        

    csv_buffer = io.BytesIO()
    filtered_data.drop(columns=['geometry'], errors='ignore').to_csv(csv_buffer, index=False, encoding='utf-8')         # Drops geom column here too 

    csv_buffer.seek(0)
    
    return send_file(                                                   

        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='firecan_filtered_data.csv'
    ) 


def fx_download_gpkg(filtered_data):
    gpkg_buffer = io.BytesIO()  

    filtered_data.to_file(gpkg_buffer, driver="GPKG")

    gpkg_buffer.seek(0) 

    return send_file(
        gpkg_buffer,
        mimetype='application/geopackage+sqlite3',
        as_attachment=True,
        download_name='firecan_filtered_data.gpkg'
    )

