<!-- page script -->
<script>
{% if Task.status in 'RN' %}
  var rpintervalId;
  function refreshStatus(){
    $.ajax({
      url: '{% url 'tasksstatusdata' Task.taskid %}',
      type: "GET",
      dataType: "json",
      success: function(data){
        $('#taskprogress').css('width',data[1]).attr('aria-valuenow',data[0]);
        $('#taskprogress').html(data[1]+' Complete');
        $('#taskendtime').html(data[2]);
        $('#tasklog').html(data[3]);
        $('#taskstatus').html(rendertaskstatusbadge(data[4], 'label'));
        if (data[4] == 'F' || data[4] == 'E'){
          clearInterval(rpintervalId);
          $('#listrefresh').hide()
          $('#taskdivprogress').hide()
          $('#taskdeletebutton').show()
        }
      },
    });
  };
  $('#listrefresh').on('click', function(){
    refreshStatus();
  });
  $(function(){
    rpintervalId = setInterval(refreshStatus, 60000);
  });
{% endif %}
  //SLIMSCROLL FOR log box
  $('#tasklog').slimScroll({
    height: '250px'
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}