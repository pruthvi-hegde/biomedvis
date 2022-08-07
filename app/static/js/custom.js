let minYear = ""
let maxYear = ""
let chartHigh = null

$(document).on('click', ".custom-info", function () {

    let _index = $(this).attr('data-index');
    let _articleTitle = $(".article-title-" + _index).val();
    let _articleThumbnail = $(".article-thumbnail-" + _index).val()
    let _articleDOI = $(".article-DOI-" + _index).val()
    let _articleYear = $(".article-publishedDate-" + _index).val()
    let _abstract = $(".article-abstract-" + _index).val()
    _articleTitle = _articleTitle + ' (' + _articleYear + ')'
    $("#exampleModalLongTitle").text(_articleTitle)
    $("#articleThumbnail").attr('src', _articleThumbnail)

    $("#articleDOI").attr('href', _articleDOI)
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
    let $input = $('#searchArticle');

    /* $input.on('keyup keypress', function (event) {
         var key = event.keyCode || event.which;
         if (key === 13) {
             event.preventDefault();
             return false;
         }
     });*/

    //on keyup, start the countdown
    $input.on('keyup', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(populate_search, doneTypingInterval);
    });

    //on keydown, clear the countdown
    $input.on('keydown', function () {
        clearTimeout(typingTimer);
    });

    $('input[type=search]').on('search', function () {
        populate_search()
    });

    function populate_search() {
        let request_parameters = {
            q: $input.val() // value of user_input: the HTML element with ID user-input
        }
        // Run Ajaxl
        $.ajax({
            url: '/articles-search', data: request_parameters, success: function (res) {
                $('#filteredArticles').html(res.article_view_data);
                updateTimeView(res.time_view_data['published_year'], res.time_view_data['article_count'], false)
                $('#myDiv').html(res.embedding_view_data);
                $("#selDataset").val(res.selected_model).trigger('chosen:updated');
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
        // Run Ajax
        $.ajax({
            url: '/filter-data', data: _filterObj, dataType: 'json', beforeSend: function () {
            }, success: function (res) {
                $("#filteredArticles").html(res.article_view_data);
                updateTimeView(res.time_view_data['published_data'], res.time_view_data['article_count'], false)
                $('#myDiv').html(res.embedding_view_data);
                $("#selDataset").val(res.selected_model).trigger('chosen:updated');
                enableDropdown()
            },
        });
    })

    enableDropdown()
});

function enableDropdown() {
    let $selDataset = $('#selDataset')
    $selDataset.on('change', embeddingView);
    $.proxy(embeddingView, $selDataset)();
}

function embeddingView() {
    let selection_data = {
        selectedModel: $('#selDataset').val(),
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
    let _publishedyears = ctx.data('year')
    let _count = ctx.data('count')
    updateTimeView(_publishedyears, _count, true)

}

function updateTimeView(_publishedyearsSelected, _countSelected, flag) {
    console.log(_countSelected)
    console.log(_publishedyearsSelected)
    let _count = []
    let _publishedYears = [2008, 2010, 2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    for (let i = 0; i < _publishedYears.length; i++) {
        _count[i] = 0
    }
    for (let i = 0; i < _publishedYears.length; i++) {
        for (let j = 0; j < _publishedyearsSelected.length; j++) {
            if (_publishedYears[i] === _publishedyearsSelected[j]) {
                _count[i] = _countSelected[j]
            }
        }
    }

    Highcharts.chart('slider-bar-chart', {
        chart: {
            type: 'column', zoomType: 'x'
        }, colors: ['#d8d826'], legend: {
            enabled: false
        }, title: {
            text: ''
        }, tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' + '<td style="padding:0"><b>{point.y:.f}</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        }, subtitle: {
            style: {
                fontSize: '0px'
            }
        }, xAxis: {
            categories: _publishedYears, tickmarkPlacement: 'on', tickInterval: 1, minRange: 1, // set this to allow up to one year to be viewed
            gridLineColor: 'transparent', linecolor: 'black', style: {
                font_family: 'Calibri'
            }
        }, yAxis: {
            tickmarkPlacement: 'on', minRange: 1, gridLineColor: 'transparent', linecolor: 'black', title: {
                text: '', style: {
                    font_family: 'Calibri'
                }
            }
        }, plotOptions: {
            column: {
                pointPadding: 0.01, borderWidth: 0
            }, series: {
                cursor: 'pointer',
            }
        }, series: [{
            name: 'No of articles by year', data: _count,
        }]
    }, function (chart) {
        let myData = _publishedYears;
        let currentmin = 0
        let currentmax = myData.length - 1

        if (minYear !== "") {
            for (let i = 0; i < myData.length; i++) {
                if (myData[i] === minYear) {
                    currentmin = i
                }
            }
        }

        if (maxYear !== "") {
            for (let i = 0; i < myData.length; i++) {
                if (myData[i] === maxYear) {
                    currentmax = i
                }
            }
        }

        let slider_config = {
            range: true, min: 0, max: 10, step: 1, values: [currentmin, currentmax], slide: function (event, ui) {
                if (ui.values[0] === ui.values[1]) {
                    $("#sliderLabel").val(myData[ui.values[0]]);
                } else {
                    $("#sliderLabel").val(myData[ui.values[0]] + '-' + myData[ui.values[1]]);
                }
                chart.xAxis[0].setExtremes(ui.values[0], ui.values[1]);
            }, stop: function (_, ui) {
                minYear = myData[ui.values[0]]
                maxYear = myData[ui.values[1]]
                updateArticleTimeView(minYear, maxYear, flag)
            }
        };

        $('#slider-range').slider(slider_config)
        $("#sliderLabel").val(myData[currentmin] + " - " + myData[currentmax]);
        chart.xAxis[0].setExtremes(currentmin, currentmax);
        updateArticleTimeView(minYear, maxYear, flag)
    });

}

function updateArticleTimeView(minYear, maxYear, flag) {
    console.log('Years')
    console.log(minYear, maxYear)
    var article_data = {
        'minYear': minYear, 'maxYear': maxYear, 'loadFirstTime': flag
    }

    $.ajax({
        url: '/update-article-time-view',
        type: 'POST',
        data: JSON.stringify(article_data),
        dataType: 'json',
        beforeSend: function () {
        },
        success: function (res) {
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
        bounds: true, maxScale: 3, minScale: 1, zoomDoubleClickSpeed: 1,
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
    // Run Ajaxl
    $.ajax({
        url: '/update-article-view',
        type: 'POST',
        data: JSON.stringify(plotly_points),
        contentType: "application/json",
        beforeSend: function () {
        },
        success: function (res) {
            $("#articlePageView").html(res.article_view_data);
            updateTimeView(res.time_view_data['published_year'], res.time_view_data['article_count'], false)
        }
    });
})

$(document).on('plotly_click', '#myDiv', function (arg1, arg2) {
    arg2.points.forEach(function (pt) {
        let article_title = pt.hovertext
        showArticleDetailsView(article_title)

    })
})


function showArticleDetailsView(article_title) {
    // Run Ajaxl
    $.ajax({
        url: '/populate-details-view', type: 'POST', data: JSON.stringify(article_title), success: function (res) {
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