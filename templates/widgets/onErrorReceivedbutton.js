  function onErrorReceived(request,status,error){
    button.button('Done...');
    var modal = button.closest('.modal')
    modal.modal('hide');
    modal.on('hidden.bs.modal', function (){
      button.text(text);
    });
    {% include 'widgets/errorprocessingajax.js' %}
  };