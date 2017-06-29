<script>
  function fetchData{{ id }}(){
    $("#{{ id }}").load('{% url id %}', function() { $("#{{ id }}loading").hide(); });
  };
  {% include 'pages/refreshbutton.js' %}
  $(function(){
    $("#{{ id }}").load('{% url id %}', function() { $("#{{ id }}loading").hide(); });
    setInterval(fetchData{{ id }}, 60000);
  });
</script>
