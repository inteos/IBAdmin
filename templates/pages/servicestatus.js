  function fetchData{{ id }}(){
    function onDataReceived(data) {
      dirstat = data['DIRStatus'];
      if (dirstat){
        $('#DIRStatusfailed').hide();
        $('#DIRStatussuccess').show();
      } else {
        $('#DIRStatussuccess').hide();
        $('#DIRStatusfailed').show();
      };
      sdstat = data['SDStatus'];
      if (sdstat){
        $('#SDStatusfailed').hide();
        $('#SDStatussuccess').show();
      } else {
        $('#SDStatussuccess').hide();
        $('#SDStatusfailed').show();
      };
      fdstat = data['FDStatus'];
      if (fdstat){
        $('#FDStatusfailed').hide();
        $('#FDStatussuccess').show();
      } else {
        $('#FDStatussuccess').hide();
        $('#FDStatusfailed').show();
      };
      ibadstat = data['IBADStatus'];
      if (ibadstat){
        $('#IBADStatusfailed').hide();
        $('#IBADStatussuccess').show();
      } else {
        $('#IBADStatussuccess').hide();
        $('#IBADStatusfailed').show();
      };
    };
    $.ajax({
      url: '{% url id %}',
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  };