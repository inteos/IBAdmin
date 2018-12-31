<script>
  function formatColor(data){
    if (!data.id) { return data.text };
    return $('<span>').html(data).addClass("label "+data.id).append(data.text);
  };
  $(function () {
    $(".label-color").select2({
      templateResult: formatColor,
      templateSelection: formatColor,
    });
    $(".perms").select2();
  });
  var interval;
  function selectreload(){
    clearInterval(interval);
    $('.perms').select2("destroy").select2();
  };
  $(".perms").on("select2:select select2:unselect", function(d){
    $('.perms').find('option').attr('disabled', false);
    var val = $(this).val();
    if (val && val.length){
      for (i=0;i<val.length;i++){
        if (val[i].startsWith('addallperms_')){
          $('.perms').find('option[value="'+val[i]+'"]').parent().find('option').attr('disabled', 'disabled');
        };
      };
    };
    interval = setInterval(selectreload);
  });
  $("#addform").submit(function(){
    $('.perms').find('option').attr('disabled', false);
  });
  $("#addform").validate({
    rules: {
      {{ form.name.name }}: {
        required: true,
        maxlength: 80,
        remote: {
          url: "{% url 'rolesname' %}"
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
{% include 'widgets/helpbutton.js' with helppage='departments.add' %}