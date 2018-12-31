{% if perms.jobs.view_job or perms.tasks.view_tasks %}
<script>
{% if perms.jobs.view_job %}
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
{% endif %}
{% if perms.tasks.view_tasks %}
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
{% endif %}
{% if perms.jobs.view_job and jobstatuswidgetRefresh %}
  function jobstatuswidgetRefresh(){
    $("#jobstatuswidget").load('{% url 'jobsstatuswidget' %}');
  };
{% endif %}
  function autoRefresh(){
{% if perms.jobs.view_job %}
    jobstatusnrRefresh();
  {% if jobstatuswidgetRefresh %}
    jobstatuswidgetRefresh();
  {% endif %}
{% endif %}
{% if perms.tasks.view_tasks %}
    taskstatuswidgetRefresh();
{% endif %}
  };
  $(function(){
    setInterval(autoRefresh, 60000);
  });
</script>
{% endif %}