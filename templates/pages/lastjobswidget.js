  function fetchData{{ id }}(){
    $("#{{ id }}").load('{% url id %}', function() { $("#{{ id }}loading").hide(); });
  };
  {% include 'pages/refreshbutton.js' %}