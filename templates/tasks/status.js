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
        if (data[4] != 'N' && data[4] != 'R'){
          clearInterval(rpintervalId);
          $('#listrefresh').hide()
          $('#taskdivprogress').hide()
          $('#taskcancelbutton').hide()
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
  {% include "widgets/confirmmodal2t.js" with selector='#cancelconfirm' %}
  $('#cancelconfirmbutton').on('click', function () {
    var button = $(this);
    button.button('loading');
    var url = button.data('url');
    function onDataReceived(data) {
        button.button('Done...');
        var modal = button.closest('.modal')
        modal.modal('hide');
        refreshStatus();
    };
    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        success: onDataReceived,
    });
  });
{% endif %}
  $('#taskdeletebutton').on('click', function () {
    $.ajax({
        url: "{% url 'tasksdelete' Task.taskid %}",
        type: "GET",
        dataType: "json",
        success: function(){
            location.href="{% url 'taskslist' %}";
        },
    });
  });
  //SLIMSCROLL FOR log box
  $('#tasklog').slimScroll({
    height: '250px'
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='task.status' %}