  $('#labelconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    var taskid = 0;
    var rpintervalId;
    {% include 'widgets/onErrorReceivedbutton.js' %}
    function closeProgress(){
      clearInterval(rpintervalId);
      $('#labelconfirmprogress').on('hidden.bs.modal', function (){
        $('#taskprogress').css('width','0%').attr('aria-valuenow',0);
        $('#taskprogress').html("0%");
        $('#labelconfirmprogress').removeClass('modal-danger');
      });
      $.ajax({
        url: "{% url 'storagevolumesnr' %}",
        type: "GET",
        dataType: "json",
        success: function(data){
            var nr = data['storagevolumesnr'];
            if (nr > 0){
                $('#storagevolumesnr').show();
                $('#storagevolumesnrval').html(nr);
            }
        },
        error: onErrorReceived,
      });
    };
    function refreshProgress(){
      $.ajax({
        url: '{% url 'tasksprogress_rel' %}' + taskid + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
          $('#taskprogress').css('width',data[1]).attr('aria-valuenow',data[0]);
          $('#taskprogress').html(data[1]);
          if (data[0] == 100){
            $('#labelconfirmprogress').modal('hide');
          };
          if (data[2] == 'E' || data[2] == 'C'){
            $('#labelconfirmprogress').addClass('modal-danger');
            $('#labelconfirmprogress').find('.modal-header').find('h4').html('Failed...')
            closeProgress();
          }
        },
        error: onErrorReceived,
      });
    };
    function onDataReceived(data) {
      button.button('Done...');
      var modal = button.closest('.modal')
      modal.modal('hide');
      taskid = data['taskid'];
      $('#labelconfirmprogress').modal('show');
      rpintervalId = setInterval(refreshProgress, 1000);
      $('#labelconfirmprogress').on('hide.bs.modal', function (event) {
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
      error: onErrorReceived,
    });
  });
