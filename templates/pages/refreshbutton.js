$('#{{ id }}refresh').on('click', function(){
  $("#{{ id }}loading").show();
  fetchData{{ id }}();
});
