  $(".dropdown-menu li a").click(function(event){
    event.preventDefault();
    var selText = $(this).text();
    var selValue = this.id;
    $('#{{ form.retention.id_for_label }}-button').html(selText+' <span class="caret"></span>');
    $('#{{ form.retention.id_for_label }}-interval').val(selValue);
  });