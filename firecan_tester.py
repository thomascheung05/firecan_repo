import geopandas as gpd
from firecan_fx import fx_get_can_fire_data,fx_merge_provincial_fires,fx_get_can_fire_data,fx_scrape_cwfis, fx_createexploremap,fx_get_qc_fire_data,fx_get_on_fire_data, fx_scrape_ontariogeohub,fx_get_qc_fire_data,fx_filter_fires_data,fx_download_json,fx_download_csv,timenow, fx_download_gpkg, fx_get_qc_watershed_data


gdf_qc_fires = fx_get_qc_fire_data()
gdf_qc_watershed_data = fx_get_qc_watershed_data()

gdf_can_fires = fx_get_can_fire_data()


gdf_fires = fx_merge_provincial_fires(gdf_qc_fires, gdf_can_fires)