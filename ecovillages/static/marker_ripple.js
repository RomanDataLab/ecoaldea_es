// marker_ripple.js
// This script adds mouseover event listeners to all Leaflet markers for zoom and ripple effect

function addRipple(map, lat, lon, color) {
    for (let i = 0; i < 3; i++) {
        setTimeout(function() {
            var circle = L.circle([lat, lon], {
                color: color,
                fillColor: color,
                fillOpacity: 0.2,
                radius: 200 + i*100
            }).addTo(map);
            setTimeout(function() { map.removeLayer(circle); }, 600);
        }, 200 * i);
    }
}

// Wait for the map and markers to be available
setTimeout(function() {
    if (typeof markers !== 'undefined' && markers.length > 0) {
        markers.forEach(function(marker) {
            marker.on('mouseover', function(e) {
                var map = marker._map;
                if (map) {
                    var currZoom = map.getZoom();
                    map.setView(marker.getLatLng(), Math.round(currZoom * 1.2));
                    // Use marker.options.color for ripple color
                    addRipple(map, marker.getLatLng().lat, marker.getLatLng().lng, marker.options.color || 'blue');
                }
            });
        });
    }
}, 500); 