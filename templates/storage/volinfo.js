<!-- page script -->
<script>
$(function () {
  var table = $("#jobshistory").DataTable({
    "serverSide": true,
    "ajax": "{% url 'volumeshistorydata' Volume.volumename %}",
    "language": {
      "emptyTable": "No Jobs stored yet."
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
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
              var bres = btn + 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
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
{% include "widgets/refreshbutton.js" %}
  var tablelog = $("#volumeloghistory").DataTable({
    "serverSide": true,
    "ajax": "{% url 'volumeslogdata' Volume.volumename %}",
    "pageLength": 25,
    "language": {
      "emptyTable": "No volume history found."
    },
    "order": [[ 0, 'asc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "110px", "sClass": "vertical-align text-center" },    // time
      { "width": "30px", "sClass": "vertical-align text-center" },    // jobid
      { "orderable": false, "sClass": "vertical-align" },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
    tablelog.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
  function setupButtons(volstatus){
    if (volstatus == 'Append'){
        $('#volclosebutton').show()
        $('#volopenbutton').hide()
        $('#volrecyclebutton').show()
        $('#voldeletebutton').hide()
    } else
    if (volstatus == 'Purged' || volstatus == 'Recycle'){
        $('#volclosebutton').hide()
        $('#volopenbutton').hide()
        $('#volrecyclebutton').hide()
        $('#voldeletebutton').show()
    } else
    if (volstatus == 'Used'){
        $('#volclosebutton').hide()
        $('#volopenbutton').show()
        $('#volrecyclebutton').show()
        $('#voldeletebutton').show()
    } else
    if (volstatus == 'Full' || volstatus == 'Error'){
        $('#volclosebutton').hide()
        $('#volopenbutton').hide()
        $('#volrecyclebutton').show()
        $('#voldeletebutton').show()
    } else {
        $('#volclosebutton').hide()
        $('#volopenbutton').hide()
        $('#volrecyclebutton').hide()
        $('#voldeletebutton').hide()
    };
  };
  setupButtons('{{ Volume.volstatus }}');
{% include "widgets/refreshbutton.js" with id='volumelogrefresh' table='tablelog' %}
  $('#volusedconfirmbutton').on('click', function () {
    var button = $(this)
    var text = button.text()
    button.button('loading')
    var url = button.data('url')
    function onDataReceived(data) {
      button.button('Done...');
      button.closest('.modal').modal('hide');
      $('td.volstatus').html(rendervolstatus('Used'));
      setupButtons('Used');
      tablelog.ajax.reload( null, false );
      button.text(text);
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  $('#volopenconfirmbutton').on('click', function () {
    var button = $(this)
    var text = button.text()
    button.button('loading')
    var url = button.data('url')
    function onDataReceived(data) {
      button.button('Done...');
      button.closest('.modal').modal('hide');
      $('td.volstatus').html(rendervolstatus('Append'));
      setupButtons('Append');
      tablelog.ajax.reload( null, false );
      button.text(text);
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  $('#volpurgeconfirmbutton').on('click', function () {
    var button = $(this)
    var text = button.text()
    button.button('loading')
    var url = button.data('url')
    function onDataReceived(data) {
      button.button('Done...');
      button.closest('.modal').modal('hide');
      $('td.volstatus').html(rendervolstatus('Purged'));
      setupButtons('Purged');
      table.ajax.reload( null, false );
      tablelog.ajax.reload( null, false );
      button.text(text);
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  $('#voldeleteconfirmbutton').on('click', function () {
    var button = $(this)
    button.button('loading')
    var url = button.data('url')
    function onDataReceived(data) {
      button.button('Done...');
      location.href = "{% url 'storagevolumes' %}";
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton, #deletejobidconfirmbutton' %}
});
{% include 'widgets/confirmmodal1.js' with selector='#volusedconfirm, #volpurgeconfirm, #volopenconfirm, #voldeleteconfirm' %}
{% include "widgets/confirmmodal2.js" with selector='#deletejobidconfirm, #canceljobconfirm, #stopjobconfirm' %}
{% include "widgets/commenteditname.js" %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}