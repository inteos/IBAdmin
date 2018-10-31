<script>
$(function () {
  $(".select2").select2();
});
$(function () {
  var form = $("#editform");
  form.validate({
    rules: {
      {{ form.email.name }}: {
        required: true,
        email: true,
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
  $('#savebutton').on('click', function (e){
    if (form.valid()){
      $('#saveinfo').hide();
      var formdata = $("#editform").serialize();
      function onSavedata(data){
        if (data){
          $('#restartsrvinfo').show();
          $('#saveinfo').removeClass('alert-success').addClass('alert-warning');
        } else {
          $('#restartsrvinfo').hide();
          $('#saveinfo').removeClass('alert-warning').addClass('alert-success');
        };
        $('#saveinfo').show();
      };
      $.ajax({
        url: "{% url 'systemconfigsave' %}",
        type: "POST",
        data: formdata,
        dataType: "json",
        success: onSavedata,
      });
    };
  });
});
// check for updates
function updateRelease(data){
  var version = data['tag_name']
  var url = data['html_url']
  var text = 'Update available&nbsp; <a href="' + url + '"><i class="fa fa-external-link"></i></a>';
  if (version > "{{ ibadminver }}"){
    $('#updatebadge').removeClass('label-success').addClass('label-warning').html(text);
  };
};
$(function () {
  $.ajax({
    url: "https://api.github.com/repos/inteos/IBAdmin/releases/latest",
    type: "GET",
    dataType: "json",
    success: updateRelease,
  });
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='system.config' %}
