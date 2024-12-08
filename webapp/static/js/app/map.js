var map_mode = {
    is3D: false,
    terrain: false,
    MAPTILER_KEY: null,
    track: null,
    terrain_source: '',

    change: function() {
        if (this.is3D == false) {
            this.is3D= true;
            window.map.setPitch(60);
            window.map.dragRotate.enable();
            window.map.keyboard.enable(); 
            window.map.touchZoomRotate.enableRotation();
            window.map.setTerrain(this.terrain_source)
            this.terrain = true

            // if (this.terrain == false) {
            //     window.map.addSource("pytrackvis_terrain", {
            //         type: "raster-dem",
            //         url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${this.MAPTILER_KEY}`
            //     });
                
            //     window.map.setTerrain({
            //         source: "pytrackvis_terrain"
            //     });
            //     this.terrain = true;
            // }
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
}

function draw_map_2D(track, MAPTILER_KEY, style_id, debug=false) {

    map_mode.MAPTILER_KEY = MAPTILER_KEY // for map change 2D/3D
    map_mode.track = track
    map_mode.terrain_source = { source: 'pytrackvis_terrain' }

    var load_terrain = true;
    var hillshading = false;
    var load_buildings = true;


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
    
    //https://gist.github.com/ryanbaumann/7f9a353d0a1ae898ce4e30f336200483/96bea34be408290c161589dcebe26e8ccfa132d7
    //https://github.com/maplibre/maplibre-gl-js/issues/2587
    // var customLayers = [
    //     {
    //         source_id: `pytrackvis_track_${track.id}`,
    //         source: {
    //             type: "geojson",
    //             data: `/tracks/as_geojson?id=${track.id}`
    //         },
    //         layer: {
    //             'id': `pytrackvis_track_${track.id}_layer`,
    //             'type': 'line',
    //             'source': `pytrackvis_track_${track.id}`,
    //             'layout': { 
    //                 'line-join': "round", 
    //                 'line-cap': "round"
    //             },
    //             'paint': {
    //                 'line-color': '#FFFF50', 
    //                 'line-width': 4
    //             }
    //         }
    //     },
    //     {
    //         source_id: 'pytrackvis_openmaptiles',
    //         source: {
    //             url: `https://api.maptiler.com/tiles/v3/tiles.json?key=${MAPTILER_KEY}`,
    //             type: 'vector',
    //         },
    //         layer: {
    //             'id': 'pytrackvis_3d-buildings',
    //             'source': 'pytrackvis_openmaptiles',
    //             'source-layer': 'building',
    //             'type': 'fill-extrusion',
    //             'minzoom': 16,
    //             'filter': ['!=', ['get', 'hide_3d'], true],
    //             'paint': {
    //                 'fill-extrusion-color': [
    //                     'interpolate',
    //                     ['linear'],
    //                     ['get', 'render_height'], 0, 'lightgray', 200, 'royalblue', 400, 'lightblue'
    //                 ],
    //                 'fill-extrusion-height': [
    //                     'interpolate',
    //                     ['linear'],
    //                     ['zoom'],
    //                     15,
    //                     0,
    //                     16,
    //                     ['get', 'render_height']
    //                 ],
    //                 'fill-extrusion-base': ['case',
    //                     ['>=', ['get', 'zoom'], 16],
    //                     ['get', 'render_min_height'], 0
    //                 ]
    //             }
    //         }
    //     }
    // ]
    map.on('style.load', () => {
        map_mode.update_terrain();
    });

    map.on('load', () => {

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
        //
        // not needed
        //map.addControl(new maplibregl.TerrainControl({ source: 'pytrackvis_terrain' }));
        
        // load our custom layers. This will be moved again inside the call.
        // for (var i = 0; i < customLayers.length; i++) {
        //     var me = customLayers[i]
        //     map.addSource(me.source_id, me.source);
        //     map.addLayer(me.layer)
        // }

        map.addSource(`pytrackvis_track_${track.id}`, {
            type: "geojson",
            data: `/track/as_geojson?id=${track.id}`
        });
        map.addLayer({
            'id': `pytrackvis_track_${track.id}_layer`,
            'type': 'line',
            'source': `pytrackvis_track_${track.id}`,
            'layout': { 
                'line-join': "round", 
                'line-cap': "round"
            },
            'paint': {
                'line-color': '#FFFF50', 
                //'line-color': '#880ED4', 
                'line-width': 5
            }
        });
        
        //
        // terrain info.
        // 

        
        if (load_terrain) {

            map.addSource("pytrackvis_terrain", {
                type: "raster-dem",
                url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
            });

            map.setTerrain({
                source: "pytrackvis_terrain"
            });

            if (hillshading) {
                // this doesn't produce any effect for now.
                map.addSource("pytrackvis_terrain_hs", {
                    type: "raster-dem",
                    url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
                });
                map.addLayer({
                    'id': 'pytrackvis_hillshading',
                    'source': 'pytrackvis_terrain_hs',
                    'type': 'hillshade'
                    }
                );
    
            }
            
        };
       
        
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
            map.addSource('pytrackvis_openmaptiles', {
                    url: `https://api.maptiler.com/tiles/v3/tiles.json?key=${MAPTILER_KEY}`,
                    type: 'vector',
            });
            map.addLayer({
                'id': 'pytrackvis_3d-buildings',
                'source': 'pytrackvis_openmaptiles',
                'source-layer': 'building',
                'type': 'fill-extrusion',
                'minzoom': 12,
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
                        15,
                        0,
                        18,
                        ['get', 'render_height']
                    ],
                    'fill-extrusion-base': ['case',
                        ['>=', ['get', 'zoom'], 18],
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
                map.setPaintProperty(`pytrackvis_track_${track.id}_layer`, 'line-color', '#FFFF50');
            } else {
                map.setPaintProperty(`pytrackvis_track_${track.id}_layer`, 'line-color', '#880ED4');
            }

            map.setStyle(`https://api.maptiler.com/maps/${styleId}/style.json?key=${MAPTILER_KEY}`, {
                transformStyle: (previousStyle, nextStyle) => {
                  var custom_layers = previousStyle.layers.filter(layer => {
                    return layer.id.startsWith('pytrackvis_')
                  });
                  var layers = nextStyle.layers.concat(custom_layers);
              
                  var sources = nextStyle.sources;
                  for (const [key, value] of Object.entries(previousStyle.sources)) {
                    if (key.startsWith('pytrackvis_')) {
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
    })

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