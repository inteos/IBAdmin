<script>
  function jobstatusnrRefresh(){
    function onDataReceived(data) {
      if (data.jobsrunning > 0){
        $('#jobsmenutoprunning').html(data.jobsrunning);
        $('#jobsmenutopqueued').hide();
        $('#jobsmenutopangle').hide();
        $('#jobsmenutoprunning').show();
      } else
      if (data.jobsqueued > 0){
        $('#jobsmenutoprunning').html(data.jobsqueued);
        $('#jobsmenutopangle').hide();
        $('#jobsmenutoprunning').hide();
        $('#jobsmenutopqueued').show();
      } else {
        $('#jobsmenutoprunning').hide();
        $('#jobsmenutopqueued').hide();
        $('#jobsmenutopangle').show();
      };
      if (data.jobsrunning > 0){
        $('#jobsmenurunningnr').html(data.jobsrunning);
        $('#jobsmenurunning').show();
      } else {
        $('#jobsmenurunning').hide();
      };
      if (data.jobsqueued > 0){
        $('#jobsmenuqueuednr').html(data.jobsqueued);
        $('#jobsmenuqueued').show();
      } else {
        $('#jobsmenuqueued').hide();
      };
      if (data.jobssuccess > 0){
        $('#jobsmenusuccess').html(data.jobssuccess);
        $('#jobsmenusuccess').show();
      } else {
        $('#jobsmenusuccess').hide();
      };
      if (data.jobserror > 0){
        $('#jobsmenuerror').html(data.jobserror);
        $('#jobsmenuerror').show();
      } else {
        $('#jobsmenuerror').hide();
      };
      if (data.jobswarning > 0){
        $('#jobsmenuwarning').html(data.jobswarning);
        $('#jobsmenuwarning').show();
      } else {
        $('#jobsmenuwarning').hide();
      };
    };
    $.ajax({
      url: '{% url 'jobsstatusnr' %}',
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
  function taskstatuswidgetRefresh(){
    $("#taskstatuswidget").load('{% url 'tasksstatuswidget' %}');
    function onDataReceived(data) {
      if (data.tasksrunningnr > 0){
        $('#taskstatuswidgetnr').html(data.tasksrunningnr);
        $('#taskstatuswidgetnr').show();
        $('#taskstatuswidgetinfo').html('You have '+data.tasksrunningnr+' tasks running')
      } else {
        $('#taskstatuswidgetnr').html('');
        $('#taskstatuswidgetnr').hide();
        $('#taskstatuswidgetinfo').html('No tasks running')
      };
    };
    $.ajax({
      url: '{% url 'tasksstatusnr' %}',
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
{% if jobstatuswidgetRefresh %}
  function jobstatuswidgetRefresh(){
    $("#jobstatuswidget").load('{% url 'jobsstatuswidget' %}');
  };
{% endif %}
{% if servicestatuswidgetRefresh %}
  function servicestatuswidgetRefresh(){
    $("#servicestatuswidget").load('/servicestatuswidget');
  };
{% endif %}
  function autoRefresh(){
    jobstatusnrRefresh();
    taskstatuswidgetRefresh();
{% if jobstatuswidgetRefresh %}
    jobstatuswidgetRefresh();
{% endif %}
{% if servicestatuswidgetRefresh %}
    servicestatuswidgetRefresh();
{% endif %}
  };
  $(function(){
    setInterval(autoRefresh, 60000);
  });
</script>
