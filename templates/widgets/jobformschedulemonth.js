  $(function(){
    $('#schedulemonth_31').change(function(){
      var control;
      if ($('#schedulemonth_31').val() == 'full'){
        for (var i = 0; i < 31; i++) {
          control = '#schedulemonth_' + i;
          $(control).val("full").trigger("change");
          $(control).attr('disabled','disabled');
        }
      } else
      if ($('#schedulemonth_31').val() == 'incr'){
        for (var i = 0; i < 31; i++) {
          control = '#schedulemonth_' + i;
          $(control).val("incr").trigger("change");
          $(control).attr('disabled','disabled');
        }
      } else
      if ($('#schedulemonth_31').val() == 'diff'){
        for (var i = 0; i < 31; i++) {
          control = '#schedulemonth_' + i;
          $(control).val("diff").trigger("change");
          $(control).attr('disabled','disabled');
        }
      } else
      if ($('#schedulemonth_31').val() == 'off'){
        for (var i = 0; i < 31; i++) {
          control = '#schedulemonth_' + i;
          $(control).removeAttr('disabled');
        }
      }
    });
  });