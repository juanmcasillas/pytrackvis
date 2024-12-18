var mapManager = {
    prefix: 'pytrackvis_',         // used to mark our custom layers in the map
    is3D: false,
    terrain: false,
    track: null,
    terrain_source: null,
    marker: new maplibregl.Marker(),
    catastro_flag: null,
    catastro_ids: [],

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
        // not used // this.catastro_layer_id = this.layer_prefix('catastro-layer')
        this.catastro_line_layer_id = this.layer_prefix('catastro-line-layer')
        this.catastro_poly_layer_id = this.layer_prefix('catastro-poly-layer')
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
    toogle_catastro_point: function(obj) {
        if (this.catastro_flag === null) {
            obj.classList.replace("map-catastro-point", "map-catastro-point-active");
            map.getCanvas().style.cursor = 'pointer';
            this.catastro_flag = obj
        } else {
            this.catastro_flag.classList.replace("map-catastro-point-active", "map-catastro-point");
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
                data.features.forEach(element => {
      
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

    }
}
