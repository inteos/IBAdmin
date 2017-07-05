<script>
{% if Job.Type == 'R' %}
  $(function () {
    $("#jobrestorefiles").DataTable({
      "serverSide": true,
      "ajax": "{% url 'jobsrestorefilesdata' Job.JobId %}",
      "language": {
        "emptyTable": "No files restored found in logs."
      },
      "pageLength": 25,
      "ordering": false,
      "bAutoWidth": false,
      "columns": [
        { "orderable": false, "width": "50px", "sClass": "vertical-align text-center", },
        { "orderable": false, "sClass": "vertical-align text-center" },
        { "orderable": false, "sClass": "vertical-align text-center" },
        { "orderable": false, "sClass": "vertical-align" },
        { "orderable": false, "sClass": "vertical-align text-center" },
        { "orderable": false, "sClass": "vertical-align" },
      ],
    });
  });
{% endif %}
{% if Job.Type != 'D' and Job.Type != 'R' %}
  $(function () {
    $("#jobbackupfiles").DataTable({
      "serverSide": true,
      "ajax": "{% url 'jobsbackupfilesdata' Job.JobId %}",
      "language": {
        "emptyTable": "No files in backup."
      },
      "pageLength": 25,
      "order": [3, "asc"],
      "bAutoWidth": false,
      "columns": [
        { "orderable": false, "width": "50px", "sClass": "vertical-align text-center", },
        { "orderable": false, "sClass": "vertical-align text-center" },
        { "orderable": false, "sClass": "vertical-align" },
        { "sClass": "vertical-align" },
      ],
    });
  });
{% endif %}
{% include "widgets/confirmbuttonhref.js" with selector='#restartjobidconfirmbutton, #restartijobidconfirmbutton' %}
$('#deletejobidconfirmbutton').on('click', function () {
  var button = $(this);
  button.button('loading');
  var url = button.data('url');
  function onDataReceived(data) {
    button.button('Done...');
    location.href="{% url 'jobsinfo' Job.Name %}";
  };
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
{% include "widgets/confirmmodal2.js" with selector='#restartjobidconfirm, #restartijobidconfirm, #canceljobconfirm, #stopjobconfirm, #deletejobidconfirm' %}
{% include "widgets/commenteditjobid.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.log' %}