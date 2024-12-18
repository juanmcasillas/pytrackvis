var mapManager = {
    prefix: 'pytrackvis_',         // used to mark our custom layers in the map
    is3D: false,
    terrain: false,
    track: null,
    terrain_source: null,
    marker: new maplibregl.Marker(),
    catastro_flag: null,

    icons: [
        'nc', 
        'hc',
        // add custom on init
        '10',
        '93',
        '46',
        '48',
        '63',
        '52',
        '53',
        '36',
        '140',
        '141',
        '142',
        '105',
        '54',
        '14',
        'nc',
        '106',
    ],


    init_defaults: function(track) {
        this.track = track
        this.terrain_source = { source: 'pytrackvis_terrain' }
        this.marker.setLngLat([track.begin.long, track.begin.lat, track.begin.elev]).addTo(map);
        this.marker.setOpacity(0)
      

        this.places_source_id = this.layer_prefix('places-source')
        this.places_layer_id = this.layer_prefix('places-layer')
        this.track_source_id = this.layer_prefix(`track_${this.track.id}-source`)
        this.track_layer_id = this.layer_prefix(`track_${this.track.id}-layer`)
        this.catastro_source_id = this.layer_prefix('catastro-source')
        this.catastro_layer_id = this.layer_prefix('catastro-layer')
        // implicit load of required icons to speed up
        // for (var i=0; i<265; i++) {
        //     this.icons.push(`${i}`)
        // }
    },

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
    marker_off: function() {
        this.marker.setOpacity(0)
    },
    marker_on: function() {
        this.marker.setOpacity(1)
    },
    load_icons: async function() {
        
        for (const icon of mapManager.icons) { 
            if (! window.map.getImage(icon)) {
                //console.log(`X reloading ${icon} /static/img/icons/wpt/${icon}.png`)
                const image = await window.map.loadImage(`/static/img/icons/wpt/${icon}.png`);
                //console.log(image)
                //check again
                if (! window.map.getImage(icon)) {
                     window.map.addImage(icon, image.data); 
                }
            }
        }
    },
    set_normal_contrast: function() {
        var trk_layer = this.layer_prefix(`track_${this.track.id}_layer`)
        var places_layer = this.layer_prefix('places-layer')

        window.map.setPaintProperty(this.track_layer_id,    'line-color', '#FFFF50');
        window.map.setPaintProperty(this.places_layer_id, 'text-color', '#FFFFFF');
        window.map.setPaintProperty(this.places_layer_id, 'text-halo-color', '#FFFFFF');
        //window.map.setLayoutProperty(this.places_layer_id, 'icon-image', 'nc');
    },
    set_high_contrast: function() {

        window.map.setPaintProperty(this.track_layer_id,    'line-color', '#880ED4');
        window.map.setPaintProperty(this.places_layer_id, 'text-color', '#000000');
        window.map.setPaintProperty(this.places_layer_id, 'text-halo-color', '#000000');
        //window.map.setLayoutProperty(this.places_layer_id, 'icon-image', 'hc');
    },
    show_hide_places: function() {
        var vis = window.map.getLayoutProperty(this.places_layer_id, 'visibility');
        if (vis == 'none') {
            window.map.setLayoutProperty(this.places_layer_id, 'visibility', 'visible');
        }else {
            window.map.setLayoutProperty(this.places_layer_id, 'visibility', 'none');
        }
    },
    toogle_catastro: function(obj) {
        if (this.catastro_flag === null) {
            obj.classList.replace("map-catastro", "map-catastro-active");
            map.getCanvas().style.cursor = 'pointer';
            this.catastro_flag = obj
        } else {
            this.catastro_flag.classList.replace("map-catastro-active", "map-catastro");
            map.getCanvas().style.cursor = '';
            this.catastro_flag = null;
        }
        
    },
    check_catastro: function(lat, lng) {
  
        console.log("testing catastro as this:", lat, lng)

        $.ajax({
            url: '/utils/check_catastro',
            type: 'POST',
            //dataType: 'json',
            //data: JSON.stringify(postData),
            // contentType: 'application/json',
            data: { 'lat': lat, 
                    'lng': lng, 
                },
            beforeSend: function (data) {
                // no wait, ugly
                //$('#wait-spinning').css("visibility", "visible");
            },
            success: function (data) {
                if (data.error > 0) {
                    json_error("Error getting catastro_info", data.text)
                    return;
                }
                // use here the container to process the tracks and save them
                // console.log(data.tracks)
                //var block = document.getElementById('block-page')

                // no wait, ugly
                // $('#wait-spinning').css("visibility", "hidden");
                // set things here. for now, add a layer with some things 
                // to test.
                
                console.log(data.data.catastro)
                if (data.data.catastro.ccc == "DPU") {
                    // public domain, show alert, quit
                    json_error("Dominio Público (ccc=DPU)", "no poly for this region, sorry")
                    return
                }

                
                if (window.map.getLayer(mapManager.catastro_layer_id)) {
                    window.map.removeLayer(mapManager.catastro_layer_id)
                }

                if (window.map.getSource(mapManager.catastro_source_id)) {
                    window.map.removeSource(mapManager.catastro_source_id)
                }


                window.map.addSource(mapManager.catastro_source_id, data.gdata)
                // add things to catastro layer ??
                window.map.addLayer({
                    'id': mapManager.catastro_layer_id,
                    'type': 'fill',
                    'source': mapManager.catastro_source_id,
                    'layout': { },
                    'paint': {
                        'fill-color': [ 'get', 'style'],
                        'fill-opacity': 0.7
                    }
                });

                map.on('click', mapManager.catastro_layer_id, (e) => {
                    
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
                        console.log("features", e.features[0].properties)
                });
                // console.log(data.gdata)

            },
            fail: function (data) {
                //$('#wait-spinning').css("visibility", "hidden");
                json_error("Error getting catastro_info", data)
                //console.error(data);
            }
        });

        // do only one time
        this.toogle_catastro()
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
    mapManager.init_defaults(track)

    map.on('style.load', async () => {
        mapManager.update_terrain();
        mapManager.load_icons();
    });
   
    // main callback
    map.on('load', async () => {
    
        mapManager.load_icons()
        // var marker = 'marker-places-nc'
        // if (! map.getImage(marker)) {
        //     console.log(`reloading ${marker} /static/img/icons/${marker}.png`)
        //     const image = await map.loadImage(`/static/img/icons/${marker}.png`);
        //     map.addImage(marker, image.data);
        // }
        // marker = 'marker-places-hc'
        // if (! map.getImage(marker)) {
        //     console.log(`reloading ${marker} /static/img/icons/${marker}.png`)
        //     const image = await map.loadImage(`/static/img/icons/${marker}.png`);
        //     map.addImage(marker, image.data);
        // }


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

            //
            // WIP - Contour lines works fine
            // TODO: add buttons and manage this layer
            // properly. Too clutering for default.

            // map.addSource(mapManager.layer_prefix('contours-source'), {
            //     type: 'vector',
            //     url: `https://api.maptiler.com/tiles/contours/tiles.json?key=${MAPTILER_KEY}`
            // });
            // map.addLayer({
            //     'id': mapManager.layer_prefix('terrain-data-layer'),
            //     'type': 'line',
            //     'source': mapManager.layer_prefix('contours-source'),
            //     'source-layer': 'contour',
            //     'layout': {
            //         'line-join': 'round',
            //         'line-cap': 'round'
            //     },
            //     'paint': {
            //         'line-color': '#E0E040',
            //         'line-width': 1
            //     }
            // });

            // TODO: add buttons and manage this layer
            // BIG geoGSON file (80MB), work with caution also municipio and provincia.
            // removed for now.

            // map.addSource(mapManager.layer_prefix('state-limits-source'), {
            //     type: "geojson",
            //     //data: "/static/geojson/spain/georef-spain-municipio.geojson"
            //     data: "/static/geojson/spain/georef-spain-provincia.geojson"
            // });
            // map.addLayer({
            //     'id': mapManager.layer_prefix('state-limits-layer'),
            //     'source': mapManager.layer_prefix('state-limits-source'),
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
        
        //
        // load the GEOJSON for places layer.
        // 

        map.addSource(mapManager.places_source_id, {
            type: "geojson",
            data: "/places/as_geojson"
        });
        
        map.addLayer({
            'id': mapManager.places_layer_id,
            'source': mapManager.places_source_id,
            'type': 'symbol',
            'layout': {
                'visibility': 'none',
                'icon-allow-overlap': true,
                'text-allow-overlap': true,
                'icon-overlap': 'always',
                'text-overlap': 'always',
                'icon-image': ['get', 'icon'],
                'text-field': ['get', 'name'],
                'text-font': [
                    'Open Sans Semibold',
                    'Arial Unicode MS Bold'
                ],
                'text-offset': [0, 1.25],
                'text-anchor': 'top',
                'text-size': 12,
                'text-letter-spacing': 0.05,
                
            },
            'paint': {
                'text-color': '#FFFFFF',
                'text-halo-color': '#ffffff',
                'text-halo-width': 0.1
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

        // don't work. useful maybe for places then, lets see.
        // let features = map.getSource(mapManager.places_source_id)
        // features.getData().then( function(results) {
        //     for (const marker of results.features) {
        //         // Create a DOM element for each marker.
        //         const el = document.createElement('div');
        //         //const width = marker.properties.iconSize[0];
        //         //const height = marker.properties.iconSize[1];
        //         el.className = 'marker';
        //         el.style.backgroundImage = `url(http://localhost:5000/static/img/icons/wpt/0.png)`;
        //         el.style.width = `132px`;
        //         el.style.height = `132px`;
        //         el.style.backgroundSize = '100%';
        
        //         el.addEventListener('click', () => {
        //             window.alert(marker.properties.name);
        //         });
        
        //         // Add markers to the map.
        //         new maplibregl.Marker(el)
        //             .setLngLat(marker.geometry.coordinates)
        //             .addTo(map);
        //     }


        // });
    })



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
        mapManager.check_catastro(lat=e.lngLat.lat, lng=e.lngLat.lng)
        return 

        // console.log("XXX")
        // console.log(e)
        // console.log(e.lngLat)
        // console.log(e.point)

        // use a popup - not needed.
        // popup = new maplibregl.Popup({closeOnMove: true, closeOnClick: true, closeButton: true})
        //     .setLngLat(e.lngLat)
        //     .setHTML(`
        //         <h5>check catastro</h5>
        //         <div>
        //             <span>${e.lngLat.lat}, ${e.lngLat.lng}</span>
        //             <a href="#"  onclick="mapManager.check_catastro(lat=${e.lngLat.lat}, lng=${e.lngLat.lng})">Check it</a>
        //         </div>
        //     `)
        //     .addTo(map);
  
        return
        
    });

  
    // Change the cursor to a pointer when the mouse is over the places layer.
    map.on('mouseenter', mapManager.places_layer_id, () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    // Change it back to a pointer when it leaves.
    map.on('mouseleave', mapManager.places_layer_id, () => {
        map.getCanvas().style.cursor = '';
    });

 


    // don't delete this, please

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