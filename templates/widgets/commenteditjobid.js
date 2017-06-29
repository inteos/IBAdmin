$(document).ready(function () {
  $('#{{ id|default:'commentedit' }}').on('show.bs.modal', function (event) { // id of the modal with event
    var button = $(event.relatedTarget); // Button that triggered the modal
    var name = button.data('name'); // Extract info from data-* attributes
    var jobid = button.data('jobid'); // Extract info from data-* attributes
    var title = 'Comment on Job "' + name + '" for JobId: ' + jobid;
    // Update the modal's content.
    var modal = $(this);
    modal.find('.modal-title').text(title);
    // And if you wish to pass the productid to modal's 'Yes' button for further processing
    var linkdata = '{% url 'jobsidcomment_rel' %}' + jobid + '/';
    modal.find('button.btn-success').val(linkdata);
    function onDataReceived(data) {
      var content = '<textarea name="commenttext" class="form-control" rows="3" placeholder="Comment empty ...">'+data['comment']+'</textarea>';
      modal.find('.box-body').html(content);
    };
    $.ajax({
      url: "{% url 'jobsidcomment_rel' %}" + jobid + "/",
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
      url: "{% url 'jobsidcomment' Job.JobId %}", //this is the submit URL
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
