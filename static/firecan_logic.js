
var fireLayer;

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


// The main function to fetch and display the filtered data
function loadFilteredData() {
    // 1. Remove the old layer if it exists
    if (fireLayer) {
        map.removeLayer(fireLayer);
    }

    // 2. Get filter values from input fields. The || '/' provides a default value for the Flask script.
    const minYear = document.getElementById('minYear').value;
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;

    // 3. Construct the URL with query parameters
    const url = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}`;


    
    // 4. Fetch data from the Flask API
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
                console.log("Data successfully received and processed:");
            return response.json();
        })
        .then(data => {
            // 5. Add the new GeoJSON layer to the map
            fireLayer = L.geoJSON(data, {

                style: function(feature) {
                    return {
                        color: "#FF0000",
                        weight: 4,
                        opacity: 1,
                        fillColor: "#FF0000",
                        fillOpacity: 0.5
                    };
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
                },

            }).addTo(map);
            
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert("An error occurred while fetching the data. Please check your inputs.");
        });
}


// Function 2 (NEW): Triggers the data download (requests a file)
function downloadFilteredData() {
    // 1. Get all filter values (same as loadFilteredData)
    const minYear = document.getElementById('minYear').value;
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;
    const jsondownload = document.getElementById('jsondownload').checked;


    // 2. Construct the URL (INCLUDING the &download=1 flag)
    const downloadURL = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&jsondownload=${jsondownload}&download=1`;
    
    // 3. Trigger the file download using a temporary <a> tag
    const a = document.createElement('a');
    a.href = downloadURL;
    a.download = 'firecan_filtered_data.csv'; // Suggests a file name
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
