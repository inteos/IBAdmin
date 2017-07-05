<!-- page script -->
<script>
$(function () {
  var table = $("#clientslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'clientsdefineddata' %}",
    "language": {
      "emptyTable": "No Clients defined"
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientaddress(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "width": "128px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderosbadge(data)} }, // OS
      { "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderclientcluster(data[0],data[1])} },
      { "width": "64px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderstatus(data)} }, // Status
      { "width": "128px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var binf = btn + 'onclick="location.href=\'{% url 'clientsinfo_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var bres = btn + 'onclick="location.href=\'{% url 'restoreclient_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
          var bedi = btn + 'onclick="location.href=\'{% url 'clientsedit_rel' %}'+data[0]+'/\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
          var bdel = btn + 'data-toggle="modal" data-target="#deleteclientconfirm" data-name="'+data[0]+'" data-url="{% url 'clientsdelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          var ret = binf + bres + bedi;
          if (data[1] != 'Yes'){
            ret += bdel;
          };
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
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
            $('#deleteclientconfirmprogress').modal('hide');
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
        $('#deleteclientconfirmrunning').modal('show');
      } else
      if (data['status'] == 3) {
        $('#deleteclientconfirmalias').modal('show');
      } else
      if (data['status'] == 4) {
        $('#deleteclientconfirmcluster').modal('show');
      } else
      if (data['status'] == 2) {
        table.ajax.reload( null, false ); // user paging is not reset on reload
        taskid = data['taskid'];
        $('#deleteclientconfirmprogress').modal('show');
        rpintervalId = setInterval(refreshProgress, 1000);
        $('#deleteclientconfirmprogress').on('hide.bs.modal', function (event) {
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
{% include 'widgets/confirmmodal1.js' with selector='#deleteclientconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='clients.defined' %}