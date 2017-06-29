{% load ibadtexts %}
<script>
{% for stat in params %}
  var last{{ stat.id }} = 0;
  var data{{ stat.id }} = [];
  var interval{{ stat.id }};
  var bartype{{ stat.id }} = {{ stat.chart }};
  {% if stat.unit == 1 or stat.unit == 3 %}
  var valuediv{{ stat.id }} = 3;
  {% else %}
  var valuediv{{ stat.id }} = 1;
  {% endif %}
  var options{{ stat.id }} = {
    series: { shadowSize: 0, },
    legend: { position: 'nw', },
    xaxis: {
      show: false,
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
  var plot{{ stat.id }} = $.plot("#display{{ stat.id }}", data{{ stat.id }}, options{{ stat.id }})
  function fetchData{{ stat.id }}() {
    var url{{ stat.id }} = '';
    function onDataReceived(series) {
      data{{ stat.id }} = [series];
      plot{{ stat.id }}.setData(data{{ stat.id }});
      plot{{ stat.id }}.setupGrid();
      plot{{ stat.id }}.draw();
      $("#loading{{ stat.id }}").hide();
    };
    $("#loading{{ stat.id }}").show();
    url{{ stat.id }}='{{ stat.url }}'+last{{ stat.id }}+'/'+bartype{{ stat.id }}+'/'+valuediv{{ stat.id }}+'/';
    $.ajax({
      url: url{{ stat.id }},
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
  // flot init and refresh calls
  $(function () {
    fetchData{{ stat.id }}();
    setInterval(fetchData{{ stat.id }}, 60000);
  });
  $("#chartmenu{{ stat.id }} li a").click(function(event){
    event.preventDefault();
    var selText = $(this).html();
    var selValue = $(this).data('chart');
    if (selValue != bartype{{ stat.id }}){
      bartype{{ stat.id }} = selValue;
      $('#chtype{{ stat.id }}').html(selText+' <span class="caret"></span>');
      if (selValue == 1){   // not ideal but simple :)
        $('#charticon{{ stat.id }}').removeClass().addClass("fa {{ 1|charticon }}");
      } else
      if (selValue == 2){
        $('#charticon{{ stat.id }}').removeClass().addClass("fa {{ 2|charticon }}");
      } else
      if (selValue == 3){
        $('#charticon{{ stat.id }}').removeClass().addClass("fa {{ 3|charticon }}");
      };
      fetchData{{ stat.id }}();
    };
  });
{% if stat.unit == 1 %}
  $("#chartdiv{{ stat.id }}1 li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('chart');
    if (selValue != valuediv{{ stat.id }}){
      valuediv{{ stat.id }} = selValue;
      $('#chdiv{{ stat.id }}1').html('<i class="glyphicon glyphicon-scale"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.id }}();
    };
  });
{% endif %}
{% if stat.unit == 2 %}
  $("#chartdiv{{ stat.id }}2 li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('chart');
    if (selValue != valuediv{{ stat.id }}){
      valuediv{{ stat.id }} = selValue;
      $('#chdiv{{ stat.id }}2').html('<i class="glyphicon glyphicon-scale"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.id }}();
    };
  });
{% endif %}
{% if stat.unit == 3 %}
  $("#chartdiv{{ stat.id }}3 li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('chart');
    if (selValue != valuediv{{ stat.id }}){
      valuediv{{ stat.id }} = selValue;
      $('#chdiv{{ stat.id }}3').html('<i class="glyphicon glyphicon-scale"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.id }}();
    };
  });
{% endif %}
  $("#lastopt{{ stat.id }} li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = $(this).data('last');
    if (selValue != last{{ stat.id }}){
      last{{ stat.id }} = selValue;
      $('#lastdiv{{ stat.id }}').html('<i class="fa fa-clock-o"></i> '+selText+' <span class="caret"></span>');
      fetchData{{ stat.id }}();
    };
  });
  $('#chartrefresh{{ stat.id }}').click(fetchData{{ stat.id }});
{% endfor %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
