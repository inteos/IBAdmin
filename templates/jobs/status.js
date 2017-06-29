<script>
function statusRefresh(){
  function onDataReceived(data) {
    if (data){ location.href='{% url 'jobslog' Job.JobId %}' }
  }
  $.ajax({
    url: "{% url 'jobsstatusfinished' Job.JobId %}",
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
  $("#datalocationwidget").load('{% url 'jobsstatusvolumes' Job.JobId %}');
  $("#joblogwidget").load('{% url 'jobsstatusjoblog' Job.JobId %}');
  $("#jobsstatusheader").load('{% url 'jobsstatusheader' Job.JobId %}', function() { $("#jobstatusloading").hide(); });
};
$('#{{ id|default:'statusrefresh' }}').on('click', function(){
  $("#jobstatusloading").show();
  statusRefresh();
});
$(function(){
  $("#jobsstatusheader").load('{% url 'jobsstatusheader' Job.JobId %}', function() { $("#jobstatusloading").hide(); });
  setInterval(statusRefresh, 60000);
});
$('#canceljobconfirmbutton, #stopjobconfirmbutton').on('click', function () {
  var button = $(this);
  var text = button.text();
  button.button('loading');
  var url = button.data('url');
  function onDataReceived(data) {
    button.button('Done...');
    var modal = button.closest('.modal')
    modal.modal('hide');
    statusRefresh();
    modal.on('hidden.bs.modal', function (){
      button.text(text);
    });
  };
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm' %}
{% include "widgets/commenteditjobid.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
