  $(function(){
    $('#{{ form.backupsch.id_for_label }}').change(function(){
      if ($('#{{ form.backupsch.id_for_label }}').val() == 'c1'){
        $('#divrepeat').show();
        $('#divweekdays').hide();
        $('#divmonthdays').hide();
      } else
      if ($('#{{ form.backupsch.id_for_label }}').val() == 'c2'){
        $('#divrepeat').hide();
        $('#divweekdays').show();
        $('#divmonthdays').hide();
      } else
      if ($('#{{ form.backupsch.id_for_label }}').val() == 'c3'){
        $('#divrepeat').hide();
        $('#divweekdays').hide();
        $('#divmonthdays').show();
      }
    });
  });