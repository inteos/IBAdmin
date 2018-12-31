<!-- page script -->
<script>
$(function () {
  var table = $("#jobsqueued").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobsqueueddata' %}",
    "language": {
      "emptyTable": "No Jobs queued."
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderbadge(data)} },
      { "sClass": "vertical-align" },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function(data,type,row){ return renderbadge(data)} },
      { "width": "64px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var url = '{% url 'jobsstatus_rel' %}';
          var bsta = btn + 'onclick="location.href=\''+url+data[0]+'\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var bcan = btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle" data-toggle="tooltip" data-original-title="Cancel"></i></button>\n';
          var ret = '<div class="btn-group">' + bsta + bcan + '</div>';
          return ret;
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton' %}
});
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.queued' %}