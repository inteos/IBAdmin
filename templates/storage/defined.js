<!-- page script -->
<script>
  $(function () {
    $("#storagelist").DataTable({
      "language": {
        "emptyTable": "No Storage defined"
      },
      "bAutoWidth": false,
      "columnDefs": [
        { "width": "64px", "targets": 5 },
        { "width": "96px", "orderable": false, "targets": 6 } // 32px for every button
      ]
    } );
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.defined' %}