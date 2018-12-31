  function fetchData{{ id }}(){
    $("#{{ id }}").load('{% url id %}', function() { $("#{{ id }}loading").hide(); });
  };
  {% include 'pages/refreshbutton.js' %}
  $('#{{ id }}remove').click(function(){
    var url = "{% url 'usersprofiledash' 'off' id %}";
    $.ajax({
      url: url,
      type: "GET",
    });
  });