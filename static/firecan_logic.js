// This is my first time working in Java so its a big learning experinece for me. I'm having a hard time wrapping my head around Java as i feel the code executes differently from python but i still have a relativley good unserstanding of what each line is doing 



var fireLayer;

var map = L.map('map').setView([52.520878, -69.855725], 4.5);                                                          // Sets initial view for the amp 
var Esrimap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {    // ESRI sattelite image base map 
    maxZoom: 18,
    attribution: 'Tiles © Esri',
});
var OpenStreetMap_Mapnik = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {                             // Whack open street view map 
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
OpenStreetMap_Mapnik.addTo(map);   

function loadFilteredData() {                                                                                          // This is the fuction that sends python the filtering conditions, and receives a filtered dataset that it then displays on the map, ai helped a lot with this and the function below this  

    const loadingEl = document.getElementById('loadingMessage');                                                       // This is for the message that says the data is downlaoding, AI helped me with this
    loadingEl.innerHTML = 'Loading data<br>This may take several minutes';
    loadingEl.style.display = 'block';                                                                                 // This lines displays the message, as by deafult it is hidden 
                   
    if (fireLayer) {                                                                                                   // If there is arlready a layer of polygons remove it 
        map.removeLayer(fireLayer);
    }

    const minYear = document.getElementById('minYear').value;                                                          // This takes the inputs form the HTML and assings it to varibles in java 
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;
    const url = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}`;
                                                                                                                        // The line above takes the varibles above it and uses them to constract a URL that will be sent to my python and tells it what the filtering conditions are 
    fetch(url)                                                                                                          // This is the part that sends the URL to python, python then filters the data and sends back a filtered dataset
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
                console.log("Data successfully received and processed:");
            return response.json();
        })
        .then(data => {                                                                                                 // Using the data we just go we dispaly it on the leaflet map 

            fireLayer = L.geoJSON(data, {

                style: function(feature) {                                                                               // THis styles the polygons that are displayed on the map 
                    return {
                        color: "#FF0000",
                        weight: 4,                                                                                       // Big weight to make the polygons visible from zoomed out 
                        opacity: 1,
                        fillColor: "#FF0000",
                        fillOpacity: 0.5                                                                                 // Lower opacity looks better, and helps distinguish from polygon fill and border on map (useful when many polygons are next to each other)
                    };
                },

                onEachFeature: function(feature, layer) {                                                               // This creates a pop up when clicking on polygons that say the year and its size, this was half taken from Ottowa demo and half AI.
                    if (feature.properties) {                   
                        let popupContent = `
                            <b>Fire Details</b><br>
                            Year: ${feature.properties.an_origine}<br>
                            Size: ${feature.properties.superficie} ha
                        `;
                        layer.bindPopup(popupContent);
                    }
                },

            }).addTo(map);                                                                                            // This part actually adds everything above to map 
            
            
            const fireCount = data.features ? data.features.length : 0;
            loadingEl.textContent = `${fireCount} fires matched your criteria.`;                                       // This displays a message after the data has been loaded in it tell the user how many fires matched their criteria. THis is useful as it signals when data is loading / done loading (good for big datasets) and also tells the user if there were no fires that matches their criterai (so they are not confused by empty map)
            setTimeout(() => {                                                                                         // THis removes the message after 5 seconds 
                loadingEl.style.display = 'none';
            }, 5000);


        })

        .catch(error => {                                                                                              // Displays message if there is an error getting the data 
            console.error('Error fetching data:', error);
            alert("An error occurred while fetching the data. Please check your inputs.");
        })
}



function downloadFilteredData() {                                                                                       

    const downloadingEl = document.getElementById('downloadingMessage');                                               // Same message code as in the function above 
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
                                                                                                                      // THis code largely does the same thing as the function above but instead of displaying the data I uses my python dowloand data functions to downalod the filtered data 


    const downloadURL = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&jsondownload=${jsondownload}&download=1`;
    
    const a = document.createElement('a');                                                                            // This code here is what actually downlaods the data, I understand what it does but not really how it works, reddit has been telling me this a good way to downlaod data through a web app 
    a.href = downloadURL;
    a.download = 'firecan_filtered_data.csv'; 
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    downloadingEl.textContent = `File has been dowloaded`;                                                           // Same message code as in the function above 
    setTimeout(() => {
        downloadingEl.style.display = 'none';
    }, 5000);

}
