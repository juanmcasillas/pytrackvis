function generate_uuid() {
    return Math.random().toString(36).substring(2, 15) +
        Math.random().toString(36).substring(2, 15);
}

//
// update the track rating, using a post to the web service declared.
//
function UpdateTrackRating(trackid, rating) {
    var postData = { 
            id: trackid,
            rating: rating
        }; 

        // see @web_impl.route('/track/edit/rating', methods=['POST'])
    $.ajax({
        url: '/track/edit/rating',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(postData),
        contentType: 'application/json',
        success: function (data) {
            // pass
        },
        fail: function (data) {
            console.error(data);
        }
    });
}

function configure_nunjucks() {
    // https://mozilla.github.io/nunjucks/templating.html
    const env = nunjucks.configure( '/static/views', { autoescape: true });
    env.addFilter('format_float', function(fmt,value) {
        return value.toFixed(2)
    })
    env.addFilter('humandistance', function(distance) {
        if (distance >= 1000.0) {
            var d = parseFloat(distance) / 1000.0
            s =  `${d.toFixed(2)} Km`

            return(s)
        }
        return `${distance.toFixed(2)} m`
    })
    env.addFilter('duration_format', function(stamp,fmt) {
        // see https://momentjs.com/
        if (stamp === undefined) {
            return "--:--:--"
        }
        //fmt = (fmt !== undefined ? fmt :  "DD/MM/YYYY HH:mm:ss")
        fmt = (fmt !== undefined ? fmt : "HH:mm:ss")
        duration = moment.duration(stamp, 'seconds')
        r = moment.utc(duration.as('milliseconds')).format(fmt)
        return r
    })

    env.addFilter('strftimestamp', function(stamp,fmt) {
        // see https://momentjs.com/
        if (stamp === undefined) {
            return "--:--:--"
        }
        fmt = (fmt !== undefined ? fmt : "DD/MM/YYYY HH:mm:ss")
        r = moment.unix(stamp).format(fmt)
        //console.log(fmt, r, stamp)
        return r
    })
    
    env.addFilter('as_thumb', function(url) {
        // see https://momentjs.com/
        var data = url.split('.')
        fname = data[0]
        extension = data[1]
        return `${fname}_tb.${extension}`

    })

}

function show_big(title,map_img, elev_img) {
    Swal.fire({
    title: `<h2>${title}</h2>`,
    width: '800px',
    html: `
    <div class="" role="alert">
        <div class="w-100">
            <img src="${map_img}" class="img-fluid w-100" ></img>
            <img src="${elev_img}" class="pt-1 img-fluid w-100" ></img>
        </div>
    </div>
    `,
    showCloseButton: false,
    confirmButtonText: 'Close',
    })
}

function json_error(title,message) {
    Swal.fire({
        title: `<h2>${title}</h2>`,
        width: '800px',
        html: `
        <div class="" role="alert">
            <div class="w-80">
                <p>${message}</p>
            </div>
        </div>
        `,
        showCloseButton: false,
        confirmButtonText: 'Close',
        }).then((result) => {
            if (result['isConfirmed']){
                $('#wait-spinning').css("visibility", "hidden");
                $('#search-field').val("")
            }
          })
}

function load_tracks(query, offset=0, limit=0) {
        
    if (query === undefined || query === '') {
        // console.log("using default query")
        query = null
        
    }
    
    //console.log(postData)
        // see @web_impl.route('/tracks/query', methods=['POST'])
    
    $.ajax({
        url: '/tracks/query',
        type: 'POST',
        //dataType: 'json',
        //data: JSON.stringify(postData),
        // contentType: 'application/json',
        data: { 'query': query, 
                'offset': offset, 
                'limit': limit 
            },
        beforeSend: function (data) {
            $('#wait-spinning').css("visibility", "visible");
        },
        success: function (data) {
            if (data.error > 0) {
                json_error("Error getting tracks", data.text)
                return;
            }
            // use here the container to process the tracks and save them
            // console.log(data.tracks)
            //var block = document.getElementById('block-page')
            $('#wait-spinning').css("visibility", "hidden");
            $('#block-page').empty()
            var total_msg = `${data.tracks.length}`
            if (data.total_size != data.tracks.length) {
                total_msg = `${data.tracks.length}/${data.total_size}`
            }
            var msg_s = ''
            msg_s = (data.tracks.length > 1 ? 's': '')

            $('#track-counter').html(`${total_msg} track${msg_s} found`)
            var page = nunjucks.render('track.html', { tracks: data.tracks, pagination: data.pagination, query: data.query })
            $('#block-page').html(page);
        },
        fail: function (data) {
            $('#wait-spinning').css("visibility", "hidden");
            json_error("Error getting tracks", data)
            //console.error(data);
        }
    });
}

// do this globally
configure_nunjucks();
$(function () {
    $('[data-toggle="tooltip"]').tooltip({
        delay: { "show": 500, "hide": 50 }
    })
})