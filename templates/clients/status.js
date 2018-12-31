<!-- page script -->
<script>
$(function () {
  var table = $("#statusrunning").DataTable({
    "serverSide": true,
    "ajax": "{% url 'clientsstatusrunning' Client.Name %}",
    "language": {
      "emptyTable": "No Jobs are running"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderbadge(data)} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytessectext(data)}  },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var bsta = btn + 'onclick="location.href=\'{% url 'jobsstatus_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var bcan = btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle" data-toggle="tooltip" data-original-title="Cancel"></i></button>\n';
          var bstp = btn + 'data-toggle="modal" data-target="#stopjobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidstop_rel' %}"><i class="fa fa-pause" data-toggle="tooltip" data-original-title="Stop"></i></button>\n';
          var ret = '<div class="btn-group">' + bsta + bcan + bstp + '</div>';
          return ret;
        },
      },
    ],
  });
  $('#{{ id|default:'listrefresh' }}').on('click', function(){
    $("#clientstatusloading").show();
    table.ajax.reload(null, false);
    $("#statusheader").load('{% url 'clientsstatusheader' Client.Name %}', function() { $("#clientstatusloading").hide(); });
  });
  setInterval( function () {
    $("#statusheader").load('{% url 'clientsstatusheader' Client.Name %}');
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
  $('#deleteclientconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    var taskid = 0;
    var rpintervalId;
    function closeProgress(){
      clearInterval(rpintervalId);
      $('#deleteclientconfirmprogress').on('hidden.bs.modal', function (){
        $('#taskprogress').css('width','0%').attr('aria-valuenow',0);
        $('#taskprogress').html("0%");
        $('#deleteclientconfirmprogress').removeClass('modal-danger');
      });
    };
    function refreshProgress(){
      $.ajax({
        url: '{% url 'tasksprogress_rel' %}' + taskid + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
          $('#taskprogress').css('width',data[1]).attr('aria-valuenow',data[0]);
          $('#taskprogress').html(data[1]);
          if (data[0] == 100){
            closeProgress();
            $('#deleteclientconfirmprogress').modal('hide');
          };
          if (data[2] == 'E' || data[2] == 'C'){
            $('#deleteclientconfirmprogress').addClass('modal-danger');
            $('#deleteclientconfirmprogress').find('.modal-header').find('h4').html('Failed...')
            closeProgress();
          };
        },
      });
    };
    function onDataReceived(data) {
      button.button('Done...');
      var modal = button.closest('.modal')
      modal.modal('hide');
      if (data['status'] == 0) {
        location.href="{% url 'clientsdefined' %}";
      } else
      if (data['status'] == 1) {
        $('#deleteclientconfirmrunning').modal('show');
      } else
      if (data['status'] == 3) {
        $('#deleteclientconfirmalias').modal('show');
      } else
      if (data['status'] == 4) {
        $('#deleteclientconfirmcluster').modal('show');
      } else
      if (data['status'] == 2) {
        taskid = data['taskid'];
        $('#deleteclientconfirmprogress').modal('show');
        rpintervalId = setInterval(refreshProgress, 1000);
        $('#deleteclientconfirmprogress').on('hide.bs.modal', function (event) {
          location.href="{% url 'clientsdefined' %}";
        });
      };
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
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton' %}
});
$(function(){
  $("#statusheader").load('{% url 'clientsstatusheader' Client.Name %}', function() { $("#clientstatusloading").hide(); });
});
{% include 'widgets/confirmmodal1.js' with selector='#deleteclientconfirm' %}
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm' %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='clients.status' %}