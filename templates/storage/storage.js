<!-- page script -->
<script>
{% if perms.jobs.view_jobs %}
$(function () {
  var table = $("#jobshistory").DataTable({
    "serverSide": true,
    "ajax": "{% url 'storagehistorydata' Storage.Name %}",
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
      { "width": "50px", "sClass": "vertical-align text-center", "orderable": false, "render": function (data,type,row){ return renderbadge(data)} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlabel(data)} },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var ret = '';
          if (data[3] == 'R' || data[3] == 'C'){
{% if perms.jobs.status_jobs %}
            ret += btn + 'onclick="location.href=\'{% url 'jobsstatus_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
{% endif %}
          } else {
{% if perms.jobs.view_jobs %}
            ret += btn + 'onclick="location.href=\'{% url 'jobslog_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
{% endif %}
          };
{% if perms.jobs.cancel_jobs %}
          if (data[3] == 'R' || data[3] == 'C'){
            ret += btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle" data-toggle="tooltip" data-original-title="Cancel"></i></button>\n';
          };
{% endif %}
          if (data[3] == 'R'){
{% if perms.jobs.stop_jobs %}
            ret += btn + 'data-toggle="modal" data-target="#stopjobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidstop_rel' %}"><i class="fa fa-pause" data-toggle="tooltip" data-original-title="Stop"></i></button>\n';
{% endif %}
          } else
          if (data[3] != 'C') {
{% if perms.jobs.restore_jobs %}
            if (data[2] == 'B'){
              ret += btn + 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
            }
{% endif %}
{% if perms.jobs.delete_jobs %}
            ret += btn + 'data-toggle="modal" data-target="#deletejobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsiddelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
{% endif %}
          };
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton, #deletejobidconfirmbutton' %}
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm, #deletejobidconfirm' %}
});
{% endif %}

{% include "widgets/labelconfirm.js" %}
{% include 'widgets/confirmmodal1a.js' with selector='#labelconfirm' %}

</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.info' %}