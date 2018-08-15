<script>
$(function () {
  // Initialize Select2 Elements
  $(".select2").select2();
});
$(".timepicker").timepicker({
    showInputs: false,
    minuteStep: 1,
    showMeridian: false,
});
$(function() {
  $('#{{ form.enabled.id_for_label }}').change(function() {
    checked = $(this).prop('checked');
    if (!checked){
      $('#disableconfirm').modal('show');
    };
  })
});
$('#disableconfirmbutton, #disableconfirmbuttonx').on('click', function () {
  $('#disableconfirm').modal('hide');
  $('#{{ form.enabled.id_for_label }}').bootstrapToggle('on');
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.catalogadvanced' %}