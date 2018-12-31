<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
  });
  $("#addform").validate({
    rules: {
      {{ form.username.name }}: {
        required: true,
        alphanumeric: true,
        maxlength: 150,
        remote: {
          url: "{% url 'usersname' %}"
        },
      },
      {{ form.firstname.name }}:{
        maxlength: 30,
      },
      {{ form.lastname.name }}: {
        maxlength: 30,
      },
      {{ form.email.name }}: {
        required: true,
        email: true,
      },
      {{ form.password.name }}_r: {
        equalTo: "#{{ form.password.id_for_label }}",
      },
    },
    messages: {
      {{ form.username.name }}: {
        remote: "User name already exist. Choose other.",
      },
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
  $('#{{ form.usertype.id_for_label }}').on('change', function(event){
    if (this.value == 'super'){
      $('#{{ form.departments.id_for_label }}').val(null).trigger("change");
      $('#{{ form.departments.id_for_label }}').prop('disabled', true);
      $('#{{ form.roles.id_for_label }}').val(null).trigger("change");
      $('#{{ form.roles.id_for_label }}').prop('disabled', true);
    } else if (this.value == 'admin'){
      $('#{{ form.roles.id_for_label }}').val(null).trigger("change");
      $('#{{ form.roles.id_for_label }}').prop('disabled', true);
    } else {
      $('#{{ form.departments.id_for_label }}').prop('disabled', false);
      $('#{{ form.roles.id_for_label }}').prop('disabled', false);
    };
  });
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='users.add' %}