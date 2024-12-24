// //////////////////////////////////////////////////////////////////////////
//
// configures and control the map (see map.js)
//
//
//
// //////////////////////////////////////////////////////////////////////////

var mapManager = {


    prefix: 'pytrackvis_',         // used to mark our custom layers in the map
    MAPTILER_KEY: null,

    track_color:         '#b1e016', // this should be the same that config.catastro['public_color']
    contour_lines_color: '#909040',
    states_lines_color:  '#9090AA',
    cities_lines_color:  '#A0A0FF',
    
    is3D: false,
    terrain: false,
    track: null,
    terrain_source: null,
    marker: new maplibregl.Marker(),
    catastro_flag: null,
    catastro_ids: [],
    contour_lines_loaded: false,
    state_limits_loaded: false,
    city_limits_loaded: false,
    // load some optional layers by defaut.
    load_terrain: true,
    load_hillshading: false,
    load_buildings: false,
    places_layers: [],
    places_layers_id: {},

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
        '80',
    ],

    /**
     * init the object and set the default variables.
     * @param {*} track 
     */
    init_defaults: function(track, MAPTILER_KEY, places_layers) {

        this.track = track
        this.MAPTILER_KEY = MAPTILER_KEY
        this.places_layers = places_layers
        this.marker.setLngLat([track.begin.long, track.begin.lat, track.begin.elev]).addTo(map);
        this.marker.setOpacity(0)
        
        // sources
        
        this.terrain_source_id             = this.layer_prefix("terrain-source")
        this.contours_source_id            = this.layer_prefix('contours-source')
        this.state_limits_source_id        = this.layer_prefix('state-limits-source')
        this.cities_limits_source_id       = this.layer_prefix('cities-limits-source')
        this.terrain_hillshading_source_id = this.layer_prefix("terrain_hs-source")
        this.places_source_id              = this.layer_prefix('places-source')
        this.buildings_source_id           = this.layer_prefix('openmaptiles-source')
        this.catastro_source_id            = this.layer_prefix('catastro-source')
        this.track_source_id               = this.layer_prefix(`track_${this.track.id}-source`)
        // layers
        this.contours_layer_id             = this.layer_prefix('terrain-data-layer')
        this.state_limits_layer_id         = this.layer_prefix('state-limits-layer')
        this.cities_limits_layer_id        = this.layer_prefix('cities-limits-layer')
        this.terrain_hillshading_layer_id  = this.layer_prefix('hillshading-layer')
        // this is overhaul by place_layers
        this.places_layer_id               = this.layer_prefix('places-layer')
        for (const pl of this.places_layers) {
              this.places_layers_id[pl] = this.layer_prefix(`places-layer-${pl}`)
        }
        
        this.buildings_layer_id            = this.layer_prefix('openmaptiles-layer')
        this.catastro_poly_layer_id        = this.layer_prefix('catastro-poly-layer')
        // not used  
        // this.catastro_line_layer_id     = this.layer_prefix('catastro-line-layer')
        this.track_layer_id                = this.layer_prefix(`track_${this.track.id}-layer`)


        this.terrain_source = { source: this.terrain_source_id }
        //debug 
        // console.log(this)
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

        // window.map.setPaintProperty(this.track_layer_id,  'line-color', '#FFFF50');
        window.map.setPaintProperty(this.places_layer_id, 'text-color', '#FFFFFF');
        window.map.setPaintProperty(this.places_layer_id, 'text-halo-color', '#FFFFFF');
        //window.map.setLayoutProperty(this.places_layer_id, 'icon-image', 'nc');
    },
    set_high_contrast: function() {

        // window.map.setPaintProperty(this.track_layer_id,    'line-color', '#880ED4');
        window.map.setPaintProperty(this.places_layer_id, 'text-color', '#000000');
        window.map.setPaintProperty(this.places_layer_id, 'text-halo-color', '#000000');
        //window.map.setLayoutProperty(this.places_layer_id, 'icon-image', 'hc');
    },
    // show_hide_places: function() {

    //     var vis = window.map.getLayoutProperty(this.places_layer_id, 'visibility');
    //     if (vis == 'none') {
    //         window.map.setLayoutProperty(this.places_layer_id, 'visibility', 'visible');
    //     }else {
    //         window.map.setLayoutProperty(this.places_layer_id, 'visibility', 'none');
    //     }
    // },

    show_hide_contour: function() {
        if (!this.contour_lines_loaded) {
            this.contour_lines_loaded = true;
            window.map.addSource(this.contours_source_id, {
                type: 'vector',
                url: `https://api.maptiler.com/tiles/contours/tiles.json?key=${this.MAPTILER_KEY}`
            });

            window.map.addLayer({
                'visibility': 'visible',
                'id': this.contours_layer_id,
                'type': 'line',
                'source': this.contours_source_id,
                'source-layer': 'contour',
                'layout': {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                'paint': {
                    'line-color': this.contour_lines_color,
                    'line-width': 1
                }
            });
            return
        }

        var vis = window.map.getLayoutProperty(this.contours_layer_id, 'visibility');
        if (vis == 'none') {
            window.map.setLayoutProperty(this.contours_layer_id, 'visibility', 'visible');
        }else {
            window.map.setLayoutProperty(this.contours_layer_id, 'visibility', 'none');
        }
    },
    show_hide_states: function() {
        if (!this.state_limits_loaded) {
            this.state_limits_loaded = true;
            window.map.addSource(mapManager.state_limits_source_id, {
                type: "geojson",
                data: "/static/geojson/spain/georef-spain-provincia.geojson"
            });
                

            map.addLayer({
                'id': mapManager.state_limits_layer_id,
                'source': mapManager.state_limits_source_id,
                'visibility': 'none',
                // 'type': 'line',
                // 'layout': { 
                //     'line-join': "round", 
                //     'line-cap': "round"
                // },
                // 'paint': {
                //     //'line-color': '#909090',    // high contrast
                //     'line-dasharray': [5,10],
                //     'line-color': this.states_lines_color,  // low contrast
                //     'line-width': 1
                // }
                'type': 'fill',
                'layout': { },
                'paint': {
                    'fill-color': [
                        "interpolate", ['linear'],  ["to-number", ["get", "prov_code"]], 1, '#101010', 54, '#E0E0E0'
                    ],
                    'fill-opacity': 0.3,
                    'fill-antialias': true,
                    'fill-outline-color': "#FFFFFF"
                },
            });
            return
        }

        var vis = window.map.getLayoutProperty(this.state_limits_layer_id, 'visibility');
        if (vis == 'none') {
            window.map.setLayoutProperty(this.state_limits_layer_id, 'visibility', 'visible');
        }else {
            window.map.setLayoutProperty(this.state_limits_layer_id, 'visibility', 'none');
        }
    },
    show_hide_cities: function() {
        if (!this.cities_limits_loaded) {
            this.cities_limits_loaded = true;
            window.map.addSource(mapManager.cities_limits_source_id, {
                type: "geojson",
                data: "/static/geojson/spain/georef-spain-municipio.geojson"
            });
            
            //prov_code 1-54
            //mun_code 1001-54005
            // 1-54
            // 

            map.addLayer({
                'id': mapManager.cities_limits_layer_id,
                'source': mapManager.cities_limits_source_id,
                'visibility': 'none',
                'type': 'line',
                'layout': { 
                    'line-join': "round", 
                    'line-cap': "round"
                },
                'paint': {
                    //'line-color': '#909090',    // high contrast
                    'line-dasharray': [5,10],
                    'line-color': this.cities_lines_color,  // low contrast
                    'line-width': 1
                }
                // 'type': 'fill',
                // 'layout': { },
                // 'paint': {
                //     'fill-color': [
                //         "interpolate", ["linear"], ["to-number", ["get", "mun_code"]], 1001, '#101010', 54005, '#E0E0E0'
                //     ],
                //     'fill-opacity': 1,
                //     'fill-antialias': true,
                //     'fill-outline-color': "#FFFFFF"
                // },
            });
            return
        }

        var vis = window.map.getLayoutProperty(this.cities_limits_layer_id, 'visibility');
        if (vis == 'none') {
            window.map.setLayoutProperty(this.cities_limits_layer_id, 'visibility', 'visible');
        }else {
            window.map.setLayoutProperty(this.cities_limits_layer_id, 'visibility', 'none');
        }
    },


    toogle_catastro_point: function(obj) {
        if (this.catastro_flag === null) {
            obj.classList.replace("map-button", "map-button-active");
            map.getCanvas().style.cursor = 'pointer';
            this.catastro_flag = obj
        } else {
            this.catastro_flag.classList.replace("map-button-active", "map-button");
            map.getCanvas().style.cursor = '';
            this.catastro_flag = null;
        }
        
    },
    check_catastro_point: function(lat, lng) {
  
        console.log("testing catastro as this:", lat, lng)

        $.ajax({
            url: '/utils/check_catastro_point',
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
                
                console.log(data)
                if (data.data.catastro.ccc == "DPU") {
                    // public domain, show alert, quit
                    json_error("Dominio Público (ccc=DPU)", "no poly for this region, sorry")
                    return
                }

                // don't delete the features, instead of this add them
                // geodiff = {
                //     "update" : data.gdata.data.features
                // }
                let add_container = []
                let update_container = []
                data.gdata.data.features.forEach(element => {
      
                    if (! mapManager.catastro_ids.includes(element.id)) {
                        mapManager.catastro_ids.push(element.id)
                        add_container.push(element)
                    }
                    else {
                        update_container.push(element)
                    }
                });
                let source = window.map.getSource(mapManager.catastro_source_id)
                source.updateData({ "add": add_container })
                source.updateData({ "update": update_container })

                // add element features to source layer.

                
                // console.log(data.gdata)

            },
            fail: function (data) {
                //$('#wait-spinning').css("visibility", "hidden");
                json_error("Error getting catastro_info", data)
                //console.error(data);
            }
        });

        // do only one time
        this.toogle_catastro_point()
    },
    
    check_catastro_track: function() { 
    
        $.ajax({
            url: '/utils/check_catastro_track',
            type: 'POST',
           
            data: { 
                'track_id': this.track.id 
            },
            beforeSend: function (data) {
                // no wait, ugly
                $('#wait-spinning').css("visibility", "visible");
            },
            success: function (data) {
                if (data.error > 0) {
                    json_error("Error getting catastro_info", data.text)
                    return;
                }
                $('#wait-spinning').css("visibility", "hidden");

                // console.log(data)
                let add_container = []
                let update_container = []
                let line_container = []
                
                data.features.forEach(element => {
                    if (element.geometry.type == "LineString") {
                        line_container.push(element)
                    }
                    else {
                        if (! mapManager.catastro_ids.includes(element.id)) {
                            mapManager.catastro_ids.push(element.id)
                            add_container.push(element)
                        }
                        else {
                            update_container.push(element)
                        }
                    }
                });
                
                let source = window.map.getSource(mapManager.catastro_source_id)
                source.updateData({ "add": add_container })
                source.updateData({ "update": update_container })

                source = window.map.getSource(mapManager.track_source_id)
                source.updateData({ "removeAll":true })
                source.updateData({ "add": line_container })
           

                // work now in the "track". Change the track source with our variables.

                // disable the "default track"
                // TODO FIX THIS
                // if (window.map.getLayer(mapManager.track_layer_id) !== 'undefined') {
                //     window.map.setLayoutProperty(mapManager.track_layer_id, 'visibility', 'none');
                // }
                // add element features to source layer.

                
                // console.log(data.gdata)

            },
            fail: function (data) {
                $('#wait-spinning').css("visibility", "hidden");
                json_error("Error getting catastro_info", data)
                //console.error(data);
            }
        });

    },


    filter_places: function(obj) { 


        if (obj.checked) {
            window.map.setLayoutProperty(this.places_layers_id[obj.value], 'visibility', 'visible');
        }else {
            window.map.setLayoutProperty(this.places_layers_id[obj.value], 'visibility', 'none');
        }
        // let track_data = map.getSource(mapManager.places_source_id)
        // places_source_id.getData().then( function(results) {
        //     //
        // });
    },

    configure_places: function() { 

        for (const pl of this.places_layers) {
            
            map.addLayer({
                'id': this.places_layers_id[pl],
                'source': this.places_source_id,
                'type': 'symbol',
                'filter': ['==', ['get', 'category'], pl],
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
                    'text-halo-color': '#606060',
                    'text-halo-width': 0.12
                }
            });
        }

        //let track_data = map.getSource(mapManager.places_source_id)
        //places_source_id.getData().then( function(results) {
        //    //
        //});
    },

    

}
