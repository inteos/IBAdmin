  function fetchData{{ id }}() {
    function onDataReceived(series) {
      data = [series];
      $.plot("#{{ id }}", data, {
        lines: {
          show: true,
          fill: false,
        },
        series: {
          shadowSize: 0,
        },
        points: {
          show: true,
        },
        xaxis: {
          tickDecimals: 0,
          mode: "time",
          timezone: "browser",
        },
        yaxis: {
          tickDecimals: 0,
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
