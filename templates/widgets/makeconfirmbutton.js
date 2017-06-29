$('#{{ id|default:'makeconfirm' }}button').on('click', function () {
  var $btn = $(this).button('loading')
  function onDataReceived(data) {
    $btn.button('Done...')
    location.href=data[0]
  };
  $.ajax({
    url: this.value,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
})
