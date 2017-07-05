<!-- page script -->
<script>
$(function(){
  function refresh(){
    function onDataReceived(data) {
      dedupengine = data['dedupengine'];
      for (var key in dedupengine){
        val = dedupengine[key];
        $("#"+key).text(val);
      };
      dedupcontainers = data['dedupcontainers'];
      for (var i=0; i < dedupcontainers.length; i++){
        var block = dedupcontainers[i];
        var bs = block['block_size'];
        $("#"+bs+"_allocated_size").text(block['allocated_size']);
        $("#"+bs+"_used_size").text(block['used_size']);
        var pct = block['used_percent'];
        var color = 'bg-purple';
        if (pct < 31){
            color = 'bg-orange';
        } else
        if (pct < 91){
            color = 'bg-green'
        };
        $("#"+bs+"_used_percent").html('<span class="badge '+color+'">'+pct+'%</span>');
        $("#"+bs+"_pct").css('width',pct+'%').attr('aria-valuenow',pct)
      };
      $("#storagestatusloading").hide();
    };
    $.ajax({
      url: "{% url 'storagededupdata' Storage.Name %}",
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };
  $('#{{ id|default:'listrefresh' }}').on('click', function(){
    $("#storagestatusloading").show();
    refresh();
  });
  setInterval( refresh, 300000 );
  refresh();
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.dedup' %}