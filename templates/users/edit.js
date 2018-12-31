<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
  });
  $("#editform").validate({
    rules: {
      {{ form.email.name }}: {
        required: true,
        email: true,
      },
      {{ form.firstname.name }}:{
        maxlength: 30,
      },
      {{ form.lastname.name }}: {
        maxlength: 30,
      },
      {{ form.password.name }}_r: {
        equalTo: "#{{ form.password.id_for_label }}",
      },
    },
    messages: {
      {{ form.password.name }}_r: "Passwords does not match. Retype again.",
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
{% if form.username.value == user.username %}
  $('#{{ form.password.id_for_label }}').change(function(event){
    $('#passwdinfo').show();
  });
{% endif %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='users.edit' %}