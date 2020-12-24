var delay = 100;  // Delay time in milliseconds
var subset = 0;  // Track which subset we are up to
var subsetInc = 10  // Subset increment
var routes_list = []  // Store routes to be displayed


function initMap() {
    if ('google' in window && typeof google === 'object' && typeof google.maps === 'object') {
        console.log('Google Maps API loaded successfully');
    } else {
        console.log('Google Maps API NOT loaded')
    }

    const centerLatLng = { lat: 41.85, lng: -87.65 };
    const mapOptions = {
        zoom: 8,
        center: centerLatLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    const map = new google.maps.Map(document.getElementById('map'), mapOptions);
    const dirService = new google.maps.DirectionsService();

    getRoute(map, dirService);
}

function getRoute(map, dirService) {
    const dirDisplay = new google.maps.DirectionsRenderer();

    dirDisplay.setMap(map);
    dirService.route(
        {
            origin: new google.maps.LatLng(40.650100, -83.949580),
            destination: new google.maps.LatLng(41.700370, -83.920970),
            waypoints: optRoute,
            optimizeWaypoints: false,
            travelMode: google.maps.TravelMode.DRIVING,
        },
        (response, status) => {
            if (status === 'OK') {
                console.log('GMap status:: ' + status);
                dirDisplay.setDirections(response);
            } else if (status === 'OVER_QUERY_LIMIT') {
                console.log('GMap status:: ' + status);
            } else {
                console.log('GMap status:: ' + status);
            }
        }
    );
}

function createRoutes(startPt, endPt, midPts) {

}

function nextSubset() {
    if (subset < optRoute.length) {
        setTimeout('createRoutes("'+addresses[nextAddress]+'",theNext)', delay);
        subset = subset + subsetInc - 1;
    } else {
        // We're done. Show map bounds
        map.fitBounds(bounds);
    }
}
