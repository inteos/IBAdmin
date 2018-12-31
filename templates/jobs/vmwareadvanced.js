<script>
$(function () {
  // Initialize Select2 Elements
  $(".select2").select2();
});
{% if Storagededup %}
$(function() {
  $('#{{ form.dedup.id_for_label }}').change(function() {
    checked = $(this).prop('checked');
    if (checked){
      $('#{{ form.compr.id_for_label }}').prop('disabled', true);
    } else {
      $('#{{ form.compr.id_for_label }}').prop('disabled', false);
    };
  })
});
{% endif %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.vmwareadvanced' %}
