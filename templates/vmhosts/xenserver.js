<!-- page script -->
<script>
$(function () {
  var table = $("#clientslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'vmsxenserverdefineddata' %}",
    "language": {
      "emptyTable": "No XenServer Hosts defined"
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientaddress(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderdepartmentlabel(data);} },
      { "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderclientcluster(data[0],data[1])} },
      { "width": "64px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderstatus(data)} }, // Status
      { "width": "160px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var ret = '';
{% if perms.virtual.list_xen %}
          ret += '<button class="btn btn-sm btn-default displayVM" type="button" data-name="'+data[0]+'"><i class="fa fa-cubes" data-toggle="tooltip" data-original-title="VM Guests list"></i></button>\n';
{% endif %}
{% if perms.clients.view_clients %}
          ret += btn + 'onclick="location.href=\'{% url 'clientsinfo_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
{% endif %}
{% if perms.clients.restore_clients %}
          ret += btn + 'onclick="location.href=\'{% url 'restoreclient_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
{% endif %}
{% if perms.clients.change_clients %}
          ret += btn + 'onclick="location.href=\'{% url 'clientsedit_rel' %}'+data[0]+'/?b={% url 'vmsxenserverdefined' %}\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
{% endif %}
{% if perms.clients.delete_clients %}
          if (data[1] != 'Yes'){
            ret += btn + 'data-toggle="modal" data-target="#deleteclientconfirm" data-name="'+data[0]+'" data-url="{% url 'clientsdelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          }
{% endif %}
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
  function guestaddbutton(data,type,text){
    var btn = '<div class="pull-right box-tools"><button class="btn btn-sm btn-default" type="button"';
    btn += 'onclick="location.href=\'{% url 'jobsaddproxmox' %}?c='+encodeURIComponent(data[1])+'&'+type+'='+encodeURIComponent(data[0])+'\';"';
    return data[0] + btn + '><i class="fa fa-plus" data-toggle="tooltip" data-original-title="'+text+'"></i></button></div>\n';
  }
  var tableguests = $("#guestslist").DataTable({
    "data": [],
    "language": {
      "emptyTable": "No XenServer Guests available"
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align",
        "render": function (data,type,row){
          return guestaddbutton(data,'v','Add VMname');
        },
      },
      { "sClass": "vertical-align",
        "render": function (data,type,row){
          return guestaddbutton(data,'i','Add VMID');
        },
      },
      { "width": "96px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlabel(data)} },
      { "width": "120px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return bytestext(data)} },
    ],
  });
  var ajaxguests = null;
  {% include 'widgets/onErrorReceived.js' %}
  function loadguests(name){
    tableguests.context[0].oLanguage.sEmptyTable = "No XenServer Guests available";
    tableguests.clear();
    $('#xenserverguestlist').removeClass('box-danger').addClass('box-primary');
    $('#vmguestsloading').show();
    $('#guestsrefresh').prop("disabled", true);
    ajaxguests = $.ajax({
        url: "{% url 'vmsxenservervmlist_rel' %}" + name + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
            tableguests.rows.add(data['data']);
            if (data['err'] != null){
                $('#xenserverguestlist').removeClass('box-primary').addClass('box-danger');
                switch (data['err']){
                case 1:
                    tableguests.context[0].oLanguage.sEmptyTable = "Cannot connect to XenServer Host."
                    break;
                case 2:
                    tableguests.context[0].oLanguage.sEmptyTable = "No XenServer Plugin installed on Host."
                    break;
                }
            }
            tableguests.draw();
            $('#vmguestsloading').hide();
            ajaxguests = null;
            $('#guestsrefresh').prop("disabled", false);
        },
        error: onErrorReceived,
      });
  };
  var vmdisplayguests = '';
  $(document).on('click', '.displayVM', function () {
    var name = $(this).data('name');
    if (ajaxguests != null){
        ajaxguests.abort();
    }
    if (vmdisplayguests != name){
      if (vmdisplayguests != ''){
        $('.displayVM').removeClass('btn-info').addClass('btn-default');
        $('#xenserverguestlist').removeClass('box-danger').addClass('box-primary');
      };
      vmdisplayguests = name;
      $(this).removeClass('btn-default').addClass('btn-info');
      loadguests(name);
      $('#One').collapse('show');
    } else {
      $('#One').collapse('hide');
      $('#vmguestsloading').hide();
      $('.displayVM').removeClass('btn-info').addClass('btn-default');
      $('#xenserverguestlist').removeClass('box-danger').addClass('box-primary');
      vmdisplayguests = '';
    };
  });
  $('#guestsrefresh').on("click", function(){
    if (vmdisplayguests != ''){
        loadproxmoxguests(vmdisplayguests);
    }
  });
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
    {% include 'widgets/onErrorReceivedbutton.js' %}
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
      error: onErrorReceived,
    });
  });
});
{% include 'widgets/confirmmodal1.js' with selector='#deleteclientconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='vmhosts.xenserver' %}