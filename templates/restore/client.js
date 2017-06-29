<!-- page script -->
<script>
  $(function () {
    $("#jobsdefined").DataTable({
      "language": {
        "emptyTable": "No Jobs defined"
      },
      "bAutoWidth": false,
      "order": [[ 1, "desc" ]],
      "columnDefs": [
        { "width": "32px", "orderable": false, "targets": 0 }, // <!-- 32px for every button -->
        { "width": "50px", "targets": 3 },
        { "width": "32px", "orderable": false, "targets": 5 },
      ]
    });
  });
  var fsdisplayjob = '';
  $('.displayFS').on('click', function (e){
    var jobname = $(this).data('jobname');
    if (fsdisplayjob!=jobname){
      if (fsdisplayjob!=''){
        $('.displayFS').removeClass('btn-info').addClass('btn-default');
      };
      $(this).removeClass('btn-default').addClass('btn-info');
      url = "{% url 'restoredisplayfs_rel' %}" + encodeURIComponent(jobname) + '/';
      $('#blockquotefs').load(url, function() {
        $('#jdefinedtab').removeClass('col-lg-12').addClass('col-lg-9');
        $('#fsdisplaydiv').show();
      });
      fsdisplayjob = jobname;
    } else {
      $('#fsdisplaydiv').hide();
      $('#jdefinedtab').removeClass('col-lg-9').addClass('col-lg-12');
      $('.displayFS').removeClass('btn-info').addClass('btn-default');
      fsdisplayjob = '';
    };
  });
  $('.jobselect').on('click', function (e){
    var jobname = $(this).data('jobname');
    $('#One').collapse('toggle');
    $('#One').on('hidden.bs.collapse', function () {
        url = "{% url 'restorejob_rel' %}" + encodeURIComponent(jobname) + '/';
        location.href = url;
    });
  });
</script>
{% include "pages/refresh.js" %}
