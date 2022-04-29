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
                drawChartView()
            }
        });
    })

    // // This is for toggle view
    var embeddingViewData = $('#articleEmbeddingView').data('article')
    embeddingView(embeddingViewData);

    // This is for time filter.

    // let ctx = $('#chartContainer');
    // let _filterdate = ctx.data('date')
    // let _filtercount = ctx.data('count')
    // // To toggle between article and embedding view.
    //
    // const myChart = new Chart(ctx, {
    //     type: 'bar',
    //     data: {
    //         labels: _filterdate,
    //         datasets: [{
    //             label: '# of Articles',
    //             data: _filtercount,
    //             backgroundColor: "#A74482",
    //             borderColor: [],
    //             borderWidth: 1
    //         }]
    //     },
    //     options: {
    //         scales: {
    //             y: {
    //                 beginAtZero: true
    //             }
    //         }
    //     }
    // });


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


//This is for the chart view
document.addEventListener('DOMContentLoaded', function () {
    drawChartView()

});

function drawChartView(){
    let ctx = $('#chartContainer');
    let _filterdate = ctx.data('date')
    let _filtercount = ctx.data('count')
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
    }, tooltip: {
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
      categories: _filterdate,
      tickmarkPlacement: 'on',
      tickInterval: 1,
      minRange: 1, // set this to allow up to one year to be viewed
    },
    yAxis: {
      title: {
        text: 'Number',
        style: {
          fontSize: '0px'
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
      data: _filtercount,
    }]
  }, function(chart) {
      let myData = _filterdate;
   let slider_config = {
    range: true,
        min: 0,
        max: myData.length - 1,
        step: 1,
        slide: function( event, ui ) {
            // Set the real value into the inputs
            $("#amount").val(myData[ui.values[0]]  + " - " + myData[ui.values[1]]);
        chart.xAxis[0].setExtremes(ui.values[0], ui.values[1]);
        },
    create: function() {
        $(this).slider('values',0,0);
        $(this).slider('values',1,myData.length - 1);
    }
};

// Render Slider
$('#slider-range').slider(slider_config)


  });
}



