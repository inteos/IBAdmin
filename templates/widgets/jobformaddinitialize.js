  $(function () {
    // Initialize Select2 Elements
    $(".select2").select2();
    // Initialize backupsch and all forms
    $('#divrepeat').show();
    $('#divweekdays').hide();
    $('#divmonthdays').hide();
    $(".timepicker").timepicker({
        showInputs: false,
        minuteStep: 1,
        showMeridian: false,
    });
    $('input').iCheck({
      //Initialize iCheck - boxes
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue',
    });
    $("#addform").submit(function() {
        $('select').removeAttr('disabled');
    });
  });