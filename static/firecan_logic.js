
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

    const loadingEl = document.getElementById('loadingMessage');
    loadingEl.innerHTML = 'Loading data<br>This may take several minutes';
    loadingEl.style.display = 'block';






    if (fireLayer) {
        map.removeLayer(fireLayer);
    }

    const minYear = document.getElementById('minYear').value;
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;
    const url = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
                console.log("Data successfully received and processed:");
            return response.json();
        })
        .then(data => {

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
            
            
            const fireCount = data.features ? data.features.length : 0;
            loadingEl.textContent = `${fireCount} fires matched your criteria.`;
            setTimeout(() => {
                loadingEl.style.display = 'none';
            }, 5000);


        })

        .catch(error => {
            console.error('Error fetching data:', error);
            alert("An error occurred while fetching the data. Please check your inputs.");
        })
}



function downloadFilteredData() {

    const downloadingEl = document.getElementById('downloadingMessage');
    downloadingEl.innerHTML = 'Downloading the data now<br>This may take several minutes';
    downloadingEl.style.display = 'block';

    const minYear = document.getElementById('minYear').value;
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;
    const jsondownload = document.getElementById('jsondownload').checked;



    const downloadURL = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&jsondownload=${jsondownload}&download=1`;
    

    const a = document.createElement('a');
    a.href = downloadURL;
    a.download = 'firecan_filtered_data.csv'; 
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);


    downloadingEl.textContent = `File has been dowloaded`;
    setTimeout(() => {
        downloadingEl.style.display = 'none';
    }, 5000);

}
