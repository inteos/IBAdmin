<!-- page script -->
<script>
$(function () {
  var table = $("#jobslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobsdefineddata' %}",
    "language": {
      "emptyTable": "No Jobs defined"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
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
  $('#deletejobconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    var taskid = 0;
    var rpintervalId;
    function closeProgress(){
      clearInterval(rpintervalId);
      $('#deletejobconfirmprogress').on('hidden.bs.modal', function (){
        $('#taskprogress').css('width','0%').attr('aria-valuenow',0);
        $('#taskprogress').html("0%");
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
            $('#deletejobconfirmprogress').modal('hide');
          }
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
});
{% include 'widgets/confirmmodal1.js' with selector='#runjobconfirm, #deletejobconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.defined' %}