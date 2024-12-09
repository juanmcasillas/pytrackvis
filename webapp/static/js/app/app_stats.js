stats = null;

function drawAppStats() {


     // Load the Visualization API and the corechart package.
     google.charts.load('current', {'packages':['corechart', 'bar']});
    
     // Set a callback to run when the Google Visualization API is loaded.
     google.charts.setOnLoadCallback(drawChart);

     function drawChart() {

        /*
             s['by_kind'] = []
        for row in self.conn.execute("select sum(elevation),sum(distance),count(*),kind from tracks group by kind"):
            d = {}
            d['elevation'] = row[0]
            d['distance'] = row[1]
            d['number'] = row[2]
            d['kind'] = row[3]
            s['by_kind'].append(d)
         */
                    
        // Create the data table.
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Distance (Km)');
        
        for (var i=0; i< stats.by_kind.length; i++) {
            var item = stats.by_kind[i];
            data.addRow( [ item.kind, parseFloat(item.length_2d)/1000.0 ] );
        }
        
        var total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
        
        // Set chart options
        var options = {title:'Distance ('+total.getValue(0, 1).toFixed(2)+' Km)', 
        
                        titleTextStyle: { fontSize: 16 },
                        chartArea: {'width': '80%', 'height': '80%' }, 
                        pieHole: 0.4,
                        legend: 'bottom'
                         };

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.PieChart(document.getElementById('distance_by_kind_chart_div'));
        chart.draw(data, options);
        
        // another one
        
        data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Elevation (Km)');
        
        for (var i=0; i< stats.by_kind.length; i++) {
            var item = stats.by_kind[i];
            data.addRow( [ item.kind, parseFloat(item.uphill_climb)/1000.0 ] );
        }
        
        // Set chart options
        total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
        
        options.title = 'Elevation ('+(total.getValue(0, 1)*1000).toFixed(2)+' m)'

        // Instantiate and draw our chart, passing in some options.
        chart = new google.visualization.PieChart(document.getElementById('elevation_by_kind_chart_div'));
        chart.draw(data, options);
                
        // the last one for de demo
        
        data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Number of Tracks');
        
        for (var i=0; i< stats.by_kind.length; i++) {
            var item = stats.by_kind[i];
            data.addRow( [ item.kind, parseFloat(item.number) ] );
        }

        
        // Set chart options
        total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);        
 
        options.title = 'Number of tracks ('+total.getValue(0, 1).toFixed(0)+')'
                
        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.PieChart(document.getElementById('number_by_kind_chart_div'));
        chart.draw(data, options);
        
        //////////////////////////////////////////////////////////////////////
        // by equipment
        //////////////////////////////////////////////////////////////////////
        
        data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Distance (Km)');
        
        for (var i=0; i< stats.by_equipment.length; i++) {
            var item = stats.by_equipment[i];
            data.addRow( [ item.equipment, parseFloat(item.length_2d)/1000.0 ] );
        }
        
        // Set chart options
        
        var total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
        
        // Set chart options
        options.title = 'Distance ('+total.getValue(0, 1).toFixed(2)+' Km)'; 

        
        
        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.PieChart(document.getElementById('distance_by_equipment_chart_div'));
        chart.draw(data, options);
        
        // another one
        
        data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Elevation (Km)');
        
        for (var i=0; i< stats.by_equipment.length; i++) {
            var item = stats.by_equipment[i];
            data.addRow( [ item.equipment, parseFloat(item.uphill_climb)/1000.0 ] );
        }
        
        // Set chart options
        total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
        
        options.title = 'Elevation ('+(total.getValue(0, 1)*1000).toFixed(2)+' m)'

        // Instantiate and draw our chart, passing in some options.
        chart = new google.visualization.PieChart(document.getElementById('elevation_by_equipment_chart_div'));
        chart.draw(data, options);
                
        // the last one for de demo
        
        data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Number of Tracks');
        
        for (var i=0; i< stats.by_equipment.length; i++) {
            var item = stats.by_equipment[i];
            data.addRow( [ item.equipment, parseFloat(item.number) ] );
        }
        
        // Set chart options
        total = google.visualization.data.group(data, 
                            [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                            [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);     
                                    
         options.title = 'Number of tracks ('+total.getValue(0, 1).toFixed(0)+')'
                
        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.PieChart(document.getElementById('number_by_equipment_chart_div'));
        chart.draw(data, options);
 
         // draw year tendencies.   

        var parentdiv = document.getElementById('year_tendency_chart_div');

        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Year');
        data.addColumn('number', 'Elevation (Km)');
        data.addColumn('number', 'Distance (Km)');
        data.addColumn('number', 'Activities');
    
        for (var i=0; i< stats.years.length; i++) {
            // get the values for this year (equipment)
            var item = stats.years[i];
            data.addRow( [ item.year, parseFloat(item.uphill_climb)/1000.0, parseFloat(item.length_2d)/1000.0, parseInt(item.number) ] );
        }
        
        var options = {
                        title: 'Year info', 
                        titleTextStyle: { fontSize: 16 },
                        chartArea: {'width': '80%', 'height': '80%' }, 
                        legend: 'bottom',
                          series: {
                            0: { axis: 'Distance (Km)' }, 
                            1: { axis: 'Elevation (Km)' } // Bind series 1 to an axis named 'brightness'.
                          },
                          axes: {
                            y: {
                              Distance: {label: 'Distance'}, // Left y-axis.
                              Elevation: {side: 'right', label: 'Elevation'} // Right y-axis.
                            }
                          },
                        vAxis: { format: 'decimal' },
                        hAxis: { format: 'decimal' }
                     };
        
        var formatter = new google.visualization.NumberFormat({ fractionDigits: 2, prefix: ''});

        formatter.format(data, 1); // Apply formatter to second column.
        formatter.format(data, 2); // Apply formatter to second column.
       
        
        var newdiv = document.createElement('div');
        newdiv.setAttribute('class','appstats_item_big')
        parentdiv.append(newdiv);
        var newchart = new google.charts.Bar(newdiv);
        newchart.draw(data, options);
        window.onresize = function(){
            if (document.getElementById("year_tendency_chart_div") != null) {
                var container = document.getElementById("year_tendency_chart_div").firstChild.firstChild;
                container.style.width = "100%";
                newchart.draw(data, options);
            }
        };
        
      
        // load the filtered boxes
        draw_by_year(null);
      }     
}


function draw_by_year(year) {

    // populate the combos
    
    if (year == null) {
        var year_c = document.getElementById('comboelevation');
        $('#comboelevation').empty();
        
        var opt = document.createElement('option');
        opt.value = 'all';
        opt.innerHTML = "all";
        year_c.appendChild(opt);
        
        for (var i=0; i< stats.years.length; i++) {
            // get the values for this year (equipment)
            var item = stats.years[i];
        
            var opt = document.createElement('option');
            opt.value = item.year;
            opt.innerHTML = item.year;
            year_c.appendChild(opt);
        
        }
    }
    draw_elevation_by_year(year);
    draw_distance_by_year(year);
    

}      

function draw_elevation_by_year(year) {


    var localyear = year;
    if (year != null) {

    localyear =  (year.value == 'all' ? null : year.value);
    }


    var parentdiv = document.getElementById('elevation_by_sport_by_year_container_div');
    $("#elevation_by_sport_by_year_container_div").empty();

    // if null, use the collection with all the data: by_equipment
    // else, use the other.      
    

    var item_collection = stats.by_equipment
    if (localyear !== null) {
            item_collection =  stats.by_equipment_and_year[localyear];
    }
        
    
    
    for (var kind in stats.kinds) {

        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Elevation (Km)');
        
        for (var i=0; i< item_collection.length; i++) {
            var item = item_collection[i];
            
            if (item.kind == stats.kinds[kind] && (localyear == null || item.year == localyear)) {
                data.addRow( [ item.equipment, parseFloat(item.uphill_climb)/1000.0 ] );
            }
        }
    
            // kind has the type of sport.

        total = google.visualization.data.group(data, 
                        [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                        [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
        
            // Set chart options
        
        
        if (data.getNumberOfRows() > 0) {
        
            var options = { 
                    titleTextStyle: { fontSize: 16 },
                    chartArea: {'width': '80%', 'height': '80%' }, 
                    pieHole: 0.4,
                    legend: 'bottom'
                    };
            options.title = stats.kinds[kind] + ' ('+(total.getValue(0, 1)*1000).toFixed(2)+' m)'
        
            var newdiv = document.createElement('div');
            newdiv.setAttribute('class','appstats_item')
            parentdiv.append(newdiv);
            var newchart = new google.visualization.PieChart(newdiv);
            newchart.draw(data, options);
            
        }                
    }            

}

function draw_distance_by_year(year) {

    var localyear = year;
    if (year != null) {
        localyear =  (year.value == 'all' ? null : year.value);
    }
    
    var parentdiv = document.getElementById('distance_by_sport_by_year_container_div');
    $("#distance_by_sport_by_year_container_div").empty();
    // if null, use the collection with all the data: by_equipment
    // else, use the other.      

    var item_collection = stats.by_equipment
    if (localyear != null) {
            item_collection =  stats.by_equipment_and_year[localyear];
    }
    
    for (var kind in stats.kinds) {
    
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Sport');
        data.addColumn('number', 'Distance (Km)');
        
        for (var i=0; i< item_collection.length; i++) {
            var item = item_collection[i];
            
            if (item.kind == stats.kinds[kind] && (localyear == null || item.year == localyear)) {
                data.addRow( [ item.equipment, parseFloat(item.length_2d)/1000.0 ] );
            }
        }
    
            // kind has the type of sport.

        total = google.visualization.data.group(data, 
                        [{ type: 'boolean', column: 0, modifier: function () {return true;}}], 
                        [{ type: 'number',  column: 1, aggregation: google.visualization.data.sum }]);
    
            // Set chart options
        
        
        if (data.getNumberOfRows() > 0) {
        
            var options = { 
                    titleTextStyle: { fontSize: 16 },
                    chartArea: {'width': '80%', 'height': '80%' }, 
                    pieHole: 0.4,
                    legend: 'bottom'
                    };
            options.title = stats.kinds[kind] + ' ('+(total.getValue(0, 1)).toFixed(2)+' Km)'

            var newdiv = document.createElement('div');
            newdiv.setAttribute('class','appstats_item')
            parentdiv.append(newdiv);
            var newchart = new google.visualization.PieChart(newdiv);
            newchart.draw(data, options);

            
        }
    }
}

