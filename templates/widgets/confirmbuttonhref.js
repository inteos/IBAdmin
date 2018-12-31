$('{{ selector }}').on('click', function () {
  var button = $(this);
  var text = button.text();
  button.button('loading');
  var url = button.data('url');
  function onDataReceived(data) {
    button.button('Done...');
  {% if href %}
    location.href="{{ href }}";
  {% else %}
    location.href=data['href'];
  {% endif %}
  };
{% include 'widgets/onErrorReceivedbutton.js' %}
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
    error: onErrorReceived,
  });
})