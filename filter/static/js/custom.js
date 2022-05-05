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
    embeddingView()
    $("#searchArticle").on('keyup', function () {
        let request_parameters = {
            q: $(this).val() // value of user_input: the HTML element with ID user-input
        }
        // Run Ajaxl
        $.ajax({
            url: '/articles-search', data: request_parameters, beforeSend: function () {
            }, success: function (res) {
                $('#filteredArticles').html(res.data);
                embeddingView();
                drawTimeView();
            }
        });
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
                embeddingView();
                drawTimeView()
            }
        });
    })
})

function embeddingView() {
    // Run Ajaxl
    let data = $('#articleEmbeddingView').data('article')
    let jsonText = JSON.stringify(data);
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
$(document).on('plotly_selected', "#myDiv", function (arg1, arg2) {
    var plotly_points = []
    arg2.points.forEach(function (pt) {
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
            updateTimeView(res.data2['published_data'], res.data2['article_count'])
        }
    });
})

$(document).on('plotly_click', "#myDiv", function (arg1, arg2) {
    arg2.points.forEach(function (pt) {
//   Think what to do here...
    })
})


//This is for the time view
document.addEventListener('DOMContentLoaded', function () {
    drawTimeView()

});

function drawTimeView() {
    let ctx = $('#chartContainer');
    let _publishedyears = ctx.data('date')
    let _count = ctx.data('count')
    updateTimeView(_publishedyears, _count)

}

function updateArticleView(val1, val2) {
    $.ajax({
        url: '/update-article-time-view',
        type: 'POST',
        data: JSON.stringify([val1, val2]), dataType: 'json', beforeSend: function () {
        }, success: function (res) {
            $("#articlePageView").html(res.data);
            $('#myDiv').html(res.data2);
        }
    })
}

function updateTimeView(_publishedyears, _count) {
    year = _publishedyears.map(i => Number(i))
    year_min = Math.min(...year)
    year_max = Math.max(...year)
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
            style: {
                fontSize: '0px'
            }
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
                updateArticleView(myData[ui.values[0]], myData[ui.values[1]])
            }
        };
        $('#slider-range').slider(slider_config)
        $("#amount").val(year_min.toString() +
            " - " + year_max.toString());

    });

}

$(document).on('click', ".custom-item", function () {

    var _vm = $(this);
    var _index = _vm.attr('area-controls');
})
