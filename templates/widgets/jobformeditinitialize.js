  $(function () {
    // Initialize Select2 Elements
    $(".select2").select2();
    // Initialize backupsch and all forms
    {% if form.backupsch.value == 'c1' %}
    $('#divrepeat').show();
    $('#divweekdays').hide();
    $('#divmonthdays').hide();
    {% endif %}
    {% if form.backupsch.value == 'c2' %}
    $('#divrepeat').hide();
    $('#divweekdays').show();
    $('#divmonthdays').hide();
    {% endif %}
    {% if form.backupsch.value == 'c3' %}
    $('#divrepeat').hide();
    $('#divweekdays').hide();
    $('#divmonthdays').show();
    {% endif %}
    $('input').iCheck({
      //Initialize iCheck - boxes
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue',
    });
    $("#editform").submit(function() {
        $('select').removeAttr('disabled');
    });
    $(".timepicker").timepicker({
        showInputs: false,
        minuteStep: 1,
        showMeridian: false,
    });
  });

