var delay = 100;  // Delay time in milliseconds
var subsetIdx = 0;  // Track which subset we are up to
var subsetIdxInc = 10;  // Subset increment
var routeDispList = [];  // Store routes to be displayed

var map = {};
var dirService = {};

var dirDisplayOptions = {
    preserveViewport: true
};

var totalDist = 0;
var totalDur = 0;

function initMap() {
    if ('google' in window && typeof google === 'object' && typeof google.maps === 'object') {
        console.log('Google Maps API loaded successfully');
    } else {
        console.log('Google Maps API NOT loaded')
    }

    const centerLatLng = { lat: 41.85, lng: -87.65 };
    const mapOptions = {
        zoom: 4,
        center: centerLatLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }

    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    dirService = new google.maps.DirectionsService();

    // getRouteTest();
    nextSubset();
}

// function getRouteTest() {
//     const dirDisplay = new google.maps.DirectionsRenderer();
//
//     dirDisplay.setMap(map);
//     dirService.route(
//         {
//             origin: new google.maps.LatLng(40.650100, -83.949580),
//             destination: new google.maps.LatLng(41.700370, -83.920970),
//             waypoints: optRoute,
//             optimizeWaypoints: false,
//             travelMode: google.maps.TravelMode.DRIVING,
//         },
//         (response, status) => {
//             if (status === 'OK') {
//                 console.log('GMap status:: ' + status);
//                 dirDisplay.setDirections(response);
//             } else if (status === 'OVER_QUERY_LIMIT') {
//                 console.log('GMap status:: ' + status);
//             } else {
//                 console.log('GMap status:: ' + status);
//             }
//         }
//     );
// }

function getRoutes(start, end, points, next) {
    // // Diagnostic print outs
    // console.log('*****___ Next Route ___*****')
    // console.log('start: ' + start.location.lat + ' lng: ' + start.location.lng);
    // console.log('points length is ' + points.length);
    // Object.entries(points).forEach(([key, value]) => {
    //     console.log(value.location);
    // });
    // console.log('end lat: ' + end.location.lat + ' lng: ' + end.location.lng);

    // Get the route from Google Maps API
    var dirDisplay = new google.maps.DirectionsRenderer(dirDisplayOptions);

    var wypts = [];
    for (var i = 0; i < points.length; i++) {
        wypts.push({
            location:points[i],
            stopover:false}
        );
    }

    var request = {
        origin: start,
        destination: end,
        waypoints: wypts,
        optimizeWaypoints: false,
        travelMode: google.maps.TravelMode.DRIVING
    };

    dirService.route(request, function(response, status) {
        console.log('API status response: ' + status + ' for start: ' + start.location.lat + ' end: ' + end.location.lat);
        if (status == google.maps.DirectionsStatus.OK) {
            // dirDisplay.setMap(map);
            dirDisplay.setDirections(response);
            var subsetRoute = response.routes[0];  // Should only be 1 route

            for (let i = 0; i < subsetRoute.legs.length; i++){
                totalDist += subsetRoute.legs[i].distance.value;
                totalDur += subsetRoute.legs[i].duration.value;
            }
            console.log('Total distance: ' + totalDist + ' m');

        }
    });
    routeDispList.push(dirDisplay);

    next();
}

function nextSubset() {
    // const subsetLimit = 20;
    const subsetLimit = optRoute.length - 1;
    if (subsetIdx < subsetLimit) {
        var nextSubsetIdx = subsetIdx + subsetIdxInc - 1;
        var endPointIdx = Math.min(subsetLimit, nextSubsetIdx);

        var thisSubset = optRoute.slice(subsetIdx, endPointIdx + 1);
        var startPoint = thisSubset[0];
        var midPoints = thisSubset.slice(1, thisSubset.length - 1);
        var endPoint = thisSubset[thisSubset.length - 1];

        setTimeout(getRoutes.bind(null, startPoint, endPoint, midPoints, nextSubset), delay);

        // // Diagnostic print outs
        // console.log('subsetIdx: ' + subsetIdx + ' nextSubsetIdx: ' + nextSubsetIdx + ' endPointIdx: ' + endPointIdx);

        subsetIdx = endPointIdx;
    } else {
        // // We're done. Show map bounds
        // map.fitBounds(bounds);
        displayRoutes();
        console.log('We are done at subsetIdx:: ' + subsetIdx);
    }
}

function displayRoutes() {
    console.log('Hello:: ' + subsetIdx);
    for (i = 0; i < routeDispList.length; i++) {
        routeDispList[i].setMap(map);
    }

    const tourStart = document.getElementById("tour-start");
    tourStart.innerHTML = "Wonderland";

    const tourEnd = document.getElementById("tour-end");
    tourEnd.innerHTML = "Mt. Doom";

    const tourLength = document.getElementById("tour-length");
    tourLength.innerHTML = totalDist;

    const summaryPanel = document.getElementById("route-panel");
    summaryPanel.innerHTML = "";

    for (let i = 0; i < optRoute.length; i++) {
        const routeSegment = i + 1;
        summaryPanel.innerHTML +=
        "<b>Route Segment: " + optRoute[i].location.lat + "</b><br>";
        summaryPanel.innerHTML += optRoute[i].location.lng + " to ";
    }
}
