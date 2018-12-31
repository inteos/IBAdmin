<!-- page script -->
<script>
  $(function () {
    var datestr = '';
    var table = $("#jobshistory").DataTable({
      "serverSide": true,
      "ajax": {
        "url": "{% url 'restorehistorydata' Job.Name %}",
        "data": function(d) {
            d.datefilter = datestr;
        },
      },
      "language": {
        "emptyTable": "No Jobs run yet"
      },
      "order": [[ 1, 'desc' ]],
      "bAutoWidth": false,
      "columns": [
        { "width": "32px", "orderable": false, "sClass": "vertical-align text-center", //<!-- 32px for every button -->
          "render": function (data,type,row){
            return '<button class="btn btn-sm btn-default jobidselect" type="button" data-jobid="'+data+'"><i class="fa fa-cloud-upload"></i></button>\n';
          },
        },
        { "width": "45px", "sClass": "vertical-align text-center" },
        { "sClass": "vertical-align"},
        { "width": "50px", "sClass": "vertical-align text-center", "orderable": false, "render": function (data,type,row){ return renderbadge(data)} },
        { "sClass": "vertical-align" },
        { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      ],
    });
    var calendar = $('#datepiker').datepicker({
      todayHighlight: true,
      maxViewMode: 1,
      startDate: "{{ jobmin|date:'d/m/Y' }}",
      endDate: "{{ jobmax|date:'d/m/Y' }}",
      toggleActive: true,
      format: "dd/mm/yyyy",
    });
    calendar.on('changeDate', function (e) {
      var date = e.date;
      if (date){
        var month = date.getMonth() + 1
        datestr = date.getDate()+'-'+month+'-'+date.getFullYear();
      } else {
        datestr = '';
      };
      table.draw();
    });
    function updateJobidselect(e, settings){
      $('.jobidselect').on('click', function (e){
        var jobid = $(this).data('jobid');
        $('#Two').collapse('toggle');
        $('#Two').on('hidden.bs.collapse', function () {
            url = "{% url 'restorejobid_rel' %}" + jobid + '/';
            location.href = url;
        });
      });
    };
    table.on('draw', updateJobidselect);
    $('.jobselected').on('click', function (e){
      var client = $(this).data('client');
      $('#Two').collapse('toggle');
      $('#Two').on('hidden.bs.collapse', function () {
          url = "{% url 'restoreclient_rel' %}" + client + '/';
          location.href = url;
      });
    });
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='restore.job' %}
