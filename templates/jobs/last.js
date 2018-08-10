<!-- page script -->
<script>
$(function () {
  var table = $("#jobslast").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobslastdata' %}",
    "language": {
      "emptyTable": "No last Jobs"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderstatuslabel(data[0], data[1])} },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var blog = btn + 'onclick="location.href=\'{% url 'jobslog_rel' %}'+data[0]+'\';"><i class="fa fa-info-circle"></i></button>\n';
          var ret = '<div class="btn-group">' + blog;
          if (data[2] == 'B'){
            var bres = btn;
            if (data[3] == 'T' || data[3] == 'I'){
                bres += 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'\';"><i class="fa fa-cloud-upload"></i></button>\n';
              } else {
                bres += 'data-toggle="modal" data-target="#restartjobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidrestart_rel' %}"><i class="fa fa-refresh" data-toggle="tooltip" data-original-title="Restart"></i></button>\n';
              }
            ret += bres;
          }
          var bdel = btn + 'data-toggle="modal" data-target="#deletejobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsiddelete_rel' %}"><i class="fa fa-trash"></i></button>\n';
          ret +=  bdel;
          ret += '</div>';
          return ret;
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#deletejobidconfirmbutton' %}
{% include "widgets/confirmbuttonhref.js" with selector='#restartjobidconfirmbutton' %}
});
{% include "widgets/confirmmodal2.js" with selector='#restartjobidconfirm, #deletejobidconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.last' %}