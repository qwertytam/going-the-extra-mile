const apiKey = config.apiKey;
const urlStart = 'https://maps.googleapis.com/maps/api/js?key=';
const urlEnd = '&callback=initMap&libraries=&v=weekly';

// Create the script tag, set the appropriate attributes
var script = document.createElement('script');
script.src = urlStart + apiKey + urlEnd
script.defer = true;

// Attach the callback function to the `window` object
window.initMap = function() {
  // JS API is loaded and available
};

// Append the 'script' element to 'head'
document.head.appendChild(script);
