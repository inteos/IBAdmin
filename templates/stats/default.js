{% load ibadtexts %}
<script>
{% for stat in params %}
  var starttime{{ stat.parid.parid }} = moment().subtract(24, 'hours');
  var endtime{{ stat.parid.parid }} = moment();
  var data{{ stat.parid.parid }} = [];
  var interval{{ stat.parid.parid }};
  var live{{ stat.parid.parid }} = false;
  var bartype{{ stat.parid.parid }} = {{ stat.parid.chart }};
  {% if stat.parid.unit == 'Bytes' %}
  var valuediv{{ stat.parid.parid }} = 3;
  {% else %}
  var valuediv{{ stat.parid.parid }} = 1;
  {% endif %}
  var options{{ stat.parid.parid }} = {
    series: { shadowSize: 0, },
    legend: { position: 'nw', },
    xaxis: {
      tickDecimals: 0,
      mode: "time",
      timezone: "browser",
    },
    yaxes: [
      {tickDecimals: 0, min: 0,},               // 1 - autoscale, integer, min zero
      {tickDecimals: 1, min: 0, max: 100,},     // 2 - percent display
      {tickDecimals: 0,},                       // 3 - autoscale, integer
      {tickDecimals: 1,},                       // 4 - autoscale, decimal point
      {tickDecimals: 1, min: 0,},               // 5 - autoscale, decimal point, min zero
      {tickDecimals: 0, ticks: [[0, "Offline"], [1, "Online"]], min: -1, max: 2, },    // 6 - binary status display
    ],
    colors: ['#3c8dbc'],
  };
  var plot{{ stat.parid.parid }} = $.plot("#display{{ stat.parid.parid }}", data{{ stat.parid.parid }}, options{{ stat.parid.parid }})
  function fetchData{{ stat.parid.parid }}() {
    var url{{ stat.parid.parid }} = '';
    function onDataReceived(series) {
      data{{ stat.parid.parid }} = [series];
      plot{{ stat.parid.parid }}.setData(data{{ stat.parid.parid }});
      plot{{ stat.parid.parid }}.setupGrid();
      plot{{ stat.parid.parid }}.draw();
      $("#loading{{ stat.parid.parid }}").hide();
    };
    $("#loading{{ stat.parid.parid }}").show();
    url{{ stat.parid.parid }}='{% url 'statsdata_rel' stat.parid.name %}'+starttime{{ stat.parid.parid }}.format("X")+'/'+endtime{{ stat.parid.parid }}.format("X")+'/'+bartype{{ stat.parid.parid }}+'/'+valuediv{{ stat.parid.parid }}+'/';
    $('#daterangespan{{ stat.parid.parid }}').html(' ' + starttime{{ stat.parid.parid }}.format('YYYY-MM-DD') + ' - ' + endtime{{ stat.parid.parid }}.format('YYYY-MM-DD') + ' ');
    $.ajax({
      url: url{{ stat.parid.parid }},
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
  // flot init
  $(function () {
    fetchData{{ stat.parid.parid }}();
  });
  //Date range as a button
  $('#daterange{{ stat.parid.parid }}').daterangepicker(
    {
      locale: {
        "firstDay": 1,
        format: 'YYYY-MM-DD',
      },
      opens: "left",
      minDate: moment("{{ stat.mintime|date:'U' }}","X"),
      maxDate: moment("{{ stat.maxtime|date:'U' }}","X"),
      ranges: {
        'Last Hour': [moment().subtract(1, 'hour'), moment()],
        'Today': [moment().startOf('day'), moment().endOf('day')],
        'Yesterday': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
        'Last 24 Hours': [moment().subtract(24, 'hours'), moment()],
        'Last 7 Days': [moment().subtract(7, 'days'), moment()],
        'Last 30 Days': [moment().subtract(30, 'days'), moment()],
        'This Month': [moment().startOf('month'), moment().endOf('month')],
        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
      },
      startDate: moment().subtract(24, 'hours'),
      endDate: moment()
    },
    function (start, end) {
      starttime{{ stat.parid.parid }} = start;
      endtime{{ stat.parid.parid }} = end;
      fetchData{{ stat.parid.parid }}();
    }
  );
  $("#chartmenu{{ stat.parid.parid }} li a").click(function(event){
    event.preventDefault();
    var selText = $(this).html();
    var selValue = $(this).data('chart');
    if (selValue != bartype{{ stat.parid.parid }}){
      bartype{{ stat.parid.parid }} = selValue;
      $('#chtype{{ stat.parid.parid }}').html(selText+' <span class="caret"></span>');
      if (selValue == 1){   // not ideal but simple :)
        $('#charticon{{ stat.parid.parid }}').removeClass().addClass("fa {{ 1|charticon }}");
      } else
      if (selValue == 2){
        $('#charticon{{ stat.parid.parid }}').removeClass().addClass("fa {{ 2|charticon }}");
      } else
      if (selValue == 3){
        $('#charticon{{ stat.parid.parid }}').removeClass().addClass("fa {{ 3|charticon }}");
      };
      fetchData{{ stat.parid.parid }}();
    };
  });
{% if stat.parid.unit == 'Bytes' %}
  $("#chartdiv{{ stat.parid.parid }} li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('chart');
    if (selValue != valuediv{{ stat.parid.parid }}){
      valuediv{{ stat.parid.parid }} = selValue;
      $('#chdiv{{ stat.parid.parid }}').html('<i class="glyphicon glyphicon-scale"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.parid.parid }}();
    };
  });
{% endif %}
{% if stat.parid.unit == 'Bytes/s' %}
  $("#chartdiv{{ stat.parid.parid }}3 li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('chart');
    if (selValue != valuediv{{ stat.parid.parid }}){
      valuediv{{ stat.parid.parid }} = selValue;
      $('#chdiv{{ stat.parid.parid }}3').html('<i class="glyphicon glyphicon-scale"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.parid.parid }}();
    };
  });
{% endif %}
  function refreshData{{ stat.parid.parid }}(){
    starttime{{ stat.parid.parid }} = moment().subtract(1, 'hour');
    endtime{{ stat.parid.parid }} = moment();
    fetchData{{ stat.parid.parid }}();
  };
  $('#live{{ stat.parid.parid }}, #live{{ stat.parid.parid }}btn').click(function(){
    if (!live{{ stat.parid.parid }}){
      // start live update
      $('#liveico{{ stat.parid.parid }}').removeClass().addClass("fa fa-play-circle");
      $('#daterange{{ stat.parid.parid }}').hide();
      $('#daterange{{ stat.parid.parid }}cam').show();
      refreshData{{ stat.parid.parid }}();
      interval{{ stat.parid.parid }} = setInterval(refreshData{{ stat.parid.parid }}, 60000);
      live{{ stat.parid.parid }} = true;
    } else {
      // stop the live
      $('#liveico{{ stat.parid.parid }}').removeClass().addClass("fa fa-play-circle-o");
      $('#daterange{{ stat.parid.parid }}').data('daterangepicker').setStartDate(starttime{{ stat.parid.parid }});
      $('#daterange{{ stat.parid.parid }}').data('daterangepicker').setEndDate(endtime{{ stat.parid.parid }});
      $('#daterange{{ stat.parid.parid }}cam').hide();
      $('#daterange{{ stat.parid.parid }}').show();
      clearInterval(interval{{ stat.parid.parid }});
      live{{ stat.parid.parid }} = false;
    }
  });
{% endfor %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
