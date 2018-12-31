  function fetchData{{ id }}() {
    function onDataReceived(series) {
      data = [series];
      $.plot("#{{ id }}", data, {
        lines: {
          show: true,
          fill: true,
        },
        series: {
          shadowSize: 0,
        },
        points: {
          show: false
        },
        xaxis: {
          tickDecimals: 0,
          mode: "time",
          timezone: "browser",
        },
        yaxis: {
          tickDecimals: 1,
          min: 0,
          max: 100,
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