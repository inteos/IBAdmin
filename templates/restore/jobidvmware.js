{% include 'widgets/restorejobidinitialize.js' %}
<script>
$(function () {
  $('#{{ form.where.id_for_label }}-group').hide();
  $('#{{ form.replace.id_for_label }}-group').hide();
  $('#{{ form.localrestore.id_for_label }}').on('ifChanged', function(e) {
    var isChecked = e.currentTarget.checked;
    if (isChecked){
      $('#{{ form.where.id_for_label }}-group').show();
      $('#{{ form.replace.id_for_label }}-group').show();
      $('#{{ form.datastore.id_for_label }}-group').hide();
      $('#{{ form.restoreesx.id_for_label }}-group').hide();
    } else {
      $('#{{ form.where.id_for_label }}-group').hide();
      $('#{{ form.replace.id_for_label }}-group').hide();
      $('#{{ form.datastore.id_for_label }}-group').show();
      $('#{{ form.restoreesx.id_for_label }}-group').show();
    };
  });
  $("#restoreform").validate({
    rules: {
      {{ form.comment.name }}: {
        maxlength: 128,
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
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='restore.jobidvmware' %}
