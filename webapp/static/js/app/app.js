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