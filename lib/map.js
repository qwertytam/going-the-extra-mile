// Delay time in milliseconds
var delay = 100;
var subset = 0;
var routes_list = []

function initMap() {

    const dirService = new google.maps.DirectionsService();
    const dirDisplay = new google.maps.DirectionsRenderer();

    const centerLatLng = { lat: 41.85, lng: -87.65 };
    const mapOptions = {
        zoom: 8,
        center: centerLatLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    const map = new google.maps.Map(document.getElementById('map'), mapOptions);

    directionsRenderer.setMap(map);
    dirService.route({
        origin: new google.maps.LatLng(40.650100, -83.949580),
        destination: new google.maps.LatLng(41.700370, -83.920970),
        waypoints: [
            {location: new google.maps.LatLng(41.147600, -83.989310), stopover: false},
            {location: new google.maps.LatLng(40.783430, -83.966250), stopover: false},
            {location: new google.maps.LatLng(40.796770, -84.481540), stopover: false},
            {location: new google.maps.LatLng(40.829820, -85.077670), stopover: false},
            {location: new google.maps.LatLng(41.322320, -84.802390), stopover: false},
            {location: new google.maps.LatLng(41.576760, -85.258790), stopover: false},
            {location: new google.maps.LatLng(41.655650, -84.689330), stopover: false},
            {location: new google.maps.LatLng(42.278140, -84.915990), stopover: false},
            {location: new google.maps.LatLng(42.531180, -85.523510), stopover: false},
            {location: new google.maps.LatLng(42.601180, -86.180480), stopover: false},
            {location: new google.maps.LatLng(43.048120, -86.147420), stopover: false},
            {location: new google.maps.LatLng(43.075350, -85.706850), stopover: false},
            {location: new google.maps.LatLng(43.025630, -84.985990), stopover: false},
            {location: new google.maps.LatLng(42.700480, -84.924260), stopover: false},
        ],
        optimizeWaypoints: false,
        travelMode: google.maps.TravelMode.DRIVING,
        },
        (response, status) => {
            if (status === 'OK') {
                directionsRenderer.setDirections(response);
            }
        }
    );
}

function calcRoute() {

}

function createRoutes() {

}
