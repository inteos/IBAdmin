<!-- page script -->
<script>
$(function(){
  function refresh(){
    $("#storagedevices").load('{% url 'storagestatusdevices' Storage.Name %}', function() { $("#storagestatusloading").hide(); });
    $("#statusheader").load('{% url 'storagestatusheader' Storage.Name %}');
  };
  $('#{{ id|default:'listrefresh' }}').on('click', function(){
    $("#storagestatusloading").show();
    refresh();
  });
  $(document).on('click', '[data-dev="devena"]', function () {
    function onDataReceived(data) {
        $("#storagestatusloading").show();
        refresh();
    };
    var button = $(this);
    var name = button.data('name');
    var status = button.data('status');
    var url = "{% url 'storagedisabledevice_rel' Storage.Name %}" + name + '/';
    if (status == 'Disabled'){
        url = "{% url 'storageenabledevice_rel' Storage.Name %}" + name + '/';
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  setInterval(refresh, 60000);
  refresh();
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.status' %}