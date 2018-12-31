  $(function(){
    $('#scheduleweek_7').change(function(){
        var control;
        var controls = ['#monlevel', '#tuelevel', '#wedlevel', '#thulevel', '#frilevel', '#satlevel', '#sunlevel'];
        if ($('#scheduleweek_7').val() == 'full'){
            for (var i = 0; i < 7; i++) {
                control = '#scheduleweek_' + i;
                $(control).val("full").trigger("change");
                $(control).attr('disabled','disabled');
            }
        } else
        if ($('#scheduleweek_7').val() == 'incr'){
            for (var i = 0; i < 7; i++) {
                control = '#scheduleweek_' + i;
                $(control).val("incr").trigger("change");
                $(control).attr('disabled','disabled');
            }
        } else
        if ($('#scheduleweek_7').val() == 'diff'){
            for (var i = 0; i < 7; i++) {
                control = '#scheduleweek_' + i;
                $(control).val("diff").trigger("change");
                $(control).attr('disabled','disabled');
            }
        } else
        if ($('#scheduleweek_7').val() == 'off'){
            for (var i = 0; i < 7; i++) {
                control = '#scheduleweek_' + i;
                $(control).removeAttr('disabled');
            }
        }
    });
  });
