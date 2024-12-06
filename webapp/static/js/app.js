//
// update the track rating, using a post to the web service declared.
//
function UpdateTrackRating(trackid, rating) {
    var postData = { 
            id: trackid,
            rating: rating
        }; console.log(postData);

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