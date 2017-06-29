$(document).ready(function () {
  $('#{{ id|default:'commentedit' }}').on('show.bs.modal', function (event) { // id of the modal with event
    var button = $(event.relatedTarget); // Button that triggered the modal
    var name = button.data('name'); // Extract info from data-* attributes
    var title = 'Comment on Volume "' + name + '"';
    // Update the modal's content.
    var modal = $(this);
    modal.find('.modal-title').text(title);
    var linkdata = '{% url 'storagevolcomment_rel' %}' + name + '/';
    modal.find('button.btn-success').val(linkdata);
    function onDataReceived(data) {
      var content = '<textarea name="commenttext" class="form-control" rows="3" placeholder="Comment empty ...">'+data['comment']+'</textarea>';
      modal.find('.box-body').html(content);
    };
    $.ajax({
      url: "{% url 'storagevolcomment_rel' %}" + name + "/",
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
  $('#{{ id|default:'commentedit' }}form').on('submit', function (event){
    $btn = $('#{{ id|default:'commentedit' }}button');
    $btn.button('loading');
    $modal = $('#{{ id|default:'commentedit' }}');
    $.ajax({
      url: "{% url 'storagevolcomment' Volume.volumename %}", //this is the submit URL
        type: 'POST',
        data: $('#{{ id|default:'commentedit' }}form').serialize(),
        success: function(data){
          $btn.button('Done...');
          $modal.modal('hide');
          location.reload();
        }
    });
    return false;
  });
});
