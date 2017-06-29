<script>
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
