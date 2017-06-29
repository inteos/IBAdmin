  $('#{{ id|default:'listrefresh' }}').click(function(){ {{ table|default:'table' }}.ajax.reload(null, false); });
