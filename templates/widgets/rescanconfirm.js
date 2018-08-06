$('#rescanconfirmprogress')
$('#rescanconfirmbutton').on('click', function () {
  var button = $(this);
  var text = button.text();
  button.button('loading');
  var url = button.data('url');
  var taskid = 0;
  var rpintervalId;
  function closeProgress(){
    clearInterval(rpintervalId);
    $('#rescanconfirmprogress').on('hidden.bs.modal', function (){
      $('#taskprogress').css('width','0%').attr('aria-valuenow',0);
      $('#taskprogress').html("0%");
      $('#rescanconfirmprogress').removeClass('modal-success').removeClass('modal-danger');
      $('#rescanfinishbutton').attr('disabled', true);
      $('#rescanconfirmprogress').find('.modal-header').find('h4').html('<i class="fa fa-cog fa-spin"></i> Rescanning library in progress.');
      $('#rescancog').show();
    });
  };
    function finishProcess(){
        $('#rescanmsg').hide();
        $('#rescanfinishbutton').removeAttr('disabled');
        clearInterval(rpintervalId);
    };
  function refreshProgress(){
    $.ajax({
      url: "{% url 'storagetapetaskprogress_rel' %}" + taskid + '/',
      type: "GET",
      dataType: "json",
      success: function(data){
        var progress = data[0]
        $('#taskprogress').css('width',data[1]).attr('aria-valuenow',progress);
        $('#taskprogress').html(data[1]);
        $('#operationlog').html(data[2]);
        var status = data[3]
        if (status == 'E'){
            $('#rescanconfirmprogress').addClass('modal-danger');
            $('#rescanconfirmprogress').find('.modal-header').find('h4').html('<i class="fa fa-times-circle"></i> Library {{ storage }} detection failed.');
            finishProcess();
        } else
        if (status == 'S'){
            $('#rescanconfirmprogress').addClass('modal-success');
            $('#rescanconfirmprogress').find('.modal-header').find('h4').html('<i class="fa fa-check-circle"></i> Library {{ storage }} hardware did not changed.');
            finishProcess();
        } else
        if (progress == 100){
          $('#rescanconfirmprogress').find('.modal-header').find('h4').html('<i class="fa fa-check-circle"></i> Library {{ storage }} detection done.');
          $('#{{ form.taskid.id_for_label }}').val(taskid);
          finishProcess();
        }
      },
    });
  };
  function onDataReceived(data) {
    button.button('Done...');
    var modal = button.closest('.modal')
    modal.modal('hide');
    taskid = data['taskid'];
    $('#rescanconfirmprogress').modal('show');
    rpintervalId = setInterval(refreshProgress, 1000);
    $('#rescanconfirmprogress').on('hide.bs.modal', function (event) {
      closeProgress();
    });
    modal.on('hidden.bs.modal', function (){
      button.text(text);
    });
  };
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
