<!-- page script -->
<script>
$(function () {
  var table = $("#jobsdefined").DataTable({
    "serverSide": true,
    "ajax": "{% url 'clientsinfodefineddata' Client.Name %}",
    "language": {
      "emptyTable": "No Jobs defined"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderdatadis(data[0],data[1])} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderdatana(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderstoragelink(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "width": "160px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var binf = btn + 'onclick="location.href=\'{% url 'jobsinfo_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var brun = btn + 'data-toggle="modal" data-target="#runjobconfirm" data-name="'+data[0]+'" data-url="{% url 'jobsrun_rel' %}"><i class="fa fa-play" data-toggle="tooltip" data-original-title="Run"></i></button>\n';
          var bres = btn + 'onclick="location.href=\'{% url 'restorejob_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
          var bedi = btn + 'onclick="location.href=\'{% url 'jobsedit_rel' %}'+data[0]+'/\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
          var bdel = btn + 'data-toggle="modal" data-target="#deletejobconfirm" data-name="'+data[0]+'" data-url="{% url 'jobsdelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          var ret = binf;
          if (data[1] != 'Restore'){
            ret += brun;
            if (data[1] != 'Admin'){
              ret += bres;
            };
          };
          if (data[2] != 'Yes'){
            ret += bedi + bdel;
          }
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbuttonhref.js" with selector='#runjobconfirmbutton' %}
  var tablehis = $("#jobshistory").DataTable({
    "serverSide": true,
    "ajax": "{% url 'clientshistorydata' Client.Name %}",
    "language": {
      "emptyTable": "No Jobs run yet"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderdataar(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderdata(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderstatuslabel(data[0],data[1])} },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var tmp;
          if (data[3] == 'R' || data[3] == 'C'){
            tmp = '{% url 'jobsstatus_rel' %}';
          } else {
            tmp = '{% url 'jobslog_rel' %}';
          };
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var blog = btn + 'onclick="location.href=\''+tmp+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var ret = blog;
          if (data[3] == 'R' || data[3] == 'C'){
            var bcan = btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle" data-toggle="tooltip" data-original-title="Cancel"></i></button>\n';
            ret += bcan;
          };
          if (data[3] == 'R'){
            var bstp = btn + 'data-toggle="modal" data-target="#stopjobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidstop_rel' %}"><i class="fa fa-pause" data-toggle="tooltip" data-original-title="Stop"></i></button>\n';
            ret += bstp;
          } else if (data[3] != 'C') {
            if (data[2] == 'B'){
              var bres;
              if (data[3] == 'T' || data[3] == 'I'){
                bres = btn + 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
              } else {
                bres = btn + 'data-toggle="modal" data-target="#restartjobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidrestart_rel' %}"><i class="fa fa-refresh" data-toggle="tooltip" data-original-title="Restart"></i></button>\n';
              };
              ret += bres;
            }
            var bdel = btn + 'data-toggle="modal" data-target="#deletejobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsiddelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
            ret +=  bdel;
          };
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
    tablehis.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" with id='jobhistoryrefresh' table='tablehis' %}
  function closeProgress(){
    clearInterval(rpintervalId);
    $('#deletejobconfirmprogress').on('hidden.bs.modal', function (){
      $('#taskprogress').css('width','0%').attr('aria-valuenow',0);
      $('#taskprogress').html("0%");
      $('#deletejobconfirmprogress').removeClass('modal-danger');
      $('#deleteclientconfirmprogress').removeClass('modal-danger');
      tablehis.ajax.reload( null, false ); // user paging is not reset on reload
    });
  };
  $('#deletejobconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    var taskid = 0;
    var rpintervalId;
    function refreshProgress(){
      $.ajax({
        url: '{% url 'tasksprogress_rel' %}' + taskid + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
          $('#taskprogress').css('width',data[1]).attr('aria-valuenow',data[0]);
          $('#taskprogress').html(data[1]);
          if (data[0] == 100){
            $('#deletejobconfirmprogress').modal('hide');
          }
          if (data[2] == 'E' || data[2] == 'C'){
            $('#deletejobconfirmprogress').addClass('modal-danger');
            $('#deletejobconfirmprogress').find('.modal-header').find('h4').html('Failed...')
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
        table.ajax.reload( null, false ); // user paging is not reset on reload
      } else
      if (data['status'] == 1) {
        $('#deletejobconfirmrunning').modal('show');
      } else
      if (data['status'] == 2) {
        table.ajax.reload( null, false ); // user paging is not reset on reload
        taskid = data['taskid'];
        $('#deletejobconfirmprogress').modal('show');
        rpintervalId = setInterval(refreshProgress, 1000);
        $('#deletejobconfirmprogress').on('hide.bs.modal', function (event) {
          closeProgress();
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
  $('#deleteclientconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    var taskid = 0;
    var rpintervalId;
    function refreshProgress(){
      $.ajax({
        url: '{% url 'tasksprogress_rel' %}' + taskid + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
          $('#taskprogress').css('width',data[1]).attr('aria-valuenow',data[0]);
          $('#taskprogress').html(data[1]);
          if (data[0] == 100){
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
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton, #deletejobidconfirmbutton' table='tablehis' %}
{% include "widgets/confirmbuttonhref.js" with selector='#restartjobidconfirmbutton' %}
});
{% include 'widgets/confirmmodal1.js' with selector='#deleteclientconfirm, #runjobconfirm, #deletejobconfirm' %}
{% include "widgets/confirmmodal2.js" with selector='#restartjobidconfirm, #deletejobidconfirm, #canceljobconfirm, #stopjobconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='clients.info' %}