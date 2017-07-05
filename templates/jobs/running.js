<!-- page script -->
<script>
$(function () {
  var table = $("#jobsrunning").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobsrunningdata' %}",
    "language": {
      "emptyTable": "No Jobs currently running."
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "sClass": "vertical-align" },
      { "width": "50px", "orderable": false, "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var url = '{% url 'jobsstatus_rel' %}';
          var bsta = btn + 'onclick="location.href=\''+url+data[0]+'\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var bcan = btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle" data-toggle="tooltip" data-original-title="Cancel"></i></button>\n';
          var bstp = btn + 'data-toggle="modal" data-target="#stopjobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidstop_rel' %}"><i class="fa fa-pause" data-toggle="tooltip" data-original-title="Stop"></i></button>\n';
          var ret = '<div class="btn-group">' + bsta + bcan + bstp + '</div>';
          return ret;
        },
      },
    ],
  }); // DUPA
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton' %}
});
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.running' %}