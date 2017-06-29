<script>
var displaylog = '';
function clearlog(){
    displaylog = '';
    $('#daemonlogsinfo').show();
    $('#daemonlogs').hide();
};
$('#masterbuttonlog, #sdbuttonlog, #fdbuttonlog, #ibadbuttonlog').click(function () {
    var url = $(this).data('url');
    if (displaylog != url){
        displaylog = url;
        $('#daemonlogsinfo').hide();
        $('#daemonlogs').load(url, function () {
            $('#daemonlogs').show();
        });
    } else {
        clearlog();
    };
});
function fetchDataservicestatus(){
  function onDataReceived(data) {
    dirstat = data['DIRStatus'];
    if (dirstat){
      $('#DIRStatusfailed').hide();
      $('#DIRStatussuccess').show();
      $('#masterbuttonstart').addClass('disabled');
      $('#masterbuttonstop').removeClass('disabled');
    } else {
      $('#DIRStatussuccess').hide();
      $('#DIRStatusfailed').show();
      $('#masterbuttonstart').removeClass('disabled');
      $('#masterbuttonstop').addClass('disabled');
    };
    sdstat = data['SDStatus'];
    if (sdstat){
      $('#SDStatusfailed').hide();
      $('#SDStatussuccess').show();
      $('#sdbuttonstart').addClass('disabled');
      $('#sdbuttonstop').removeClass('disabled');
    } else {
      $('#SDStatussuccess').hide();
      $('#SDStatusfailed').show();
      $('#sdbuttonstart').removeClass('disabled');
      $('#sdbuttonstop').addClass('disabled');
    };
    fdstat = data['FDStatus'];
    if (fdstat){
      $('#FDStatusfailed').hide();
      $('#FDStatussuccess').show();
      $('#fdbuttonstart').addClass('disabled');
      $('#fdbuttonstop').removeClass('disabled');
    } else {
      $('#FDStatussuccess').hide();
      $('#FDStatusfailed').show();
      $('#fdbuttonstart').removeClass('disabled');
      $('#fdbuttonstop').addClass('disabled');
    };
    ibadstat = data['IBADStatus'];
    if (ibadstat){
      $('#IBADStatusfailed').hide();
      $('#IBADStatussuccess').show();
      $('#ibadbuttonstart').addClass('disabled');
      $('#ibadbuttonstop').removeClass('disabled');
    } else {
      $('#IBADStatussuccess').hide();
      $('#IBADStatusfailed').show();
      $('#ibadbuttonstart').removeClass('disabled');
      $('#ibadbuttonstop').addClass('disabled');
    };
    $('#restartinfo').fadeOut(3000);
  };
  $.ajax({
    url: "{% url 'servicestatuswidget' %}",
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
};
$(function(){
  setInterval(fetchDataservicestatus, 60000);
});
$('#masterbuttonstop, #sdbuttonstop, #masterbuttonrestart, #sdbuttonrestart').on('click', function () {
  var urldaemon = $(this).data('url');
  var daemonoper = $(this).data('oper');
  var name = $(this).data('daemon');
  function onDataReceived(data) {
    if (data['status'] == 2) {
      // ask for permission
      $('#confirmbutton').data('urldaemon', urldaemon);
      $('#daemonname').text(name + ' Daemon');
      $('#daemonoperation').text(daemonoper);
      $('#demonconfirm').modal('show');
    } else {
      // update flags
      fetchDataservicestatus();
      if (displaylog !=''){
        $('#daemonlogs').load(displaylog);
      };
      if (daemonoper == 'restart'){
        $('#restartinfo').show();
      };
    };
  };
  $.ajax({
    url: urldaemon,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
$('#confirmbutton').on('click', function () {
  var urlstop = $(this).data('urldaemon') + '?conf=Y';
  function onDataReceived(data) {
    $('#demonconfirm').modal('hide');
    fetchDataservicestatus();
    if (displaylog !=''){
      $('#daemonlogs').load(displaylog);
    };
  };
  $.ajax({
    url: urlstop,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
$('#fdbuttonstop, #ibadbuttonstop, #masterbuttonstart, #sdbuttonstart, #fdbuttonstart, #ibadbuttonstart, #fdbuttonrestart, #ibadbuttonrestart').on('click', function () {
  var urldaemon = $(this).data('url');
  var daemonoper = $(this).data('oper');
  function onDataReceived(data) {
    // update flags
    fetchDataservicestatus();
    if (displaylog !=''){
      $('#daemonlogs').load(displaylog);
    };
    if (daemonoper){
      $('#restartinfo').show();
    };
  };
  $.ajax({
    url: urldaemon,
    type: "GET",
    dataType: "json",
    success: onDataReceived,
  });
});
</script>
{% include "pages/refresh.js" %}
