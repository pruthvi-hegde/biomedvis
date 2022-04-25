$(document).on('click', ".custom-info", function () {

    var _vm = $(this);
    var _index = _vm.attr('data-index');
    var _articleTitle = $(".article-title-" + _index).val();
    var _articleThumbnail = $(".article-thumbnail-" + _index).val()
    var _articleAuthors = $(".article-authors-" + _index).val()
    var _articleISSN = $(".article-ISSN-" + _index).val()
    var _articleISBN = $(".article-ISBN-" + _index).val()
    var _articleDOI = $(".article-DOI-" + _index).val()
    var _articleYear = $(".article-publishedDate-" + _index).val()
    var _abstract = $(".article-abstract-" + _index).val()

    $("#name").val(name);
    $("#exampleModalLongTitle").text(_articleTitle)
    $("#articleThumbnail").attr('src', _articleThumbnail)
    $("#articleAuthors").text(_articleAuthors)

    $("#articleYear").text(_articleYear)
    $("#articleDOI").attr('href', _articleDOI)
    $("#articleDOI").text(_articleDOI)
    $("#abstract").text(_abstract)


    $("#articleDetailsModal").modal("show");

})

//Common document ready function.
$(document).ready(function () {

    const user_input = $("#searchArticle")
    // const search_icon = $('#search-icon')
    const articles_div = $('#filteredArticles')
    const endpoint = '/articles-search'
    const delay_by_in_ms = 700
    let scheduled_function = false

    let ajax_call = function (endpoint, request_parameters) {
        $.getJSON(endpoint, request_parameters)
            .done(response => {
                // fade out the artists_div, then:

                articles_div.animate('fast',0).promise().then(() => {
                    // replace the HTML contents
                    articles_div.html(response['html_from_view'])
                    // fade-in the div with new contents
                    articles_div.animate('fast', 1)
                    // stop animating search icon
                    // search_icon.removeClass('blink')

                })
            })
    }


    user_input.on('keyup', function () {
        const request_parameters = {
            q: $(this).val() // value of user_input: the HTML element with ID user-input
        }

        if (scheduled_function) {
            clearTimeout(scheduled_function)
        }

        scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
    })

    $(".filter-checkbox").on('click', function () {
        var _filterObj = {};
        $(".filter-checkbox").each(function () {
            var _filterVal = $(this).val();
            var _filterKey = $(this).data('filter')

            _filterObj[_filterKey] = Array.from(document.querySelectorAll('input[data-filter=' + _filterKey + ']:checked')).map(function (el) {
                return el.value;
            });
        });


        // Run Ajaxl
        $.ajax({
            url: '/filter-data', data: _filterObj, dataType: 'json', beforeSend: function () {
            }, success: function (res) {
                $("#filteredArticles").html(res.data);
                var embeddingViewData = $('#articleEmbeddingView').data('article')
                embeddingView(embeddingViewData);
            }
        });
    })

    // // This is for toggle view
    var embeddingViewData = $('#articleEmbeddingView').data('article')
    embeddingView(embeddingViewData);

    // This is for time filter.

    const ctx = $('#chartContainer');
    const _filterdate = ctx.data('date')
    const _filtercount = ctx.data('count')
    // To toggle between article and embedding view.

    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: _filterdate,
            datasets: [{
                label: '# of Articles',
                data: _filtercount,
                backgroundColor: "#1C2862",
                borderColor: [],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });


})

function embeddingView(data) {
    // Run Ajaxl
    var jsonText = JSON.stringify(data);
    $.ajax({
        url: '/embedding-view',
        type: 'POST',
        data: jsonText,
        traditional: true,
        dataType: 'json',
        success: function (res) {
            $('#myDiv').html(res.data);
        },
        error: function (xhr, status, error) {
            console.log("inside Error " + error);
        }
    });


}

//Update article view after lasso or box select
$(document).on('plotly_selected', "#myDiv", function (arg1, arg2){
    var plotly_points = []
    arg2.points.forEach(function(pt) {
        plotly_points.push(pt.hovertext)
    })
        // Run Ajaxl
        $.ajax({
            url: '/update-article-view',
            type: 'POST',
            data: JSON.stringify(plotly_points),
            contentType: "application/json",
            beforeSend: function () {
            }, success: function (res) {
                $("#articlePageView").html(res.data);
            }
        });
})

$(document).on('plotly_click', "#myDiv", function (arg1, arg2) {
arg2.points.forEach(function(pt) {
//   Think what to do here...
})
})


