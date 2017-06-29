<!-- page script -->
<script>
$(function () {
  var table = $("#messages").DataTable({
    "serverSide": true,
    "ajax": "{% url 'systemmessagesdata' %}",
    "language": {
      "emptyTable": "No Messages available."
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "130px", "sClass": "vertical-align text-center", },
      { "sClass": "vertical-align", },
    ],
    "initComplete": function(settings, json) {
        $("#messagesloading").hide();
    },
    'fnDrawCallback': function () {
      var rows = this.fnGetData();
      if (rows.length === 0) {
        $('#clearbutton').addClass('disabled');
      } else {
        $('#clearbutton').removeClass('disabled');
      };
    },
  });
  $('#clearbutton').on('click', function () {
    $('#runningbadge').show();
    var button = $(this);
    var url = button.data('url');
    function onCleardata(data){
      table.ajax.reload( null, false );
      $('#runningbadge').hide();
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onCleardata,
    });
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
  {% include "widgets/refreshbutton.js" %}
});
</script>