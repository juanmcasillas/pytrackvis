var mapManager = {
    prefix: 'pytrackvis_',         // used to mark our custom layers in the map
    is3D: false,
    terrain: false,
    track: null,
    terrain_source: null,
    marker: new maplibregl.Marker(),

    change: function() {
        if (this.is3D == false) {
            this.is3D= true;
            window.map.setPitch(60);
            window.map.dragRotate.enable();
            window.map.keyboard.enable(); 
            window.map.touchZoomRotate.enableRotation();
            window.map.setTerrain(this.terrain_source)
            this.terrain = true
        }
        else {
            this.is3D = false;
            window.map.setPitch(0);
            window.map.dragRotate.disable();
            window.map.keyboard.disable(); 
            window.map.touchZoomRotate.disableRotation();
            window.map.setTerrain(null)
            this.terrain = false;
        }
    },
    recenter: function() {
        window.map.fitBounds( track.bounds )
       
        //window.map.setCenter({ lon: track.center.long, lat: track.center.lat })
    },
    update_terrain: function() {
        if (this.terrain) {
              window.map.setTerrain(this.terrain_source)
        }
    },
    layer_prefix: function(layer_name) {
        return this.prefix + layer_name;
    },
    track_data: function() {
        return this.layer_prefix(`track_${track.id}`)
    },
    marker_off: function() {
        this.marker.setOpacity(0)
    },
    marker_on: function() {
        this.marker.setOpacity(1)
    }
    

}

function draw_map(track, MAPTILER_KEY, style_id, debug=false) {


    var load_terrain = true;
    var hillshading = false;
    var load_buildings = false; // fancy but not too useful

    if (debug == true) {
        load_terrain = false;
        hillshading = false;
         load_buildings = false;
    }

    const map = (window.map = new maplibregl.Map({
        container: 'map',
        bearing: 0,
        //pitch: 0,
        hash: true,
        style: `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,
        maxZoom: 18,
        maxPitch: 80,
        antialias: true,
        maplibreLogo: false,
        bounds: track.bounds,
        //zoom: 14,
        //center: { lon: track.center.long, lat: track.center.lat }
    }));
    
    map.dragRotate.disable();
    map.keyboard.disable(); 
    map.touchZoomRotate.disableRotation();
    
    mapManager.track = track
    mapManager.terrain_source = { source: 'pytrackvis_terrain' }
    mapManager.marker.setLngLat([track.begin.long, track.begin.lat, track.begin.elev]).addTo(map);
    mapManager.marker.setOpacity(0)
    
    
    
    // used when change the map style (topo, stellite, etc)
    map.on('style.load', () => {
        mapManager.update_terrain();
    });

    // main callback
    map.on('load', async () => {

        const image = await map.loadImage('/static/img/icons/marker-wpt-small.png');
        map.addImage('custom-marker', image.data);

        map.addControl(new maplibregl.FullscreenControl({container: document.querySelector('body')}),  'top-right');
        map.addControl(
            new maplibregl.NavigationControl({
                visualizePitch: false,
                showZoom: true,
                showCompass: true
            }, 
            'top-right')
        );
        map.addControl(new maplibregl.ScaleControl({ unit: 'metric'}), 'bottom-right');
        map.addControl(new maplibreGLMeasures.default({ units: 'metric'}), 'top-right');


        map.addSource(mapManager.layer_prefix(`track_${track.id}`), {
            type: "geojson",
            data: `/track/as_geojson?id=${track.id}`
        });
        map.addLayer({
            'id': mapManager.layer_prefix(`track_${track.id}_layer`),
            'type': 'line',
            'source': mapManager.layer_prefix(`track_${track.id}`),
            'layout': { 
                'line-join': "round", 
                'line-cap': "round"
            },
            'paint': {
                'line-color': '#FFFF50',    // high contrast
                //'line-color': '#880ED4',  // low contrast
                'line-width': 5
            }
        });
        
        //
        // terrain info.
        // 

        
        if (load_terrain) {

            map.addSource(mapManager.layer_prefix("terrain"), {
                type: "raster-dem",
                url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
            });

            map.setTerrain({
                source: mapManager.layer_prefix("terrain")
            });

            //testtest
            

            if (hillshading) {
                // this doesn't produce any effect for now.
                // keep it disabled.
                map.addSource(mapManager.layer_prefix("terrain_hs"), {
                    type: "raster-dem",
                    url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
                });
                map.addLayer({
                    'id': mapManager.layer_prefix('hillshading'),
                    'source': mapManager.layer_prefix('terrain_hs'),
                    'type': 'hillshade'
                    }
                );
    
            }
            
        }
       
        //test for places
        map.addSource(mapManager.layer_prefix('places'), {
            type: "geojson",
            data: "/places/as_geojson"
        });
        map.addLayer({
            'id': mapManager.layer_prefix('places-layer'),
            'source': mapManager.layer_prefix('places'),
            'type': 'symbol',
            'layout': {
                'icon-allow-overlap': true,
                'icon-image': 'custom-marker',
                'text-field': ['get', 'name'],
                'text-font': [
                    'Open Sans Semibold',
                    'Arial Unicode MS Bold'
                ],
                'text-offset': [0, 1.25],
                'text-anchor': 'top',
                'text-size': 12,
                
            },
            'paint': {
                'text-color': '#EEEEEE'
            }
        });

        if (load_buildings) {
            // for Adding the buildings at top
            let labelLayerId;
            const layers = map.getStyle().layers;
            for (let i = 0; i < layers.length; i++) {
                if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
                    labelLayerId = layers[i].id;
                    break;
                }
            }
            map.addSource(mapManager.layer_prefix('openmaptiles'), {
                    url: `https://api.maptiler.com/tiles/v3/tiles.json?key=${MAPTILER_KEY}`,
                    type: 'vector',
            });
            map.addLayer({
                'id': mapManager.layer_prefix('3d-buildings'),
                'source': mapManager.layer_prefix('openmaptiles'),
                'source-layer': 'building',
                'type': 'fill-extrusion',
                'minzoom': 14,
                'filter': ['!=', ['get', 'hide_3d'], true],
                'paint': {
                    'fill-extrusion-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'render_height'], 0, 'lightgray', 200, 'royalblue', 400, 'lightblue'
                    ],
                    'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        14,
                        0,
                        18,
                        ['get', 'render_height']
                    ],
                    'fill-extrusion-base': ['case',
                        ['>=', ['get', 'zoom'], 16],
                        ['get', 'render_min_height'], 0
                    ]
                }
            }, labelLayerId);
        }

        // start as 2D
        //this is done in the map creation because I know what track I'm loading
        //map.fitBounds( track.bounds )
        //map.setCenter({ lon: track.center.long, lat: track.center.lat })
        map.setPitch(0)
        map.setBearing(0)


        // change base map event handler

        document.getElementById(style_id).addEventListener("change", function (event) {
            const styleId = event.target.value

            // we have to do the things in this way,
            // with a know prefix, or the setStyle will skip our 
            // layers.
            if (['satellite', 'hybrid'].includes(styleId)) {
                // use high-contrast color.
                map.setPaintProperty(mapManager.layer_prefix(`track_${track.id}_layer`), 'line-color', '#FFFF50');
            } else {
                map.setPaintProperty(mapManager.layer_prefix(`track_${track.id}_layer`), 'line-color', '#880ED4');
            }

            map.setStyle(`https://api.maptiler.com/maps/${styleId}/style.json?key=${MAPTILER_KEY}`, {
                transformStyle: (previousStyle, nextStyle) => {
                  var custom_layers = previousStyle.layers.filter(layer => {
                    return layer.id.startsWith(mapManager.layer_prefix(''))
                  });
                  var layers = nextStyle.layers.concat(custom_layers);
              
                  var sources = nextStyle.sources;
                  for (const [key, value] of Object.entries(previousStyle.sources)) {
                    if (key.startsWith(mapManager.layer_prefix(''))) {
                      sources[key] = value;
                    }
                  }
                  return {
                    ...nextStyle,
                    sources: sources,
                    layers: layers
                  };
                }
              });


        });

        // end of map onLoad
        // call the rest of things here after map loading.
          // its a promise
        let track_data = map.getSource(mapManager.track_data())
        track_data.getData().then( function(results) {
            plotElevation(results,map,mapManager)
        });
    })

    map.on('click', mapManager.layer_prefix('places-layer'), (e) => {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const description = e.features[0].properties.description;

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        new maplibregl.Popup()
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
    });

    // Change the cursor to a pointer when the mouse is over the places layer.
    map.on('mouseenter', 'places', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    // Change it back to a pointer when it leaves.
    map.on('mouseleave', 'places', () => {
        map.getCanvas().style.cursor = '';
    });

    // show lat/long if needed
    // map.on('mousemove', (e) => {
    //     document.getElementById('map-info').innerHTML =
    //         // e.point is the x, y coordinates of the mousemove event relative
    //         // to the top-left corner of the map
    //        `${JSON.stringify(e.point)
    //         }<br />${
    //             // e.lngLat is the longitude, latitude geographical position of the event
               
    //             JSON.stringify(e.lngLat.wrap())}`;
    // });

}