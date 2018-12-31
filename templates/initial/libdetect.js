<script>
$(function () {
  $('input').iCheck({
    //Initialize iCheck - boxes
    checkboxClass: 'icheckbox_square-blue',
    radioClass: 'iradio_square-blue',
  });
});
$("#initsetup").validate({
  submitHandler: function(form) {
    $('#initialwait').show();
    form.submit();
  },
});
var intervalId;
function refreshProgress(){
  $.ajax({
    url: "{% url 'initialtaskprogress' %}",
    type: "POST",
    data: {
      csrfmiddlewaretoken: '{{ csrf_token }}',
      taskid: {{ form.taskid.value }},
    },
    dataType: "json",
    success: function(data){
      var progress = data[0]
      $('#taskprogress').css('width',data[1]).attr('aria-valuenow',progress);
      $('#taskprogress').html(data[1]);
      $('#operationlog').html(data[2]);
      var status = data[3]
      if (status == 'E' || progress == 100){
        $('#okbutton').removeAttr('disabled');
        if (status == 'F'){
            $('#progressbox').removeClass('box-warning').addClass('box-success');
            $('#header').html('<i class="fa fa-check-circle"></i> Library {{ storage }} detection done.');
        } else {
            $('#progressbox').removeClass('box-warning').addClass('box-danger');
            $('#header').html('<i class="fa fa-times-circle"></i> Library {{ storage }} detection failed.');
        }
        clearInterval(intervalId);
      }
    },
  });
};
$(function(){
  refreshProgress();
  intervalId = setInterval(refreshProgress, 1000);
  $('.alert').delay(60000).hide();
});
</script>
