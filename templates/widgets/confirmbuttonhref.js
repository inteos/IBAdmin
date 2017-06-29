$('{{ selector }}').on('click', function () {
  var button = $(this);
  button.button('loading');
  var url = button.data('url');
  function onDataReceived(data) {
    button.button('Done...');
    location.href=data['href']
  };
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
})