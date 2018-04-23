<!-- page script -->
<script>
$(function () {
  var table = $("#jobshistory").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobshistorydata' Job.Name %}",
    "language": {
      "emptyTable": "No Jobs run yet"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
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
          }
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var blog = btn + 'onclick="location.href=\''+tmp+data[0]+'\';"><i class="fa fa-info-circle"></i></button>\n';
          var ret = '<div class="btn-group">' + blog;
          if (data[3] == 'R' || data[3] == 'C'){
            var bcan = btn + 'data-toggle="modal" data-target="#canceljobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidcancel_rel' %}"><i class="fa fa-minus-circle"></i></button>\n';
            ret += bcan;
          }
          if (data[3] == 'R'){
            var bstp = btn + 'data-toggle="modal" data-target="#stopjobconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsidstop_rel' %}"><i class="fa fa-pause"></i></button>\n';
            ret += bstp;
          } else if (data[3] != 'C') {
            if (data[2] == 'B'){
              var bres = btn + 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'\';"><i class="fa fa-cloud-upload"></i></button>\n';
              ret += bres;
            }
            var bdel = btn + 'data-toggle="modal" data-target="#deletejobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsiddelete_rel' %}"><i class="fa fa-trash"></i></button>\n';
            ret +=  bdel;
          }
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
        $('#deletejobconfirmprogress').removeClass('modal-danger');
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
            closeProgress();
            $('#deletejobconfirmprogress').modal('hide');
          };
          if (data[2] == 'E'){
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
        location.href="{% url 'jobsdefined' %}";
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
          location.href="{% url 'jobsdefined' %}";
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

{% include "widgets/confirmbutton.js" with selector='#canceljobconfirmbutton, #stopjobconfirmbutton, #deletejobidconfirmbutton' %}
{% include "widgets/confirmbuttonhref.js" with selector='#runjobconfirmbutton' %}
});
{% include "widgets/confirmmodal2.js" with selector='#canceljobconfirm, #stopjobconfirm, #deletejobidconfirm' %}
{% include 'widgets/confirmmodal1.js' with selector='#runjobconfirm, #deletejobconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.info' %}