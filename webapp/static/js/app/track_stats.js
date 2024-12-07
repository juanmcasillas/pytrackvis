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
                    slices: [ { color: '#ee8080' }, {color: '#ee6060'}, {color: '#ee4040'},  {color: '#ee2020'}, {color: '#ee0000'}, {color: '#dd2020'}, {color: '#cc2020'} ]
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
                    slices: [ { color: '#40cc40' }, {color: '#20bb20'}, {color: '#20aa20'},  {color: '#209920'}, {color: '#208820'}, {color: '#207720'}, {color: '#206620'} ]
                    };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('trackstats_downhill_range_distance'));
    chart.draw(data, options);

    // // time based series here.
    // var data = new google.visualization.DataTable();
    // data.addColumn('string', 'Slope');
    // data.addColumn('number', 'Time');

    // // 0-5, 5-10, 10-15, 15-20, 20-25, >30
    // data.addRow( [ "0.5% - 3% ", track.uphill_slope_range_time_0 ]);
    // data.addRow( [ "3%   - 5% ", track.uphill_slope_range_time_1 ]);
    // data.addRow( [ "5%   - 7% ", track.uphill_slope_range_time_2 ]);
    // data.addRow( [ "7%  - 10% ", track.uphill_slope_range_time_3 ]);
    // data.addRow( [ "10% - 14% ", track.uphill_slope_range_time_4 ]);
    // data.addRow( [ "14% - 20% ", track.uphill_slope_range_time_5 ]);
    // data.addRow( [ ">20% ",      track.uphill_slope_range_time_6 ]);

    // // Set chart options
    // var options = {title:'Uphill Slope Time Distribution (s)',
    //                 // titlePosition: 'center',
    //                 titleTextStyle: { fontSize: 12 },
    //                 chartArea: {left: 10, 'width': '100%', 'height': '82%' },
    //                 pieHole: 0.3,
    //                 legend: 'right',
    //                 //sliceVisibilityThreshold: .2,
    //                 slices: [ { color: '#ee8080' }, {color: '#ee6060'}, {color: '#ee4040'},  {color: '#ee2020'}, {color: '#ee0000'}, {color: '#dd2020'}, {color: '#cc2020'} ]
    //                  };

    // // Instantiate and draw our chart, passing in some options.
    // var chart = new google.visualization.PieChart(document.getElementById('trackstats_uphill_range_time'));
    // chart.draw(data, options);

    // var data = new google.visualization.DataTable();
    // data.addColumn('string', 'Slope');
    // data.addColumn('number', 'Time');

    // // 0-5, 5-10, 10-15, 15-20, 20-25, >30

    // data.addRow( [ "-3% - -0.5% ", track.downhill_slope_range_time_0] );
    // data.addRow( [ "-5%  -  -3% ", track.downhill_slope_range_time_1] );
    // data.addRow( [ "-7%  -  -5% ", track.downhill_slope_range_time_2] );
    // data.addRow( [ "-10% -  -7% ", track.downhill_slope_range_time_3] );
    // data.addRow( [ "-14% - -10% ", track.downhill_slope_range_time_4] );
    // data.addRow( [ "-20% - -14% ", track.downhill_slope_range_time_5] );
    // data.addRow( [ "<-20% ",       track.downhill_slope_range_time_6] );

    // // Set chart options
    // var options = {title:'Downhill Slope Time Distribution (s)',
    //                 // titlePosition: 'center',
    //                 titleTextStyle: { fontSize: 12 },
    //                 chartArea: {left: 10, 'width': '100%', 'height': '82%' },
    //                 pieHole: 0.3,
    //                 legend: 'right',
    //                 slices: [ { color: '#40cc40' }, {color: '#20bb20'}, {color: '#20aa20'},  {color: '#209920'}, {color: '#208820'}, {color: '#207720'}, {color: '#206620'} ]
    //                 };

    // // Instantiate and draw our chart, passing in some options.
    // var chart = new google.visualization.PieChart(document.getElementById('trackstats_downhill_range_time'));
    // chart.draw(data, options);
}