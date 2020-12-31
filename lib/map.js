var delay = 100;  // Delay time in milliseconds
var delayInc = 100;

var subsetIdx = 0;  // Track which subset we are up to
var subsetIdxInc = 10;  // Subset increment
var routeDispList = [];  // Store routes to be displayed

var map = {};
var bounds = {};
var dirService = {};

var dirDisplayOptions = {
    preserveViewport: true,
    suppressMarkers: true,
    strokeColor: 'red',
};

var totalDist = 0;
var totalDur = 0;
var markerLocations = [];

function initMap() {
    if ('google' in window && typeof google === 'object' && typeof google.maps === 'object') {
        console.log('Google Maps API loaded successfully');
    } else {
        console.log('Google Maps API NOT loaded')
    }

    const centerLatLng = { lat: 39.828175, lng: -98.5795 };
    const mapOptions = {
        zoom: 4,
        center: centerLatLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }

    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    dirService = new google.maps.DirectionsService();
    nextSubset();
}

function getRoutes(start, end, points, next) {
    var dirDisplay = new google.maps.DirectionsRenderer(dirDisplayOptions);
    var wypts = [];
    for (var i = 0; i < points.length; i++) {
        wypts.push({
            location: points[i].location,
            stopover: false},
        );
    }
    var request = {
        origin: start.location,
        destination: end.location,
        waypoints: wypts,
        optimizeWaypoints: false,
        travelMode: google.maps.TravelMode.DRIVING
    };

    dirService.route(request, function(response, status) {
        // console.log('API status response: ' + status + ' for start: ' + start.location.lat + ' end: ' + end.location.lat);
        if (status == google.maps.DirectionsStatus.OK) {

            dirDisplay.setDirections(response);
            var subsetRoute = response.routes[0];  // Should only be 1 route

            for (let i = 0; i < subsetRoute.legs.length; i++){
                legi = subsetRoute.legs[i];
                totalDist += legi.distance.value;
                totalDur += legi.duration.value;

                if (markerLocations.length == 0) {
                    // Only do this once, otherwise, will use end_location to
                    // get the end and overlapping start of subsequent subsets
                    markerLocations.push(legi.start_location);
                }

                for (let j = 0; j < legi.via_waypoints.length; j++) {
                    markerLocations.push(legi.via_waypoints[j]);
                }
                markerLocations.push(legi.end_location);
            }
            const pctInterval = 20;
            var pctDone = 100 * (subsetIdx + 1) / optRoute.length;
            var pctDoneScale = Math.round(pctDone * pctInterval / 100);
            console.log('pctDone: ' + pctDone);
            const strDone = '#';
            const strToGo = '_';
            var strStatus = '[' + strDone.repeat(pctDoneScale) + strToGo.repeat(pctInterval - pctDoneScale) + '] ' + Math.round(pctDone) + '%';
            var calcProgress = document.getElementById("calc-progress");
            calcProgress.innerHTML = strStatus;

            var calcDelay = document.getElementById("calc-delay");
            calcDelay.innerHTML = delay + ' ms';
            // console.log('Total distance: ' + totalDist + ' m');
        }
        // ====== Decode the error status ======
        else {
            // If we were sending the requests to fast, try this one again and increase the delay
            if (status == google.maps.GeocoderStatus.OVER_QUERY_LIMIT) {
                delay += delayInc;
                console.log('OVER_QUERY_LIMIT subsetIdx: ' + subsetIdx + ' delay now: ' + delay + ' ms');
                subsetIdx = subsetIdx - subsetIdxInc + 1;
            } else {
                var reason = 'Code ' + status;
                window.alert('Error: ' + reason + ' subsetIdx: ' + subsetIdx + ' delay: ' + delay + ' ms');
            }
        }
        dirDisplay.setMap(map);
        routeDispList.push(dirDisplay);
        next();
    });
}

function nextSubset() {
    // const subsetLimit = 25;
    const subsetLimit = optRoute.length - 1;
    if (subsetIdx < subsetLimit) {
        var nextSubsetIdx = subsetIdx + subsetIdxInc - 1;
        var endPointIdx = Math.min(subsetLimit, nextSubsetIdx);

        var thisSubset = optRoute.slice(subsetIdx, endPointIdx + 1);
        var startPoint = thisSubset[0];
        var midPoints = thisSubset.slice(1, thisSubset.length - 1);
        var endPoint = thisSubset[thisSubset.length - 1];

        setTimeout(getRoutes.bind(null, startPoint, endPoint, midPoints, nextSubset), delay);
        // console.log('subsetIdx: ' + subsetIdx);
        subsetIdx = endPointIdx;
    } else {
        // We're done; show lots of stuff on the map
        displayRoutes();
        displayMarkers();
        map.fitBounds(bounds);
        console.log('We are done at subsetIdx:: ' + subsetIdx);
    }
}

function naStringReturn(str){
    if (str.length == 0){
        return '[no seat]';
    } else {
        return str;
    }
}

function concateNameStateSeat(routeCounty){
    var str = routeCounty.name + ', ';
    str += routeCounty.state + ', ';
    str += naStringReturn(routeCounty.seat);
    return str;
}

function secsToDaysHrsMins(secs){
    secsRemainder = secs % 60;

    secs = Math.floor(secs / 60); // Number of whole minutes
    minsRemainder = secs % 60;

    secs = Math.floor(secs / 60); // Number of whole hours
    hrsRemainder = secs % 24;

    secs = Math.floor(secs / 24); // Number of whole days; ignores leap seconds

    var daysHrsMins = secs + ' days, ';
    daysHrsMins += hrsRemainder + ' hrs, ';
    daysHrsMins += minsRemainder + ' mins';

    return daysHrsMins;
}

function displayRoutes() {
    // for (i = 0; i < routeDispList.length; i++) {
    //     routeDispList[i].setMap(map);
    // }

    const tourStart = document.getElementById("tour-start");
    tourStart.innerHTML = concateNameStateSeat(optRoute[0].county);

    const tourEnd = document.getElementById("tour-end");
    tourEnd.innerHTML = concateNameStateSeat(optRoute[optRoute.length - 1].county);

    const tourLength = document.getElementById("tour-length");
    totalDistKm = Math.round(totalDist / 1000);  // Convert metres to kilometres
    tourLength.innerHTML = totalDistKm.toLocaleString() + ' km';

    const tourDur = document.getElementById("tour-duration");
    tourDur.innerHTML = secsToDaysHrsMins(totalDur);

    const routePanel = document.getElementById("route-panel");
    routePanel.innerHTML = '';
    for (let i = 0; i < optRoute.length; i++) {
        var idx = i + 1;
        routePanel.innerHTML += idx + ': ';
        routePanel.innerHTML += concateNameStateSeat(optRoute[i].county);
        routePanel.innerHTML += '<br>';
    }
}

function displayMarkers() {
    // var pinSVGFilled = "M 12,2 C 8.1340068,2 5,5.1340068 5,9 c 0,5.25 7,13 7,13 0,0 7,-7.75 7,-13 0,-3.8659932 -3.134007,-7 -7,-7 z";
    var labelOriginFilled =  new google.maps.Point(12,12);
    // var pinImage = {  // https://developers.google.com/maps/documentation/javascript/reference/marker#MarkerLabel
    //     // path: pinSVGFilled,
    //     path: google.maps.SymbolPath.CIRCLE,
    //     anchor: new google.maps.Point(12,17),
    //     fillOpacity: 1,
    //     strokeWeight: 2,
    //     strokeColor: "white",
    //     scale: 2,
    //     labelOrigin: labelOriginFilled
    // };

    var pinImage = {
        path: google.maps.SymbolPath.CIRCLE,
        fillOpacity: 1,
        strokeWeight: 3,
        strokeColor: "white",
        scale: 12,
    };
    var pinLabel = {
        color: "black",
        fontSize: "small",
        // fontWeight: 'bold',
    };
    var pins = [];
    bounds = new google.maps.LatLngBounds();

    for (i = 0; i < markerLocations.length; i++) {
        if (i == 0){
            var pinColor = "green";
        } else if (i == markerLocations.length - 1) {
            var pinColor = "red";
        } else {
            var pinColor = cmap[Math.round(cmap.length * i / markerLocations.length) - 1];
        }
        pinImage.fillColor = pinColor;

        var cntyName = optRoute[i].county.name;
        pinLabel.text = (i + 1) + '. ' + cntyName.replace(' ', '\n\r');

        var pin = new google.maps.Marker({
            position: markerLocations[i],
            // label: pinLabel,
            label: '' + (i + 1),
            icon: pinImage,
            map: map,
        });
        google.maps.event.addListener(pin, 'click', function() {
            infowindow.setContent(pinLabel);
            infowindow.open(map, pin);
        });
        pins.push(pin);
        bounds.extend(pin.position);
    }
    // Exlclude the first (start) and last (end) pin from the cluser to give
    // them specific green and red fill colour
    pinsForCluster = pins.slice(1, pins.length - 1);
    var markerCluster = new MarkerClusterer(map, pinsForCluster, {
        imagePath: '../images/m',
        imageExtension: 'png',
        maxZoom: 6,
    });
}
