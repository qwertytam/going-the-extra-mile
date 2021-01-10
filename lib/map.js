var delay = Math.floor((Math.random() * 150) + 50) // Delay time in milliseconds, random between 50 and 150
var delayInc = 1

var subsetIdx = 0 // Track which subset we are up to
var subsetIdxInc = 10 // Subset increment
var routeDispList = [] // Store routes to be displayed

var map = {}
var bounds = {}
var dirService = {}

var totalDist = 0
var totalDur = 0
var markerLocations = []
// var infoWindows = [];

var zPanelMsgs = ''

function initMap () {
  if ('google' in window && typeof google === 'object' && typeof google.maps === 'object') {
    console.log('Google Maps API loaded successfully')
  } else {
    console.log('Google Maps API NOT loaded')
  }

  const centerLatLng = { lat: 39.828175, lng: -98.5795 }
  const mapOptions = {
    zoom: 4,
    center: centerLatLng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }

  map = new google.maps.Map(document.getElementById('map'), mapOptions)
  dirService = new google.maps.DirectionsService()

  nextSubset()
}

function rounddp (num, dp) {
  const roundScale = 10 ** dp
  num = Math.round(num * roundScale) / roundScale
  return num
}

function updatePctProgress (current, finish) {
  const pctInterval = 20
  const strDone = '#'
  const strToGo = '_'

  var pctDone = current / finish
  var pctDoneScale = rounddp(pctDone * pctInterval, 2)

  console.log('pctDone: ' + (rounddp(pctDone, 4) * 100) + '%')

  var strStatus = '<b>Progress: </b>'
  strStatus += '[' + strDone.repeat(pctDoneScale)
  strStatus += strToGo.repeat(pctInterval - pctDoneScale) + '] '
  strStatus += rounddp(pctDone * 100, 2) + '%'

  var calcProgress = document.getElementById('calc-progress')
  calcProgress.innerHTML = strStatus
}

function getRoutes (start, end, points, next) {
  var routeLineColour = cmap[rounddp(cmap.length * subsetIdx / optRoute.length, 0)]
  var dirDisplayOptions = {
    preserveViewport: true,
    suppressMarkers: true,
    polylineOptions: {
      strokeColor: routeLineColour
    }
  }

  var dirDisplay = new google.maps.DirectionsRenderer(dirDisplayOptions)
  var wypts = []
  for (var i = 0; i < points.length; i++) {
    wypts.push({
      location: points[i].location,
      stopover: false
    }
    )
  }
  var request = {
    origin: start.location,
    destination: end.location,
    waypoints: wypts,
    optimizeWaypoints: false,
    travelMode: google.maps.TravelMode.DRIVING
  }

  dirService.route(request, function (response, status) {

    if (status === google.maps.DirectionsStatus.OK) {
      dirDisplay.setDirections(response)
      var subsetRoute = response.routes[0] // Should only be 1 route

      for (let i = 0; i < subsetRoute.legs.length; i++) {
        var legi = subsetRoute.legs[i]
        totalDist += legi.distance.value
        totalDur += legi.duration.value

        if (markerLocations.length === 0) {
          // Only do this once, otherwise, will use end_location to
          // get the end and overlapping start of subsequent subsets
          markerLocations.push(legi.start_location)
        }

        for (let j = 0; j < legi.via_waypoints.length; j++) {
          markerLocations.push(legi.via_waypoints[j])
        }
        markerLocations.push(legi.end_location)
      }
      updatePctProgress((subsetIdx + 1), optRoute.length)

      var calcDelay = document.getElementById('calc-delay')
      calcDelay.innerHTML = '<b>Delay: </b> ' + delay + ' ms'
    } else {
    // ====== Decode the error status ======
      // If we were sending the requests to fast, try this one again and increase the delay
      if (status === google.maps.GeocoderStatus.OVER_QUERY_LIMIT) {
        delay = delay * 2 ** delayInc
        delayInc += 1 // double delay each time
        console.log('OVER_QUERY_LIMIT subsetIdx: ' + subsetIdx + ' delay now: ' + delay + ' ms')
        subsetIdx = subsetIdx - subsetIdxInc + 1
    } else if (status === google.maps.GeocoderStatus.ZERO_RESULTS) {
        console.log('ZERO_RESULTS subsetIdx: ' + subsetIdx)
        zPanelMsgs += 'idx=' + subsetIdx
        zPanelMsgs += ' start=' + rounddp(start.location.lat, 4) + ','
        zPanelMsgs += rounddp(start.location.lng, 4)
        zPanelMsgs += ' end=' + rounddp(end.location.lat, 4) + ','
        zPanelMsgs += rounddp(end.location.lng, 4)
        zPanelMsgs += '<br>'
      } else {
        var reason = 'Code ' + status
        window.alert('Error: ' + reason + ' subsetIdx: ' + subsetIdx + ' delay: ' + delay + ' ms')
      }
    }
    dirDisplay.setMap(map)
    routeDispList.push(dirDisplay)
    next()
  })
}

function nextSubset () {
  // const subsetLimit = 125;

  const zeroPanel = document.getElementById('zero-panel')
  const subsetLimit = optRoute.length - 1
  if (subsetIdx < subsetLimit) {
    var nextSubsetIdx = subsetIdx + subsetIdxInc - 1
    var endPointIdx = Math.min(subsetLimit, nextSubsetIdx)

    var thisSubset = optRoute.slice(subsetIdx, endPointIdx + 1)
    var startPoint = thisSubset[0]
    var midPoints = thisSubset.slice(1, thisSubset.length - 1)
    var endPoint = thisSubset[thisSubset.length - 1]

    setTimeout(getRoutes.bind(null, startPoint, endPoint, midPoints, nextSubset), delay)
    subsetIdx = endPointIdx
  } else {
    // We're done; show lots of stuff on the map
    zeroPanel.innerHTML = zPanelMsgs
    updatePctProgress(100, 100)
    displayRoutes()
    updatePctProgress(100, 100)
    displayMarkers()
    updatePctProgress(100, 100)
    map.fitBounds(bounds)
    console.log('We are done at subsetIdx:: ' + subsetIdx)
  }
}

function naStringReturn (str) {
  if (str.length === 0) {
    return '[no seat]'
  } else {
    return str
  }
}

function concateNameStateSeat (routeCounty) {
  var str = routeCounty.name + ', '
  str += routeCounty.state + ', '
  str += naStringReturn(routeCounty.seat)
  return str
}

function secsToDaysHrsMins (secs) {
  // var secsRemainder = secs % 60

  secs = Math.floor(secs / 60) // Number of whole minutes
  var minsRemainder = secs % 60

  secs = Math.floor(secs / 60) // Number of whole hours
  var hrsRemainder = secs % 24

  secs = Math.floor(secs / 24) // Number of whole days; ignores leap seconds

  var daysHrsMins = secs + ' days, '
  daysHrsMins += hrsRemainder + ' hrs, '
  daysHrsMins += minsRemainder + ' mins'

  return daysHrsMins
}

function displayRoutes () {
  // for (i = 0; i < routeDispList.length; i++) {
  //   routeDispList[i].setMap(map);
  // }

  const tourStart = document.getElementById('tour-start')
  tourStart.innerHTML = concateNameStateSeat(optRoute[0].county)

  const tourEnd = document.getElementById('tour-end')
  tourEnd.innerHTML = concateNameStateSeat(optRoute[optRoute.length - 1].county)

  const tourLength = document.getElementById('tour-length')
  var totalDistKm = rounddp(totalDist / 1000, 2) // Convert metres to kilometres
  tourLength.innerHTML = totalDistKm.toLocaleString() + ' km'

  const tourDur = document.getElementById('tour-duration')
  tourDur.innerHTML = secsToDaysHrsMins(totalDur)

  const routePanel = document.getElementById('route-panel')
  routePanel.innerHTML = ''
  for (let i = 0; i < optRoute.length; i++) {
    var idx = i + 1
    routePanel.innerHTML += idx + ': '
    routePanel.innerHTML += concateNameStateSeat(optRoute[i].county)
    routePanel.innerHTML += '<br>'
    updatePctProgress((i + 1), optRoute.length)
  }
}

function makeInfoWindowEvent (map, infowindow, contentString, pin) {
  google.maps.event.addListener(pin, 'click', function () {
    infowindow.setContent(contentString)
    infowindow.open(map, pin)
  })
}

function displayMarkers () {
  var pinImage = {
    path: google.maps.SymbolPath.CIRCLE,
    fillOpacity: 1,
    strokeWeight: 3,
    strokeColor: 'white',
    scale: 15
  }
  // var pinLabel = {
  //   color: 'black',
  //   fontSize: 'small',
  //   // fontWeight: 'bold',
  // }
  var pins = []
  var infowindow = new google.maps.InfoWindow()
  bounds = new google.maps.LatLngBounds()
  var pinColour = ''

  for (var i = 0; i < markerLocations.length; i++) {
    if (i === 0) {
      pinColour = 'green'
    } else if (i === markerLocations.length - 1) {
      pinColour = 'red'
    } else {
      pinColour = cmap[rounddp(cmap.length * (i + 1) / markerLocations.length, 0)]
    }
    pinImage.fillColor = pinColour

    var infoText = 'County: ' + optRoute[i].county.name + '\n\r' + '<br>'
    infoText += 'County Seat: ' + naStringReturn(optRoute[i].county.seat)

    var pin = new google.maps.Marker({
      position: markerLocations[i],
      label: '' + (i + 1),
      icon: pinImage,
      map: map
    })

    makeInfoWindowEvent(map, infowindow, infoText, pin)
    pins.push(pin)
    bounds.extend(pin.position)
    updatePctProgress(i + 1, markerLocations.length)
  }
  // Exlclude the first (start) and last (end) pin from the cluser to give
  // them specific green and red fill colour
  var pinsForCluster = pins.slice(1, pins.length - 1)
  var markerCluster = new MarkerClusterer(map, pinsForCluster, {
    imagePath: '../images/m',
    imageExtension: 'png',
    maxZoom: 6
  })
}
