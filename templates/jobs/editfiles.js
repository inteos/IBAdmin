<script>
$(function () {
    //Initialize Select2 Elements
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
});
$("#editform").submit(function() {
    $('select').removeAttr('disabled');
});
$("#editform").validate({
    rules: {
        {{ form.name.name }}: {
            required: true,
            remote: {
                url: "{% url 'jobsname' %}"
            },
        },
        {{ form.retention.name }}_0: {
            required: true,
            digits: true,
            min: 1,
        },
    },
    messages: {
        {{ form.name.name }}: {
          required: "You need to provide a Backup Job name.",
          remote: "Backup Job name already exist. Please choose another one.",
        },
        {{ form.retention.name }}_0: {
          required: "You need to provide a retention period.",
          digits: "Retention is a positive integer. Please correct."
        }
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
// TODO od tego miejsca add/edit .js jest takie samo - do przewalenia do zbiorczego pliku
$(".timepicker").timepicker({
    showInputs: false,
    minuteStep: 1,
    showMeridian: false,
});
$(function(){
    $('#id_backupsch').change(function(){
        if ($('#id_backupsch').val() == 'c1'){
            $('#divrepeat').show();
            $('#divweekdays').hide();
            $('#divmonthdays').hide();
        } else
        if ($('#id_backupsch').val() == 'c2'){
            $('#divrepeat').hide();
            $('#divweekdays').show();
            $('#divmonthdays').hide();
        } else
        if ($('#id_backupsch').val() == 'c3'){
            $('#divrepeat').hide();
            $('#divweekdays').hide();
            $('#divmonthdays').show();
        }
    });
});
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
$(".dropdown-menu li a").click(function(){
  var selText = $(this).text();
  var selValue = this.id;
  $('#{{ form.retention.id_for_label }}-button').html(selText+' <span class="caret"></span>');
  $('#{{ form.retention.id_for_label }}-interval').val(selValue);
});
</script>
