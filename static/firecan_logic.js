
var fireLayer;
var fullfiredata = null;

var map = L.map('map').setView([52.520878, -69.855725], 4.5);
var Esrimap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,
    attribution: 'Tiles © Esri',
});
var OpenStreetMap_Mapnik = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
// Esrimap.addTo(map);
OpenStreetMap_Mapnik.addTo(map);   


fetch('/fx_main')
    .then(res => res.json())
    .then(data => {
        fullfiredata = data;
        console.log("Fire Data Loaded into Java")
    })







const minyear = document.getElementById('minYear').value;
const maxyear = document.getElementById('maxYear').value;
const minsize = document.getElementById('minSize').value;
const maxsize = document.getElementById('maxSize').value;
const distancecoords = document.getElementById('distanceCoords').value;
const distanceradius = document.getElementById('distanceRadius').value;
const watershedname = document.getElementById('watershedName').value;



function haversineDistance(lat1, lon1, lat2, lon2) { // Fuction for computing distances 
    const R = 6371000; // Earth radius in meters
    const toRad = angle => angle * Math.PI / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat/2)**2 +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
              Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // distance in meters
}


function filterfires(data, minyear, maxyear, minsize, maxsize, distancecoords, distanceradius, watershedname){
    minyear = minyear ? parseInt(minyear) : -Infinity;
    maxyear = maxyear ? parseInt(maxyear) : Infinity;
    minsize = minsize ? parseFloat(minsize) : 0;
    maxsize = maxsize ? parseFloat(maxsize) : Infinity;
    distanceradius = distanceradius ? parseFloat(distanceradius) : null;

    let userlat = null, userlon = null
    if (distancecoords){
        [userlat, userlon] = distancecoords.split(", ").map(Number);
    } 


    let filtered = data.features.filter(f => {
        const props = f.properties;
        const coords = f.geometry.coordinates;
        
        // Year filter
        if (props.an_origine < minyear || props.an_origine > maxyear) return false;

        // Size filter
        if (props.superficie < minsize || props.superficie > maxsize) return false;

        // Distance filter
        if (distanceradius && userlat != null && userlon != null) {
            const dist = haversineDistance(userlat, userlon, coords[1], coords[0]);
            if (dist > distanceradius) return false;
        }

        // Watershed filter (optional, needs GeoJSON of watersheds)
        if (watershedname) {
            // Implement later once you have watershed polygons loaded as GeoJSON
            // Use turf.js: turf.booleanPointInPolygon([lon, lat], polygon)
        }

        return true; // keep this feature
    });

    return { type: "FeatureCollection", features: filtered };

}



document.getElementById('filterButton')


function loadFilteredData(){
    if (fireLayer) map.removeLayer(fireLayer)

    const filteredfiredata = {
        type: "FeatureCollection",
        features: filterfires(fullfiredata)
    }

    fireLayer = L.geoJSON(filteredfiredata, {
        style: {
            color: "#FF0000",
            weight: 4,
            opacity: 1,
            fillColor: "#FF0000",
            fillOpacity: 0.5
        },
        onEachFeature: function(feature, layer) {
            if (feature.properties) {
                let popupContent = `
                    <b>Fire Details</b><br>
                    Year: ${feature.properties.an_origine}<br>
                    Size: ${feature.properties.superficie} ha
                `;
                layer.bindPopup(popupContent);
            }
        }
    }).addTo(map);
}












// // The main function to fetch and display the filtered data
// function loadFilteredData() {
//     // 1. Remove the old layer if it exists
//     if (fireLayer) {
//         map.removeLayer(fireLayer);
//     }

//     // 2. Get filter values from input fields. The || '/' provides a default value for the Flask script.
//     const minYear = document.getElementById('minYear').value;
//     const maxYear = document.getElementById('maxYear').value;
//     const minSize = document.getElementById('minSize').value;
//     const maxSize = document.getElementById('maxSize').value;
//     const distanceCoords = document.getElementById('distanceCoords').value;
//     const distanceRadius = document.getElementById('distanceRadius').value;
//     const watershedName = document.getElementById('watershedName').value;

//     // 3. Construct the URL with query parameters
//     const url = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}`;


    
//     // 4. Fetch data from the Flask API
//     fetch(url)
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//                 console.log("Data successfully received and processed:");
//             return response.json();
//         })
//         .then(data => {
//             // 5. Add the new GeoJSON layer to the map
//             fireLayer = L.geoJSON(data, {

//                 style: function(feature) {
//                     return {
//                         color: "#FF0000",
//                         weight: 4,
//                         opacity: 1,
//                         fillColor: "#FF0000",
//                         fillOpacity: 0.5
//                     };
//                 },

//                 onEachFeature: function(feature, layer) {
//                     if (feature.properties) {
//                         let popupContent = `
//                             <b>Fire Details</b><br>
//                             Year: ${feature.properties.an_origine}<br>
//                             Size: ${feature.properties.superficie} ha
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 },

//             }).addTo(map);
            
//         })
//         .catch(error => {
//             console.error('Error fetching data:', error);
//             alert("An error occurred while fetching the data. Please check your inputs.");
//         });
// }


// function downloadFilteredData() {
//     const minYear = document.getElementById('minYear').value;
//     const maxYear = document.getElementById('maxYear').value;
//     const minSize = document.getElementById('minSize').value;
//     const maxSize = document.getElementById('maxSize').value;
//     const distanceCoords = document.getElementById('distanceCoords').value;
//     const distanceRadius = document.getElementById('distanceRadius').value;
//     const watershedName = document.getElementById('watershedName').value;
//     const jsondownload = document.getElementById('jsondownload').checked;


//     const downloadURL = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&jsondownload=${jsondownload}&download=1`;
    
//     const a = document.createElement('a');
//     a.href = downloadURL;
//     a.download = 'firecan_filtered_data.csv'; 
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
// }
