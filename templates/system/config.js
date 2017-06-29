<script>
$(function () {
  $(".select2").select2();
});
$(function () {
  var form = $("#editform");
  form.validate({
    rules: {
      {{ form.email.name }}: {
        required: true,
        email: true,
      },
    },
    highlight: function(element) {
      $(element).closest('.form-group').addClass('has-error');
      $(element).closest('.form-group').removeClass('has-success');
    },
    unhighlight: function(element) {
      $(element).closest('.form-group').removeClass('has-error');
      $(element).closest('.form-group').addClass('has-success');
    },
    errorElement: 'span',
    errorClass: 'help-block',
    errorPlacement: function(error, element) {
      if(element.parent('.input-group').length) {
        error.insertAfter(element.parent());
      } else {
        error.insertAfter(element);
      }
    }
  });
  $('#savebutton').on('click', function (e){
    if (form.valid()){
      $('#saveinfo').hide();
      var formdata = $("#editform").serialize();
      function onSavedata(data){
        if (data){
          $('#restartsrvinfo').show();
        } else {
          $('#restartsrvinfo').hide();
        };
        $('#saveinfo').show();
      };
      $.ajax({
        url: "{% url 'systemconfigsave' %}",
        type: "POST",
        data: formdata,
        dataType: "json",
        success: onSavedata,
      });
    };
  });
});
</script>
{% include "pages/refresh.js" %}
