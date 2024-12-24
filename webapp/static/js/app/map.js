
/**
 * call this for the main program to create and init the custom map
 * hillshading for now is not supported. Big function, called only once
 * 
 * @param {*} track 
 * @param {*} MAPTILER_KEY 
 * @param {*} style_id 
 * @param {*} debug 
 */
function draw_map(track, MAPTILER_KEY, style_id, places_layers) {

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
    mapManager.init_defaults(track, MAPTILER_KEY, places_layers)

    map.on('style.load', async () => {
        mapManager.update_terrain();
        mapManager.load_icons();
    });
   
    // //////////////////////////////////////////////////////////////////////////
    //
    // main callback
    //
    // //////////////////////////////////////////////////////////////////////////

    map.on('load', async () => {
    
        mapManager.load_icons()

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
        
        
        // //////////////////////////////////////////////////////////////////////////
        //
        // layer definition. Check map_manager for the labels. use prefix to
        // allow change the style (map style). Order is relevant (from top to)
        // button, latest is top in view.
        //
        // //////////////////////////////////////////////////////////////////////////

        //
        // terrain info.
        // 
        
        if (mapManager.load_terrain) {

            map.addSource(mapManager.terrain_source_id, {
                type: "raster-dem",
                url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
            });

            map.setTerrain({
                source: mapManager.terrain_source_id
            });

            //
            // WARNING
            // contour lines are loaded from map_manager.show_hide_contour()
            //

            // map.addSource(mapManager.city_limits_source_id, {
            //     type: "geojson",
            //     data: "/static/geojson/spain/georef-spain-municipio.geojson"
                        // });
            // map.addLayer({
            //     'id': mapManager.city_limits_layer_id,
            //     'source': mapManager.city_limits_source_id,
            //     'type': 'line',
            //     'layout': { 
            //         'line-join': "round", 
            //         'line-cap': "round"
            //     },
            //     'paint': {
            //         //'line-color': '#909090',    // high contrast
            //         'line-dasharray': [5,10],
            //         'line-color': '#880ED4',  // low contrast
            //         'line-width': 1
            //     }
            // });
            


            if (mapManager.load_hillshading) {
                // this doesn't produce any effect for now.
                // keep it disabled.
                map.addSource(mapManager.terrain_hillshading_source_id, {
                    type: "raster-dem",
                    url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${MAPTILER_KEY}`
                });
                map.addLayer({
                    'id': mapManager.terrain_hillshading_layer_id,
                    'source': mapManager.terrain_hillshading_source_id,
                    'type': 'hillshade'
                    }
                );
    
            }
            
        }
        //
        // state & city limits are loaded in map_manager in show/hide buttons
        //

        //
        // load the GEOJSON for places layer.
        // 

        map.addSource(mapManager.places_source_id, {
            type: "geojson",
            data: "/places/as_geojson"
        });
        
        mapManager.configure_places()
        // loaded in mapManager to filter the elements in layers based on properties.
        // map.addLayer({
        //     'id': mapManager.places_layer_id,
        //     'source': mapManager.places_source_id,
        //     'type': 'symbol',
        //     'layout': {
        //         'visibility': 'none',
        //         'icon-allow-overlap': true,
        //         'text-allow-overlap': true,
        //         'icon-overlap': 'always',
        //         'text-overlap': 'always',
        //         'icon-image': ['get', 'icon'],
        //         'text-field': ['get', 'name'],
        //         'text-font': [
        //             'Open Sans Semibold',
        //             'Arial Unicode MS Bold'
        //         ],
        //         'text-offset': [0, 1.25],
        //         'text-anchor': 'top',
        //         'text-size': 12,
        //         'text-letter-spacing': 0.05,
                
        //     },
        //     'paint': {
        //         'text-color': '#FFFFFF',
        //         'text-halo-color': '#ffffff',
        //         'text-halo-width': 0.1
        //     }
        // });

        if (mapManager.load_buildings) {
            // for Adding the buildings at top
            let labelLayerId;
            const layers = map.getStyle().layers;
            for (let i = 0; i < layers.length; i++) {
                if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
                    labelLayerId = layers[i].id;
                    break;
                }
            }
            map.addSource(mapManager.buildings_source_id, {
                    url: `https://api.maptiler.com/tiles/v3/tiles.json?key=${MAPTILER_KEY}`,
                    type: 'vector',
            });
            map.addLayer({
                'id': mapManager.buildings_layer_id,
                'source': mapManager.buildings_source_id,
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

        map.addSource(mapManager.catastro_source_id, {
            type: "geojson",
            data: {
                "id": generate_uuid(),
                "type": "FeatureCollection",
                "features": [ ]
            }
        });

        map.addLayer({
            'id': mapManager.catastro_poly_layer_id,
            'type': 'fill',
            'source': mapManager.catastro_source_id,
            'layout': { },
            'paint': {
                'fill-color': [ 'get', 'style'],
                'fill-opacity': 0.7
            },
            'filter': ['==', '$type', 'Polygon']
        });
        
        // we use the this.track_source_id to add the line features, instead
        // of duplicate the work.
        // map.addLayer({
        //     'id': mapManager.catastro_line_layer_id,
        //     'type': 'line',
        //     'source': mapManager.catastro_source_id,
        //     'layout': { 
        //                 'line-join': "round", 
        //                 'line-cap': "round"
        //             },
        //     'paint': {
        //         'line-color': [ 'get', 'style'],
        //         //'line-color': '#FFFF50',
        //         'line-width': 5
        //     },
        //     'filter': ['==', '$type', 'LineString']
        // });

        map.addSource(mapManager.track_source_id, {
            type: "geojson",
            data: `/track/as_geojson?id=${track.id}`
        });
        map.addLayer({
            'id': mapManager.track_layer_id,
            'type': 'line',
            'source': mapManager.track_source_id,
            'layout': { 
                'line-join': "round", 
                'line-cap': "round"
            },
            'paint': {
                'line-color': [ "case",
                    ["has", 'style'],
                    ['get', 'style'],
                    mapManager.track_color,
                ],
                // 'line-color': '#FFFF50',    // high contrast
                //'line-color': '#880ED4',  // low contrast
                'line-width': 5,
     
            }
        });
   

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
                mapManager.set_normal_contrast();

            } else {
                mapManager.set_high_contrast();
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

        let track_data = map.getSource(mapManager.track_source_id)
        track_data.getData().then( function(results) {
            plotElevation(results,map,mapManager)
        });


    }) // end of map onload event (big one!)


    map.on('click', mapManager.places_layer_id, (e) => {
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
            .setHTML((description === undefined ? 'No description available' : description))
            .addTo(map);
    });


    map.on('click',  (e) => {
        
        // only check catastro if mode is activated
        if ( !mapManager.catastro_flag) {
            return;
        }

        // issue the call directly.
        mapManager.check_catastro_point(lat=e.lngLat.lat, lng=e.lngLat.lng)
        return 
    });


    map.on('click', mapManager.catastro_poly_layer_id, (e) => {
        e.features[0].properties.info = JSON.parse(e.features[0].properties.info)
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`
                <div>
                <h5>${e.features[0].properties.cdc}</h5>
                <h6>Public: ${e.features[0].properties.is_public}</h6>
                <ul>
                 <li>RC: ${e.features[0].properties.rc}
                 <li>CCC: ${e.features[0].properties.ccc}
                 <li>CodMun: ${e.features[0].properties.info.codigo_municipio}
                 <li>Designation: ${e.features[0].properties.info.denominacion_clase}
                 <li>Mun: ${e.features[0].properties.info.nombre_municipio}
                 <li>Prov: ${e.features[0].properties.info.nombre_provincia}
                 <li>Par: ${e.features[0].properties.info.nombre_paraje}
                 <li>Dom: ${e.features[0].properties.info.domicilio_tributario}
                </ul>
                </div>
            `)
            .addTo(map);
            //console.log("features", e.features[0].properties)
    });
  
    // Change the cursor to a pointer when the mouse is over the places layer.
    map.on('mouseenter', mapManager.places_layer_id, () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    // Change it back to a pointer when it leaves.
    map.on('mouseleave', mapManager.places_layer_id, () => {
        map.getCanvas().style.cursor = '';
    });

 
    // don't delete this, please. Information.

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