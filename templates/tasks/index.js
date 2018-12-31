<!-- page script -->
<script>
$(function () {
  var table = $("#taskslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'taskshistorydata' %}",
    "language": {
      "emptyTable": "No Tasks run."
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "orderable": false, "sClass": "vertical-align text-center", "render": function (data,type,row){ return rendertaskprogressbar(data);} },
      { "width": "50px", "orderable": false, "sClass": "vertical-align text-center", "render": function (data,type,row){ return rendertaskstatusbadge(data, "badge");} },
      { "width": "64px", "orderable": false, "sClass": "vertical-align text-center",
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var surl = '{% url 'tasksstatus_rel' %}';
          var taskid = data[1]
          var binf = btn + 'onclick="location.href=\''+surl+taskid+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var ret = binf;
          var tname = data[2];
          var bcan = btn + 'data-toggle="modal" data-target="#cancelconfirm" data-taskid="'+taskid+'" data-name="'+tname+'" data-url="{% url 'taskscancel_rel' %}"><i class="fa fa-minus-circle"></i></button>\n';
          var bdel = btn + 'data-task="delete"  data-taskid="'+taskid+'" data-url="{% url 'tasksdelete_rel' %}"><i class="fa fa-trash"></i></button>\n';
          if (data[0] != 'N' && data[0] != 'R'){
            ret += bdel;
          } else {
            ret += bcan;
          };
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
    'fnDrawCallback': function () {
      var rows = this.fnGetData();
      if (rows.length === 0) {
        $('#clearbutton').addClass('disabled');
      } else {
        $('#clearbutton').removeClass('disabled');
      };
    },
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
  $(document).on('click', '[data-task="delete"]', function () {
    $('#runningbadge').show();
    var button = $(this);
    var taskid = button.data('taskid');
    var url = button.data('url')+taskid+'/';
    function onDataReceived(data) {
      table.ajax.reload( null, false ); // user paging is not reset on reload
      $('#runningbadge').hide();
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  $('#clearbutton').on('click', function(){
    $('#runningbadge').show();
    var button = $(this);
    var url = button.data('url');
    function onDataReceived(data) {
      table.ajax.reload( null, false ); // user paging is not reset on reload
      $('#runningbadge').hide();
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
{% include "widgets/confirmbutton.js" with selector='#cancelconfirmbutton' %}
});
{% include "widgets/confirmmodal2t.js" with selector='#cancelconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='tasks.list' %}