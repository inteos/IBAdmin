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
  setInterval( refresh, 60000 );
  refresh();
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.status' %}