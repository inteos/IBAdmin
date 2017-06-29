<script>
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
          tickDecimals: 1,
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
  // flot init and refresh calls
  $(function () {
    fetchData{{ id }}();
    setInterval(fetchData{{ id }}, 60000);
  });
</script>

