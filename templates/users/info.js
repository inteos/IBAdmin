<!-- page script -->
<script>
function refreshDeparts(){
  $("#departsbox").load("{% url 'usersinfodeparts' User.username %}", function() { $("#departsboxloading").hide(); });
};
function refreshRoles(){
  $("#rolesbox").load("{% url 'usersinforoles' User.username %}", function() { $("#rolesboxloading").hide(); });
};
$(function(){
  refreshDeparts();
  refreshRoles();
});
$('#departrefresh').on('click', function(){
  $("#departsboxloading").show();
  refreshDeparts();
});
$('#rolesrefresh').on('click', function(){
  $("#rolesboxloading").show();
  refreshRoles();
});

{% if perms.departments.add_members %}
//Initialize Select2 Element
$("#{{ formdepart.departments.id_for_label }}").select2({placeholder:'No departments available.'});
var formdepart = $("#adddepartform");
formdepart.validate({
  rules: {
    {{ formdepart.departments.name }}: {
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
$('#adddepart').on('click', function (e){
  if (formdepart.valid()){
    var formdata = $("#adddepartform").serialize();
    function onSavedata(data){
      if (data[0]){
        $('#{{ formdepart.departments.id_for_label }} option[value="'+data[1]+'"]').remove()
        refreshDeparts();
      }; // TODO: add error handling
    };
    $.ajax({
      url: "{% url 'usersadddepart' User.username %}",
      type: "POST",
      data: formdata,
      dataType: "json",
      success: onSavedata,
    });
  };
});
{% endif %}
{% if perms.departments.delete_members %}
$(document).on('click', '.depart-delete', function(){
  var departname = $(this).data('departname');
  if (departname){
    function onDeletemember(data){
      if (data[0]){
        refreshDeparts();
        var value = data[1];
        var text = data[2];
        $('#{{ formdepart.departments.id_for_label }}').append(
          $('<option>', {
              value: value,
              text: text,
          })
        );
      };
    };
    url = "{% url 'usersdepartdelete_rel' User.username %}"+departname+'/';
    $.ajax({
      url: url,
      type: "GET",
      success: onDeletemember,
    });
  };
});
{% endif %}

{% if perms.users.change_users %}
//Initialize Select2 Elements
$("#{{ formrole.roles.id_for_label }}").select2({placeholder:'No roles available.'});
var formroles = $("#addrolesform");
formroles.validate({
  rules: {
    {{ formrole.roles.name }}: {
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
$('#addrole').on('click', function (e){
  if (formroles.valid()){
    var formdata = $("#addrolesform").serialize();
    function onSavedata(data){
      if (data[0]){
        $('#{{ formrole.roles.id_for_label }} option[value="'+data[1]+'"]').remove()
        refreshRoles();
      }; // TODO: add error handling
    };
    $.ajax({
      url: "{% url 'usersaddroles' User.username %}",
      type: "POST",
      data: formdata,
      dataType: "json",
      success: onSavedata,
    });
  };
});
$(document).on('click', '.roles-delete', function(){
  var rolename = $(this).data('rolename');
  if (rolename){
    function onDeletemember(data){
      if (data[0]){
        refreshRoles();
        var value = data[1];
        var text = data[2];
        $('#{{ formrole.roles.id_for_label }}').append(
          $('<option>', {
              value: value,
              text: text,
          })
        );
      };
    };
    url = "{% url 'usersrolesdelete_rel' User.username %}"+rolename+'/';
    $.ajax({
      url: url,
      type: "GET",
      success: onDeletemember,
    });
  };
});
{% endif %}
$(function(){
{% if perms.users.suspend_users %}
  function setupButtons(isactive){
    if (isactive){
      $('#userlockbadge').removeClass('bg-gray').addClass('bg-green').text('Active');
    } else {
      $('#userlockbadge').removeClass('bg-green').addClass('bg-gray').text('Locked');
    };
    var canlock = !('{{ User.username }}' == '{{ user.username }}' || ('{{ User.is_superuser }}' == 'True' && {{ nrsuperusers }} < 2))
    if (canlock){
      if (isactive){
        $('#userunlockbutton').hide();
        $('#userlockbutton').show();
      } else {
        $('#userlockbutton').hide();
        $('#userunlockbutton').show();
      }
    } else {
      $('#userlockbutton').addClass('disabled').show();
      $('#userunlockbutton').hide();
    };
  };

  setupButtons('{{ User.is_active }}' == 'True');

  $('#userlockconfirmbutton, #userunlockconfirmbutton').on('click', function () {
    var button = $(this)
    var text = button.text()
    button.button('loading')
    var url = button.data('url')
    function onDataReceived(data) {
      button.button('Done...');
      button.closest('.modal').modal('hide');
      var isactive = data[1]
      setupButtons(isactive)
      button.text(text);
    };
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
    });
  });
{% include 'widgets/confirmmodal1.js' with selector='#userlockconfirm, #userunlockconfirm' %}
{% endif %}

{% if perms.users.delete_users %}
{% url 'usersdefined' as duhrefurl %}
{% include "widgets/confirmbuttonhref.js" with selector='#userdeleteconfirmbutton' href=duhrefurl %}
{% include 'widgets/confirmmodal1.js' with selector='#userdeleteconfirm' %}
{% endif %}
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='users.departments' id='departhelp' %}
{% include 'widgets/helpbutton.js' with helppage='users.roles' id='roleshelp' %}