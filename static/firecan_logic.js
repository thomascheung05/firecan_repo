// This is my first time working in Java so its a big learning experinece for me. I'm having a hard time wrapping my head around Java as i feel the code executes differently from python but i still have a relativley good unserstanding of what each line is doing 



// Create base layers
var Esrimap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  { maxZoom: 18, attribution: 'Tiles © Esri' }
); // Esri imagery [web:50]

var OpenStreetMap_Mapnik = L.tileLayer(
  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 

var OpenCycleMap = L.tileLayer(
  'https://tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 

var Transport = L.tileLayer(
  'https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var Landscape = L.tileLayer(
  'https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var Outdoors = L.tileLayer(
  'https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var SpinalMap = L.tileLayer(
  'https://tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var TransportDark = L.tileLayer(
  'https://tile.thunderforest.com/transport-dark/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var Pioneer = L.tileLayer(
  'https://tile.thunderforest.com/pioneer/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var MobileAtlas = L.tileLayer(
  'https://tile.thunderforest.com/mobile-atlas/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var Neighbourhood = L.tileLayer(
  'https://tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 


var Atlas = L.tileLayer(
  'hhttps://tile.thunderforest.com/atlas/{z}/{x}/{y}.png?apikey=17dc0c0df61f47d4b13d3520ec5b1557',
  { maxZoom: 19, attribution: '© OpenStreetMap contributors' }
); 



// Initialize map with default base
var map = L.map('map', {
  center: [52.520878, -69.855725],
  zoom: 5,
  layers: [Transport]
}); 

// Register basemaps in the control
var baseLayers = {
  'OpenStreetMap': OpenStreetMap_Mapnik,
  'Esrimap': Esrimap,
  'OpenCycleMap': OpenCycleMap,
  'Transport': Transport,
  'Landscape': Landscape,
  'Outdoors': Outdoors,
  'SpinalMap': SpinalMap,
  'TransportDark': TransportDark,
  'Pioneer': Pioneer,
  'MobileAtlas': MobileAtlas,
  'Neighbourhood': Neighbourhood,
  'Atlas': Atlas
};

// Add the control at top-right
L.control.layers(baseLayers, null, { position: 'topright' }).addTo(map); 




var fireLayer;
var userPointLayer;
var userBufferLayer;
function loadFilteredData() {                                                                                          // This is the fuction that sends python the filtering conditions, and receives a filtered dataset that it then displays on the map, ai helped a lot with this and the function below this  

    const loadingEl = document.getElementById('loadingMessage');                                                       // This is for the message that says the data is downlaoding, AI helped me with this
    loadingEl.style.display = "block";                                                                               // This lines displays the message, as by deafult it is hidden 
                   
    if (fireLayer) { map.removeLayer(fireLayer); fireLayer = null; }   // remove old fires [web:3]
    if (userPointLayer) { map.removeLayer(userPointLayer); userPointLayer = null; } // remove old point [web:4]
    if (userBufferLayer) { map.removeLayer(userBufferLayer); userBufferLayer = null; } // remove old buffer [web:4]


    const minYear = document.getElementById('minYear').value;                                                          // This takes the inputs form the HTML and assings it to varibles in java 
    const maxYear = document.getElementById('maxYear').value;
    const minSize = document.getElementById('minSize').value;
    const maxSize = document.getElementById('maxSize').value;
    const distanceCoords = document.getElementById('distanceCoords').value;
    const distanceRadius = document.getElementById('distanceRadius').value;
    const watershedName = document.getElementById('watershedName').value;
    const qcprovinceflag = document.getElementById('quebeccheckbox').value;
    const onprovinceflag = document.getElementById('ontariocheckbox').value;    
    const url = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&qcprovinceflag=${qcprovinceflag}&onprovinceflag=${onprovinceflag}`;
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
            // Display user point
            if (data.user_point) {
                userPointLayer = L.geoJSON(data.user_point, {
                    pointToLayer: (feature, latlng) => {
                        const starIcon = L.divIcon({
                            html: "★",
                            className: "star-marker",
                            iconSize: [60, 60],
                            iconAnchor: [10, 10]
                        });
                        return L.marker(latlng, { icon: starIcon });
                    }
                }).addTo(map);
            }
            // Display buffer
            if (data.user_buffer) {
                userBufferLayer = L.geoJSON(data.user_buffer, {
                    style: { color: 'black', weight: 3, fillOpacity: 0.1 }
                }).addTo(map);
            }   

            fireLayer = L.geoJSON(data.fires, {
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
                            Year: ${feature.properties.fire_year}<br>
                            Size: ${feature.properties.fire_size} ha
                        `;
                        layer.bindPopup(popupContent);
                    }
                },
            }).addTo(map);                                                                                            // This part actually adds everything above to map 
            
    

            const fireCount = data.fires.features ? data.fires.features.length : 0;
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
    const downloadFormat = document.getElementById('downloadFormat').value;
                                                                                                                      // THis code largely does the same thing as the function above but instead of displaying the data I uses my python dowloand data functions to downalod the filtered data 


    const downloadURL = `/fx_main?min_year=${minYear}&max_year=${maxYear}&min_size=${minSize}&max_size=${maxSize}&distance_coords=${distanceCoords}&distance_radius=${distanceRadius}&watershed_name=${watershedName}&downloadFormat=${downloadFormat}&download=1`;
    
    const a = document.createElement('a');                                                                            // This code here is what actually downlaods the data, I understand what it does but not really how it works, reddit has been telling me this a good way to downlaod data through a web app 
    a.href = downloadURL;
    a.download = 'firecan_filtered_data.csv'; 
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    downloadingEl.textContent = `File has been dowloaded`;                                                           // Same message code as in the function above 
    setTimeout(() => {
        downloadingEl.style.display = 'none';
    }, 10000);

}


