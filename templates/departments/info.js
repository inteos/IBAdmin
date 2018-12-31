<!-- page script -->
<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2({placeholder:'No users available.'});
  });
  function adminsrefresh(){
    $("#adminsloading").show();
    $("#adminsbox").load("{% url 'departsinfoadmins' Department.name %}", function(response,stat,xhr){
      $("#adminsloading").hide();
      if (stat == "error"){
        status = xhr.status;
        error = xhr.statusText;
        {% include 'widgets/errorprocessingajax.js' %}
      }
    });
  };
  function usersrefresh(){
    $("#usersloading").show();
    $("#usersbox").load("{% url 'departsinfousers' Department.name %}", function(response,stat,xhr){
      $("#usersloading").hide();
      if (stat == "error"){
        status = xhr.status;
        error = xhr.statusText;
        {% include 'widgets/errorprocessingajax.js' %}
      }
    });
  };
  function refreshUsers(){
    adminsrefresh();
    usersrefresh();
  };
  $(function(){
    refreshUsers();
  });
  $(document).on('click', '.member-delete', function(){
    var username = $(this).data('username');
    if (username){
      function onDeletemember(data){
        if (data[0]){
          refreshUsers();
          var value = data[1];
          var text = data[2];
          $('#{{ form.user.id_for_label }}').append(
            $('<option>', {
                value: value,
                text: text,
            })
          );
        };
      };
      {% include 'widgets/onErrorReceivedbutton.js' %}
      url = "{% url 'departsdeletemember_rel' Department.name %}"+username+'/';
      $.ajax({
        url: url,
        type: "GET",
        success: onDeletemember,
        error: onErrorReceived,
      });
    };
  });
  $('#adminsrefresh').on('click', adminsrefresh);
  $('#usersrefresh').on('click', usersrefresh);
{% if perms.departments.add_members %}
  var form = $("#addform");
  form.validate({
    rules: {
      {{ form.user.name }}: {
        required: true,
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
  $('#addmember').on('click', function (e){
    if (form.valid()){
      var formdata = $("#addform").serialize();
      function onSavedata(data){
        if (data[0]){
          $('#{{ form.user.id_for_label }} option[value="'+data[1]+'"]').remove()
          refreshUsers();
        }; // TODO: add error handling
      };
      $.ajax({
        url: "{% url 'departsaddmember' Department.name %}",
        type: "POST",
        data: formdata,
        dataType: "json",
        success: onSavedata,
      });
    };
  });
{% endif %}
{% url 'departsdefined' as ddhrefurl %}
{% include "widgets/confirmbuttonhref.js" with selector='#departdeleteconfirmbutton' href=ddhrefurl %}
{% include 'widgets/confirmmodal1a.js' with selector='#departdeleteconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='departments.info' %}
{% include 'widgets/helpbutton.js' with helppage='departments.infoadmins' id='helpadminbutton' %}
{% include 'widgets/helpbutton.js' with helppage='departments.infousers' id='helpuserbutton' %}