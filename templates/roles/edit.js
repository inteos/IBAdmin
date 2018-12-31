<script>
  function formatColor(data){
    if (!data.id) { return data.text };
    return $('<span>').html(data).addClass("label "+data.id).append(data.text);
  };
  $(function () {
    $(".select2").select2({
      templateResult: formatColor,
      templateSelection: formatColor,
    });
  });
  $("#editform").validate({
    rules: {
      {{ form.name.name }}: {
        required: true,
        maxlength: 80,
        remote: {
          url: "{% url 'rolesnameother' form.name.value %}"
        },
      },
    },
    messages: {
      {{ form.name.name }}: {
        remote: "Role name already exist. Choose other.",
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
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='roles.edit' %}