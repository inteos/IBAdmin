<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
  });
  $("#addform").validate({
    rules: {
      {{ form.name.name }}: {
        required: true,
        remote: {
          url: "{% url 'storagename' %}"
        },
        componentname: true,
      },
      {{ form.address.name }}: {
        required: "#{{ form.storagelist.id_for_label }}:blank",
        remote: {
          url: "{% url 'storageaddress' %}"
        }
      },
      {{ form.storagelist.name }}: {
        required: "#{{ form.address.id_for_label }}:blank",
      },
    },
    messages: {
      {{ form.name.name }}: {
        remote: "Storage name already exist.",
        componentname: "Storage name can include simple letters, digits dash, space and underscore only.",
      },
      {{ form.address.name }}: {
        required: 'One of: "Storage address" or "Existing Storge" is required.',
        remote: "Address name not resolved. Please correct.",
      },
      {{ form.storagelist.name }}: {
        required: 'One of: "Storage address" or "Existing Storage" is required.',
      },
    },
    highlight: function(element) {
      $(element).closest('.form-group').addClass('has-error');
      $(element).closest('.form-group').removeClass('has-success');
    },
    unhighlight: function(element) {
      $(element).closest('.form-group').removeClass('has-error');
      $(element).closest('.form-group').addClass('has-success');
    },
    errorElement: 'span',
    errorClass: 'help-block',
    errorPlacement: function(error, element) {
      if(element.parent('.input-group').length) {
          error.insertAfter(element.parent());
      } else {
          error.insertAfter(element);
      }
    }
  });

  var intervalId;
  var taskid;

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
          $('#progressbox').removeClass('box-warning').addClass('box-danger');
          $('#header').html('<i class="fa fa-times-circle"></i> Library {{ storage }} detection failed.');
          clearInterval(intervalId);
        } else
        if (progress == 100){
          $('#detectlibbutton').hide();
          $('#addbutton').show();
          $('#progressbox').removeClass('box-warning').addClass('box-success');
          $('#header').html('<i class="fa fa-check-circle"></i> Library {{ storage }} detection done.');
          clearInterval(intervalId);
        }
      },
    });
  };
  $('#detectlibbutton').click(function (){
    $('#detectlibbutton').addClass('disabled').attr("disabled", true);
    $('#detectbox').slideDown();
    var lib = $('#{{ form.tapelist.id_for_label }}').val();
    $.ajax({
      url: "{% url 'storagetapedetect_rel' %}" + lib + '/',
      type: "GET",
      dataType: "json",
      success: function(data){
        taskid = data[0];
        $('#{{ form.taskid.id_for_label }}').val(taskid);
        refreshProgress();
        intervalId = setInterval(refreshProgress, 1000);
      },
    });
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.addtape' %}