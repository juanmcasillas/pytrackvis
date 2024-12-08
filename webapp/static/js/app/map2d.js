function forEachLayer(map, text, cb) {
    map.getStyle().layers.forEach((layer) => {
      if (!layer.id.includes(text)) return;
        cb(layer);
    });
  }
  // Changing the map base style
function changeStyle(map, style) {
    const savedLayers = [];
    const savedSources = {};
    const layerGroups = [
    'line',
    ];

    layerGroups.forEach((layerGroup) => {
        forEachLayer(map, layerGroup, (layer) => {
            console.log(layer)
            savedSources[layer.source] = map.getSource(layer.source).serialize();
            savedLayers.push(layer);
        });
    });

    map.setStyle(style);

    setTimeout(() => {
    Object.entries(savedSources).forEach(([id, source]) => {
        map.addSource(id, source);
    });

    savedLayers.forEach((layer) => {
        map.addLayer(layer);
    });
    }, 1000);
  }

function draw_map_2D(track, MAPTILER_KEY, style_id) {


    const map = (window.map = new maplibregl.Map({
        container: 'map',
        //zoom: 14,
        //bearing: 0,
        //pitch: 0,
        hash: true,
        style: `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,
        //maxZoom: 18,
        antialias: true,
        maplibreLogo: true
    }));
    map.dragRotate.disable();
    map.keyboard.disable(); 
    map.touchZoomRotate.disableRotation();
    
    //https://gist.github.com/ryanbaumann/7f9a353d0a1ae898ce4e30f336200483/96bea34be408290c161589dcebe26e8ccfa132d7
    //https://github.com/maplibre/maplibre-gl-js/issues/2587
    var customLayers = [
        {
            source_id: `pytrackvis_track_${track.id}`,
            source: {
                type: "geojson",
                data: `/tracks/as_geojson?id=${track.id}`
            },
            layer: {
                'id': `pytrackvis_track_${track.id}_layer`,
                'type': 'line',
                'source': `pytrackvis_track_${track.id}`,
                'layout': { 
                    'line-join': "round", 
                    'line-cap': "round"
                },
                'paint': {
                    'line-color': '#FFFF50', 
                    'line-width': 4
                },
            }
        }
    ]

    map.on('load', () => {

        const layers = map.getStyle().layers;


        map.addControl(new maplibregl.FullscreenControl({container: document.querySelector('body')}),  'top-right');
        map.addControl(
            new maplibregl.NavigationControl({
                visualizePitch: false,
                showZoom: true,
                showCompass: true
            }, 
            'top-right')
        );
        map.addControl(new maplibregl.ScaleControl({ unit: 'metric'}), 'top-right');
        map.addControl(new maplibreGLMeasures.default({}), 'top-right');

        for (var i = 0; i < customLayers.length; i++) {
            var me = customLayers[i]
            map.addSource(me.source_id, me.source);
            map.addLayer(me.layer)
        }

        let labelLayerId;
        for (let i = 0; i < layers.length; i++) {
            if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
                labelLayerId = layers[i].id;
                break;
            }
        }
        
        map.setCenter({ lon: track.center.long, lat: track.center.lat })
        map.fitBounds( track.bounds )
        map.setPitch(0)


        // the map selector.
     
        
        document.getElementById(style_id).addEventListener("change", function (event) {
            const styleId = event.target.value
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
   

    })

    
    // this should be removable as we pass the data by parameter.
    // $.getJSON( "/tracks/get_track_info", { 'id': `${track.id}` } )
    //     .done(function( track_data ) {
    //         //console.log(track)

    //         map.setCenter({ lon: track_data.center.long, lat: track_data.center.lat })
    //         map.fitBounds( track_data.bounds )
    //         map.setPitch(0)
            
    //     })
    //     .fail(function( jqxhr, textStatus, error ) {
    //         // show the error here, please
    //         var err = textStatus + ", " + error;
    //         console.log( "Request Failed: " + err );
    //     });

      

}