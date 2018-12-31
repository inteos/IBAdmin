  function fetchData{{ id }}() {
    function onDataReceived(series) {
      data = [series];
      $.plot("#{{ id }}", data, {
        series: {
          shadowSize: 0,
        },
        bars: {
          show: true,
          barWidth: series.barWidth,
          align: "center"
        },
        xaxis: {
          tickDecimals: 0,
          mode: "time",
          timezone: "browser",
        },
        yaxis: {
          tickDecimals: 0,
          min: 0,
        },
      });
      $("#{{ id }}loading").hide();
    };
    $.ajax({
      url: '{% url id %}',
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
  {% include 'pages/refreshbutton.js' %}
  $('#{{ id }}remove').click(function(){
    var url = "{% url 'usersprofiledash' 'off' id %}";
    $.ajax({
      url: url,
      type: "GET",
    });
  });