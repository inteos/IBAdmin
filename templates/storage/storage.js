<!-- page script -->
<script>
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
      { "width": "50px", "sClass": "vertical-align text-center", "orderable": false, "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
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
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/labelconfirm.js" %}
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton, #deletejobidconfirmbutton' %}
});
{% include 'widgets/confirmmodal1a.js' with selector='#labelconfirm' %}
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm, #deletejobidconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.info' %}