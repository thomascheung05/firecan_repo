import zipfile
import json
import requests
import geopandas as gpd
from datetime import datetime
from flask import request, send_file  
import io
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import fiona 
import numpy as np
work_dir  = Path.cwd()

                                                                                        # A lot of the code here is pretty simple data manipulaiton mostly filtering
                                                                                        # AI was used for the general 'how do i do this' stuff but the code has been changed so much not a lot of still left over form the AI with the eception of the downloading functions, which are mostly AI as they are pretty straightforward and there wasnt much to change
                                                                                        # Almost all of the structure of this code is mine, like the download only if it doesnt exist and the process if it the processesed data doenst already exist
                                                                                        # AI showed me how to apply multiple filters at once which is a pretty integral part of the script







def fx_scrape_donneqc(dataname, url, zipname, gpkgname):                                           # Scraps donne quebec to get quebef fire data, outputs the path to the data file
    savefolder = work_dir / dataname
    zip_path = savefolder / zipname                                                                # Name of zip file depends on the data being dowloaded, for fire data its the same but not for watershed data
    unzipped_file_path = savefolder / gpkgname                                                     # This differs between quebec fire data, and also watershed data set

    if not unzipped_file_path.exists():                                                            # Checks if the GPKG file exists, if not it will create a folder and downlaod it 
        print('Data does not exist, Downloading now, this may take several minutes ...')
        savefolder.mkdir(parents=True, exist_ok=True)
        print('Created folder:', savefolder)
        response = requests.get(url)                                                                # AI showed me how to do this
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print('DONE Downloading the Data for', dataname) 
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:                                            # The data come in a zipfile so must unzip it
            zip_ref.extractall(savefolder)
        print('DONE! unzipping the data, data is located in', zip_path)
    else:                                                                                          # If it already exists we do nothing as we already created the path that needs to be returned outside of the IF 
        print('....................This Dataset is already Downloaded', dataname)                

    return unzipped_file_path


def fx_get_qc_watershed_data():                                                                                        # This function gets the watershed data by using the scrap donne quebec function, it then reads it in, drops some columns, and reprojects it
    print('Getting Watershed Data')
    url_watersheddata = 'https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/Bassins_hydrographiques_multi_echelles/CE_bassin_multi.gdb.zip'
    watersheddata_zipname = 'CE_bassin_multi.gdb.zip'
    watersheddata_fgdbname = 'CE_bassin_multi.gdb'

    qcwatershed_unzipped_file_path = fx_scrape_donneqc('qcwatershed_data', url_watersheddata, watersheddata_zipname, watersheddata_fgdbname)                   
        
    qc_processed_data_folder_path = work_dir / 'qc_processed_data'
    qc_watershed_data_path = qc_processed_data_folder_path / 'qc_watershed_data.parquet'

    if not qc_watershed_data_path.exists():
        layers = fiona.listlayers(qcwatershed_unzipped_file_path)
        watershed_data = gpd.read_file(qcwatershed_unzipped_file_path, layer=layers[1])
        watershed_data = watershed_data.drop(columns=['NO_COURS_DEAU', 'NOM_COURS_DEAU_MINUSCULE', 'NIVEAU_BASSIN', 'ECHELLE', 'SUPERF_KM2', 'NO_SEQ_BV_PRIMAIRE', 'NOM_BV_PRIMAIRE', 'NO_REG_HYDRO', 'NOM_REG_HYDRO_ABREGE', 'Shape_Length', 'Shape_Area']) # might want shape length and share area later
        
        now = datetime.now().strftime('%H:%M:%S')
        print('Reprojecting Watershed data Time:', now)
        is_wgs84 = watershed_data.crs.to_epsg() == 4326
        if is_wgs84:
            print('The data is already in EPSG:4326 (WGS 84).')
        else:
            watershed_data = watershed_data.to_crs(epsg=4326)  

        now = datetime.now().strftime('%H:%M:%S')
        print('Saving Watershed Data for Later Time:',now)
        watershed_data.to_parquet(qc_watershed_data_path)  
        
    else:
        print('...............The Watershed data is already processed, loading in now ...')
        watershed_data = gpd.read_parquet(qc_watershed_data_path)

    return watershed_data

        


def fx_qc_processfiredata(beforepath, afterpath):                                                  # Loads in QC fire data (beofre and after), merges the two datasets, reprojects it, then saves it as a parquet so we only have to do this once 

    qc_processed_data_folder_path = work_dir / 'qc_processed_data'
    qc_processed_data_path = qc_processed_data_folder_path / 'qc_processed_data.parquet'

    if not qc_processed_data_path.exists():

        qc_processed_data_folder_path.mkdir(parents=True, exist_ok=True)
        print('Loading in unprocessed fire data ... This may take a few minutes ...')
        before_data = gpd.read_file(beforepath, layer= 'feux_anciens_prov')
        after_data = gpd.read_file(afterpath, layer= 'feux_prov')

        after_data = after_data.drop(columns=['exercice', 'origine', 'met_at_str', 'shape_length', 'shape_area'])        # might want shape length and share area later
        before_data = before_data.drop(columns=['exercice', 'origine', 'met_at_str', 'shape_length', 'shape_area'])        # might want shape length and share area later

        print('Merging the data')
        before_data = before_data.rename(columns={'geoc_fan': 'geoc'})
        after_data = after_data.rename(columns={'geoc_fmj': 'geoc'})
        after_data = after_data.drop(columns=['perturb', 'an_perturb', 'part_str'])
        merged_data = gpd.GeoDataFrame(
            pd.concat([before_data, after_data], ignore_index=True),
            geometry='geometry'  
        )
        merged_data['an_origine'] = pd.to_numeric(merged_data['an_origine'], errors='coerce')
        merged_data['superficie'] = pd.to_numeric(merged_data['superficie'], errors='coerce')




        now = datetime.now().strftime('%H:%M:%S')
        print('Reprojecting Fire data (',now,')')
        is_wgs84 = merged_data.crs.to_epsg() == 4326
        if is_wgs84:
            print('The data is already in EPSG:4326 (WGS 84).')
        else:
            merged_data = merged_data.to_crs(epsg=4326)    
            now = datetime.now().strftime('%H:%M:%S')
            print('The data has been reprojectd (',now,')')



    



        print('Saving processed QC data to load in later')
        merged_data.to_parquet(qc_processed_data_path)

    else:                                                                                                               # If there fire data is already processed we just load it in here
        print('...............The QC data is already processed, loading in now ...')
        merged_data = gpd.read_parquet(qc_processed_data_path)
    
    watershed_data = fx_get_qc_watershed_data()

    return merged_data, watershed_data







def fx_filter_fires_data(                                                                             # This is the function that actually filters the data, it takes in fire data (and watershed but removed it cause brocken for now), as well as user inputs for filtering 
    fire_gdf,      
    watershed_data,                                                                                   # Nore sure if i already mentioned this but i used AI to help apply all the filters at once / apply only the ones the user inputed
    min_year,
    max_year,
    min_size,
    max_size,
    distance_coords,
    distance_radius,
    watershed_name
):

    filtered_gdf = fire_gdf.copy()
    conditions = []                                                                                     # This is a list of the filtering conditions so they can all be applied at once 

    if min_year  != '' or max_year  != '':                                                                  # This IFs for all of these check if the filtering box on the site has a value inputed in it for this one and the next one we use OR becuase wse want the use to be able to input only a max or a min and not HAVE to input both 
        if min_year  != '':
            min_year = int(min_year)
        else:                                                                                               # If this field was empty (and the other was not as the IF is running) then we assing the min year to 0, if we dont do this it tryus to convert NULL to an int
             min_year = 0
        if max_year  != '':
            max_year= int(max_year)
        else:
             max_year = 100000
        conditions.append((filtered_gdf['an_origine'] >= min_year) & (filtered_gdf['an_origine'] <= max_year))      # This appends the condition to the filtering list to be applied later 

    if min_size  != '' or max_size  != '':
        if min_size  != '':
            min_size = int(min_size)
        else:
             min_size = 0
        if min_size  != '':
            max_size= int(max_size)
        else:
             min_size = 100000
        conditions.append((filtered_gdf['superficie'] >= min_size) & (filtered_gdf['superficie'] <= max_size))

    if distance_coords  != '' and distance_radius  != '':                                                     # The is the distance radius filtering that only selects fires within a radius of a point 
            lat, lon = map(float, distance_coords.split(','))       
            distance_radius = float(distance_radius)
            user_point = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326')                                    # This creates the point based ont he user inputed coords 
            utm_crs = user_point.estimate_utm_crs()                             
            user_point_m = user_point.to_crs(utm_crs)                                                             # This chanes the point to a projection that makes sense for its locatoin, we cannot have it in EPSG: 4326 becuase this projection cant measure distances in metres only in degrees 
            buffer_m = user_point_m.buffer(distance_radius)                                                         # This creates a buffer around the point with a radius that the user inputed 
            buffer_deg = buffer_m.to_crs('EPSG:4326')                                                             # Here we reproject the buffer back to EPSG:4326 so leaflet can display it, AI helped me construct this process but the logic behind it was mine, at first it wanted me to do a very roundabout way
            conditions.append(filtered_gdf.geometry.intersects(buffer_deg.iloc[0]))

    if watershed_name  != '':                                                                             # This shit dont work
            selected_ws = watershed_data[watershed_data['NOM_COURS_DEAU'] == watershed_name]
            if not selected_ws.empty:
                ws_geom = selected_ws.geometry.unary_union                                                  # This from AI 
                conditions.append(filtered_gdf.geometry.within(ws_geom))
            else:
                print(f'No watershed found with name "{watershed_name}". Filter will be ignored.')

    if conditions:
        combined_mask = np.logical_and.reduce(conditions)                                                         # The combined filtered conditions
        filtered_gdf = filtered_gdf[combined_mask]                                                                # Filtering the dataset and returning with the right fitlers 
        
    return filtered_gdf

 


def fx_download_json(filtered_data):                                                                        # This function is to dowload the filtered data as a geojson, AI showed me how to do this as it is not as simple as just regularly saving the file as it must go through flask 
        geojson_data = json.loads(filtered_data.to_json())                                                            # converst the filtered data to geojson
        geojson_string = json.dumps(geojson_data) 
    
        geojson_buffer = io.BytesIO(geojson_string.encode('utf-8'))                                             # Create an in-memory buffer to hold the file content
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



