$(document).on('click', ".custom-info", function () {

    let _index = $(this).attr('data-index');
    let _articleTitle = $(".article-title-" + _index).val();
    let _articleThumbnail = $(".article-thumbnail-" + _index).val()
    let _articleDOI = $(".article-DOI-" + _index).val()
    let _articleYear = $(".article-publishedDate-" + _index).val()
    let _abstract = $(".article-abstract-" + _index).val()
    _articleTitle = _articleTitle + ' (' + _articleYear + ')'

    // $("#name").val(name);
    $("#exampleModalLongTitle").text(_articleTitle)
    $("#articleThumbnail").attr('src', _articleThumbnail)

    $("#articleDOI").attr('href', _articleDOI)
    // $("#articleDOI").text(_articleDOI)
    $("#abstract").text(_abstract)


    $("#articleDetailsModal").modal("show");

})

$(window).bind('setup', function () {
    drawTimeView()
});

//Common document ready function.
$(document).ready(function () {
    $(window).trigger('setup');

    var typingTimer;
    var doneTypingInterval = 500;
    let input = $('#searchArticle');

    //on keyup, start the countdown
    input.on('keyup', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(populate_search, doneTypingInterval);
    });

    //on keydown, clear the countdown
    input.on('keydown', function () {
        clearTimeout(typingTimer);
    });

    $('input[type=search]').on('search', function () {
        populate_search()
    });

    function populate_search() {
        let request_parameters = {
            q: $('#searchArticle').val() // value of user_input: the HTML element with ID user-input
        }
        // Run Ajaxl
        $.ajax({
            url: '/articles-search',
            data: request_parameters,
            success: function (res) {
                $('#filteredArticles').html(res.article_view_data);
                updateTimeView(res.time_view_data['published_date'], res.time_view_data['article_count'], false)
                $('#myDiv').html(res.embedding_view_data);
                enableDropdown()
            }, error: function (xhr, status, error) {
                console.log("inside Error " + error);
            }
        });
    }

    $(".filter-checkbox").on('click', function () {
        let _filterObj = {};
        $(".filter-checkbox").each(function () {
            let _filterKey = $(this).data('filter')

            _filterObj[_filterKey] = Array.from(document.querySelectorAll('input[data-filter=' + _filterKey + ']:checked')).map(function (el) {
                return el.value;
            });
        });
        // Run Ajaxl
        $.ajax({
            url: '/filter-data', data: _filterObj, dataType: 'json', beforeSend: function () {
            }, success: function (res) {
                $("#filteredArticles").html(res.article_view_data);
                updateTimeView(res.time_view_data['published_data'], res.time_view_data['article_count'], false)
                $('#myDiv').html(res.embedding_view_data);
                enableDropdown()
            },
        });
    })

   enableDropdown()
});

function enableDropdown(){
     $('#selDataset').on('change', embeddingView);
    $.proxy(embeddingView, $('#selDataset'))();
}

function embeddingView() {
    let selection_data = {
        // articleData: JSON.stringify($('#articleEmbeddingView').data('article')),
        selectedModel: $('#selDataset').val()
    }
    $.ajax({
        url: '/embedding-view',
        type: 'POST',
        data: JSON.stringify(selection_data),
        traditional: true,
        dataType: 'json',
        success: function (res) {
            $('#myDiv').html(res.embedding_view_data);
        },
        error: function (xhr, status, error) {
            console.log("inside Error " + error);
        }
    });


}

function drawTimeView() {
    let ctx = $('#chartContainer');
    let _publishedyears = ctx.data('date')
    let _count = ctx.data('count')
    // let _tcount = ctx.data('tcount')
    updateTimeView(_publishedyears, _count, true)

}

function updateTimeView(_publishedyears, _count, flag) {
    let year = _publishedyears.map(i => Number(i))
    let year_min = Math.min(...year)
    let year_max = Math.max(...year)
    const min_max = [];
    Highcharts.chart('slider-bar-chart', {
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        colors: [
            '#d8d826'
        ],
        legend: {
            enabled: false
        },
        title: {
            text: ''
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        subtitle: {
            style: {
                fontSize: '0px'
            }
        },
        xAxis: {
            categories: _publishedyears,
            tickmarkPlacement: 'on',
            tickInterval: 1,
            minRange: 1, // set this to allow up to one year to be viewed
            gridLineColor: 'transparent',
            linecolor: 'black',
            style: {
                font_family: 'Calibri'
            }
        },
        yAxis: {
            tickmarkPlacement: 'on',
            minRange: 1,
            gridLineColor: 'transparent',
            linecolor: 'black',
            title: {
                text: '',
                style: {
                    font_family: 'Calibri'
                }
            }
        },
        tooltip: {
            shared: false,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.01,
                borderWidth: 0
            }
        },
        series: [{
            name: 'No of articles by year',
            data: _count,
        }]
    }, function (chart) {
        let myData = _publishedyears;
        let slider_config = {
            range: true,
            min: 0,
            max: myData.length - 1,
            step: 1,
            slide: function (event, ui) {
                if (ui.values[0] === ui.values[1]) {
                    $("#amount").val(myData[ui.values[0]]);
                } else {
                    $("#amount").val(myData[ui.values[0]] + '-' + myData[ui.values[1]]);
                }
                chart.xAxis[0].setExtremes(ui.values[0], ui.values[1]);
            },
            create: function () {
                $(this).slider('values', 0, 0);
                $(this).slider('values', 1, myData.length - 1);
            },
            stop: function (_, ui) {
                updateArticleView(myData[ui.values[0]], myData[ui.values[1]], flag)
            }
        };

        $('#slider-range').slider(slider_config)

        $("#amount").val(year_min.toString() +
            " - " + year_max.toString());

    });

}

function updateArticleView(minYear, maxYear, flag) {
    var article_data = {
        'minYear': minYear,
        'maxYear': maxYear,
        'loadFirstTime': flag
    }

    $.ajax({
        url: '/update-article-time-view',
        type: 'POST',
        data: JSON.stringify(article_data), dataType: 'json', beforeSend: function () {
        }, success: function (res) {
            $("#articlePageView").html(res.article_view_data);
            $('#myDiv').html(res.embedding_view_data);
        }
    })
}

$('[data-toggle="popover"]').popover({
    trigger: 'hover focus',
    placement: 'top',
    template: '<div class="popover awesome-popover-class"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
})

$(document).on('click', ".custom-info", function () {
    const elem = document.getElementById('articleThumbnail')
    const panzoom = Panzoom(elem, {
        bounds: true,
        maxScale: 3,
        minScale: 1,
        zoomDoubleClickSpeed: 1,
    })
    $('.fa-search-plus').on('click', panzoom.zoomIn)
    $('.fa-search-minus').on('click', panzoom.zoomOut)

})

//Update article view after lasso or box select
$(document).on('plotly_deselected', "#myDiv", function () {
    alert("plotly deselected")

})

//Update article view after lasso or box select
$(document).on('plotly_selected', "#myDiv", function (arg1, arg2) {
    let plotly_points = []
    arg2.points.forEach(function (pt) {
        plotly_points.push(pt.hovertext)

    })
    $(this).on('plotly_click', "#myDiv", function (arg1, arg2) {
        arg2.points.forEach(function (pt) {
            let article_title = pt.hovertext
            showArticleDetailsView(article_title)

        })
    })
    // Run Ajaxl
    $.ajax({
        url: '/update-article-view',
        type: 'POST',
        data: JSON.stringify(plotly_points),
        contentType: "application/json",
        beforeSend: function () {
        }, success: function (res) {
            $("#articlePageView").html(res.article_view_data);
            updateTimeView(res.time_view_data['published_data'], res.time_view_data['article_count'], false)
        }
    });
})

$(document).on('plotly_click', "#myDiv", function (arg1, arg2) {
    arg2.points.forEach(function (pt) {
        let article_title = pt.hovertext
        showArticleDetailsView(article_title)

    })
})

function showArticleDetailsView(article_title) {
    // Run Ajaxl
    $.ajax({
        url: '/populate-details-view',
        type: 'POST',
        data: JSON.stringify(article_title),
        success: function (res) {
            let article = res.data
            $("#exampleModalLongTitle").text(article.article_title)
            $("#articleThumbnail").attr('src', article.articleThumbnail)

            $("#articleDOI").attr('href', article.articleDOI)
            // $("#articleDOI").text(_articleDOI)
            $("#abstract").text(article.abstract)


            $("#articleDetailsModal").modal("show");

        }
    });
}