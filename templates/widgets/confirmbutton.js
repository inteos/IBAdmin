$('{{ selector }}').on('click', function () {
  var button = $(this);
  var text = button.text();
  button.button('loading');
  var url = button.data('url');
  function onDataReceived(data) {
    button.button('Done...');
    var modal = button.closest('.modal')
    modal.modal('hide');
    {{ table|default:'table' }}.ajax.reload( null, false ); // user paging is not reset on reload
    modal.on('hidden.bs.modal', function (){
      button.text(text);
    });
  };
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
