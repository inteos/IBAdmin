<script>
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
  $('#{{ form.password.id_for_label }}').change(function(event){
    $('#passwdinfo').show();
  });
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='users.editprofile' %}