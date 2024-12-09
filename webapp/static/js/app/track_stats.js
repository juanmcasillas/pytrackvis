


function drawTrackStats(track) {

    //
    // draw the data based on TRACK information.
    // data is currently defined on the page.
    //


    var uphill_p_distance = track.uphill_p_distance 
    var level_p_distance = track.level_p_distance 
    var downhill_p_distance = track.downhill_p_distance 

    var uphill_p_time = track.uphill_p_time 
    var level_p_time =  track.level_p_time
    var downhill_p_time = track.downhill_p_time 

    // Create the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Label');
    data.addColumn('number', 'Distance (% Total)');

    data.addRow( [ "Uphill", uphill_p_distance ] );
    data.addRow( [ "Level",  level_p_distance ] );
    data.addRow( [ "Downhill", downhill_p_distance ] );

    // Set chart options
    var options = {title:'% Distance',
                    // titlePosition: 'center',
                    width: '100%',
                    titleTextStyle: { fontSize: 12 },
                    chartArea: {left: 10, 'width': '100%', 'height': '82%' },
                    pieHole: 0.3,
                    legend: 'right',
                    slices: [ { color: 'red' }, {color: 'blue'}, {color: '#009933'} ]
                     };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('trackstats_distance'));
    chart.draw(data, options);

    // Create the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Label');
    data.addColumn('number', 'Time (% Total)');

    data.addRow( [ "Uphill", uphill_p_time ] );
    data.addRow( [ "Level",  level_p_time ] );
    data.addRow( [ "Downhill", downhill_p_time ] );

    // Set chart options
    var options = {title:'% Time',
                    //titlePosition: 'center',
                    titleTextStyle: { fontSize: 12 },
                    chartArea: {left: 10, 'width': '100%', 'height': '82%' },
                    pieHole: 0.3,
                    legend: 'right',
                    slices: [ { color: 'red' }, {color: 'blue'}, {color: '#009933'} ]
                     };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('trackstats_time'));
    chart.draw(data, options);

    //
    // create graphics for slopes.
    //
    
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Slope');
    data.addColumn('number', 'Distance');

    // 0-5, 5-10, 10-15, 15-20, 20-25, >30
    data.addRow( [ "0.5% - 3% ", track.uphill_slope_range_distance_0 ]);
    data.addRow( [ "3%   - 5% ", track.uphill_slope_range_distance_1 ]);
    data.addRow( [ "5%   - 7% ", track.uphill_slope_range_distance_2 ]);
    data.addRow( [ "7%  - 10% ", track.uphill_slope_range_distance_3 ]);
    data.addRow( [ "10% - 14% ", track.uphill_slope_range_distance_4 ]);
    data.addRow( [ "14% - 20% ", track.uphill_slope_range_distance_5 ]);
    data.addRow( [ ">20% ",      track.uphill_slope_range_distance_6 ]);

    // Set chart options
    var options = {title:'Uphill Slope Distance Distribution (m)',
                    // titlePosition: 'center',
                    titleTextStyle: { fontSize: 12 },
                    chartArea: {left: 10, 'width': '100%', 'height': '82%' },
                    pieHole: 0.3,
                    legend: 'right',
                    //sliceVisibilityThreshold: .2,
                    slices: [ { color: '#dd7070' }, {color: '#dd5050'}, {color: '#dd3030'},  {color: '#dd1010'}, {color: '#dd0000'}, {color: '#cc1010'}, {color: '#bb1010'} ]
                     };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('trackstats_uphill_range_distance'));
    chart.draw(data, options);

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Slope');
    data.addColumn('number', 'Distance');

    // 0-5, 5-10, 10-15, 15-20, 20-25, >30

    data.addRow( [ "-3% - -0.5% ", track.downhill_slope_range_distance_0] );
    data.addRow( [ "-5%  -  -3% ", track.downhill_slope_range_distance_1] );
    data.addRow( [ "-7%  -  -5% ", track.downhill_slope_range_distance_2] );
    data.addRow( [ "-10% -  -7% ", track.downhill_slope_range_distance_3] );
    data.addRow( [ "-14% - -10% ", track.downhill_slope_range_distance_4] );
    data.addRow( [ "-20% - -14% ", track.downhill_slope_range_distance_5] );
    data.addRow( [ "<-20% ",       track.downhill_slope_range_distance_6] );

    // Set chart options
    var options = {title:'Downhill Slope Distance Distribution (m)',
                    // titlePosition: 'center',
                    titleTextStyle: { fontSize: 12 },
                    chartArea: {left: 10, 'width': '100%', 'height': '82%' },
                    pieHole: 0.3,
                    legend: 'right',
                    slices: [ { color: '#20ac20' }, {color: '#109910'}, {color: '#109910'},  {color: '#108810'}, {color: '#107710'}, {color: '#106610'}, {color: '#105510'} ]
                    };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('trackstats_downhill_range_distance'));
    chart.draw(data, options);

 
}

function gradeslope(distance, elevation) {
    
    if (distance == 0.0 || elevation == 0.0) {
        return 0.0
    }
    
    r = Math.pow(distance, 2) - Math.pow(elevation, 2)

    d = distance    
    if (r > 0.0) {
        d = Math.sqrt( r )
    }

    s = (elevation / d) * 100.0             // projected distance (horizontal)
    s = (elevation / distance) * 100.0      // aproximation
    
    return s
}


function plotElevation(data,map,mapManager) {

    // array of (lon, lat, elev)
    // console.log(data.geometry.coordinates)
    
    //elevations = results;
    results = []
    positions = [];
    chart_data_elevation = new google.visualization.DataTable();

    chart_series = {}
  
    for (serie in data.properties.series) {
        chart_series[serie] = new Object()
        chart_series[serie].data = {}
        chart_series[serie].chart = {}
        chart_series[serie].options = {}
        
        chart_series[serie].max = Math.max(...data.properties.series[serie])
        chart_series[serie].min = Math.min(...data.properties.series[serie])
        chart_series[serie].data = new google.visualization.DataTable();
        chart_series[serie].data.addColumn('number', serie);
        chart_series[serie].data.addColumn('number', ''); // bars
        chart_series[serie].data.addColumn('number', ''); // lines
        chart_series[serie].data.addColumn({type: 'string', role: 'tooltip', 'p': {'html': true}});
        chart_series[serie].data.addColumn({type: 'string', role: 'style' });

        chart_series[serie].rainbow = new Rainbow();
        chart_series[serie].rainbow.setSpectrum('#030057','#0300B7','#0095B8', '#00D0A0', '#79E600','#D83000', '#582010');
        chart_series[serie].rainbow.setNumberRange(chart_series[serie].min, chart_series[serie].max);
    }
  
    // elevation goes alone
    chart_data_elevation.addColumn('number', 'Distance');
    chart_data_elevation.addColumn('number', ''); // bars
    chart_data_elevation.addColumn('number', ''); // lines
   
    chart_data_elevation.addColumn({type: 'string', role: 'tooltip', 'p': {'html': true}});
    chart_data_elevation.addColumn({type: 'string', role: 'style' });

    var rainbow = new Rainbow(); // for colors
    rainbow.setSpectrum('#030057','#0300B7','#0095B8', '#00D0A0', '#79E600','#D83000', '#582010');
    rainbow.setNumberRange(-20, 20); 
    
    // create heatmap
    // var heatmap =document.getElementById('heatmap');
    // var content = "";
    // for (var i=-20; i<= 20; i++) {
    //     content += "<span style='background-color: #" + rainbow.colourAt(i) + "'>"+i+"</span>";
    // } 
    // heatmap.innerHTML = content;

    
    var dist = 0.0;
    var dindex = 0;
    
    // have the data of the series
    // data.properties.series
    //   "heart_rate":  [],
    //   "power":       [],
    //   "cadence":     [],
    //   "temperature": []
    
    for (var i = 0; i < data.geometry.coordinates.length; i++) {

        var ddelta = 0.0;
        var elevation = 0.0;
        var slope_avg = 0.0;

        x_long = x_lat = x_elev = 0.0
        y_long = y_lat = y_elev = 0.0

        if (i>0) {
            //x_long = data.geometry.coordinates[i][0]
            //x_lat = data.geometry.coordinates[i][1]
            x_elev = data.geometry.coordinates[i][2]

            //y_long = data.geometry.coordinates[i-1][0]
            //y_lat = data.geometry.coordinates[i-1][1]
            y_elev = data.geometry.coordinates[i-1][2]

            //var PA = new maplibregl.Marker().setLngLat([x_long, x_lat, x_elev]); 
            //var PB = new maplibregl.Marker().setLngLat([y_long, y_lat, y_elev]); 
            // elevation = x_elev - y_elev;
            // slope_avg = (elevation == 0 ? 0 : ddelta / elevation)
            var PA = new maplibregl.Marker().setLngLat(data.geometry.coordinates[i]); 
            var PB = new maplibregl.Marker().setLngLat(data.geometry.coordinates[i-1]); 
            
            elevation = x_elev - y_elev;
            ddelta = PA.getLngLat().distanceTo(PB.getLngLat())
            slope_avg = gradeslope(ddelta, elevation)
        }
        
        dist += ddelta; 
        
        var legend = "Distance: "+(dist /1000.0).toFixed(2)+ " Km\n";
        legend += "Elevation: "+ x_elev.toFixed(2)+ " m\n";
        legend += "Slope: "+ slope_avg.toFixed(2)+ " %\n";
        
        var color = rainbow.colourAt(slope_avg);
        
        // instead of dist, add i to ensure tigh bars (no spaces)
        
        if (ddelta > 0.3) {
            chart_data_elevation.addRow([ dindex, x_elev, x_elev  ,legend, "color: "+ color ]);
            pos = PA.getLngLat()
            positions.push([pos.lng, pos.lat, x_elev]);
            dindex++;

            // add the series here.
            for (serie in data.properties.series) {
                val = data.properties.series[serie][i]
                var serie_legend = "Distance: "+(dist /1000.0).toFixed(2)+ " Km\n";
                serie_legend += `${serie}: `+ val.toFixed(2)+ "\n";
                color = chart_series[serie].rainbow.colourAt(val);
                chart_series[serie].data.addRow([ dindex, val, val  ,serie_legend, "color: "+ color ]);
            }
        }
        
    }

    //document.getElementById('elevation_chart').style.display = 'block';
    chart = new google.visualization.ComboChart(document.getElementById('elevation_chart'));
    //chart = new google.visualization.ColumnChart(document.getElementById('elevation_chart'));
    chart_options = {
        //tooltip: { trigger: 'selection' },
        // LINE OPTIONS

        //width: 300,
        //height: 150,
        legend: 'none',

        tooltip: { textStyle: { fontSize: 10 } },
        //legend: {'position': 'bottom'},
        titleY: 'Elevation (m)',
        titleX: 'Distance (Km)',
        seriesType: 'bars',
        series: {1: {type: 'bars'}, 0: {type: 'line'}},
        
        focusBorderColor: '#00ff00',
        bar: {groupWidth: '100%' },
        explorer: { actions: ['dragToZoom', 'rightClickToReset'] , 
                    axis: 'horizontal',
                        keepInBounds: true,
                        maxZoomOut:1,
                },
        focusTarget: 'category',
        // colors: [ '#00aa00', '#aa0000' ],
        // max with text chartArea: {'width': '95%', 'height': '73%', 'align': 'center' }
        // use 100% in height for ColumnChart, if desired (better line)
        chartArea: {'width': '100%', 'height': '90%' }
    }

    chart.draw(chart_data_elevation, chart_options);
    
    for (serie in data.properties.series) {

        chart_series[serie].chart = new google.visualization.ComboChart(document.getElementById(`${serie}_chart`));
        chart_series[serie].options = {
            legend: 'none',
            tooltip: { textStyle: { fontSize: 10 } },
            titleY: serie,
            titleX: 'Distance (Km)',
            seriesType: 'bars',
            series: {1: {type: 'bars'}, 0: {type: 'line'}},
            
            focusBorderColor: '#00ff00',
            bar: {groupWidth: '100%' },
            explorer: { actions: ['dragToZoom', 'rightClickToReset'] , 
                        axis: 'horizontal',
                            keepInBounds: true,
                            maxZoomOut:1,
                    },
            focusTarget: 'category',
            chartArea: {'width': '100%', 'height': '90%' }
        }

        chart_series[serie].chart.draw(chart_series[serie].data, chart_series[serie].options);
    }
    
    window.onresize = function(){
        if (document.getElementById("elevation_chart") != null) {
            var container = document.getElementById("elevation_chart").firstChild.firstChild;
            container.style.width = "100%";
            chart.draw(chart_data_elevation, chart_options);
        }
        for (serie in data.properties.series) {
            if (document.getElementById(`${serie}_chart`) != null) {
                var container = document.getElementById(`${serie}_chart`).firstChild.firstChild;
                container.style.width = "100%";
                chart_series[serie].chart.draw(chart_series[serie].data, chart_series[serie].options);
            }
        }
    };

    // the tabs
    
    if (document.getElementById(`elevation-button-id`) != null) {
        tabEl = document.getElementById(`elevation-button-id`)

        tabEl.addEventListener('shown.bs.tab', function (event) {
            event.target // newly activated tab
            event.relatedTarget // previous active tab
            $(window).trigger('resize');
        })
    }

    for (serie in data.properties.series) {
        if (document.getElementById(`${serie}-button-id`) != null) {
            tabEl = document.getElementById(`${serie}-button-id`)
            tabEl.addEventListener('shown.bs.tab', function (event) {
                event.target // newly activated tab
                event.relatedTarget // previous active tab
                $(window).trigger('resize');
            })
        }
    }
   

    google.visualization.events.addListener(chart, 'onmouseover', function(e) {
        mapManager.marker_on()
        var point = positions[e.row]
        mapManager.marker.setLngLat(point)
        map.setCenter(point);
      });

    for (serie in data.properties.series) {
        google.visualization.events.addListener(chart_series[serie].chart, 'onmouseover', function(e) {
            mapManager.marker_on()
            var point = positions[e.row]
            mapManager.marker.setLngLat(point)
            map.setCenter(point);
        });
    }
}

