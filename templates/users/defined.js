<!-- page script -->
<script>
$(function () {
  var table = $("#userslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'usersdefineddata' %}",
    "language": {
      "emptyTable": "No Users defined?"
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderdata(data)}  },
      { "width": "64px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderuserstatus(data)} }, // Status
      { "width": "100px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderusertype(data)} }, // Type
      { "width": "128px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var ret = btn + 'onclick="location.href=\'{% url 'usersinfo_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
{% if perms.users.change_users %}
          var bedi = btn + 'onclick="location.href=\'{% url 'usersedit_rel' %}'+data[0]+'/\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
          ret += bedi;
{% endif %}
{% if perms.users.suspend_users %}
          if (data[3]){
              if (data[2]){
                ret += btn + 'data-toggle="modal" data-target="#userlockconfirm" data-name="'+data[0]+'" data-url="{% url 'userslock_rel' %}"><i class="fa fa-lock" data-toggle="tooltip" data-original-title="Suspend"></i></button>\n';
              } else {
                ret += btn + 'data-toggle="modal" data-target="#userunlockconfirm" data-name="'+data[0]+'" data-url="{% url 'usersunlock_rel' %}"><i class="fa fa-unlock-alt" data-toggle="tooltip" data-original-title="Activate"></i></button>\n';
              };
          };
{% endif %}
{% if perms.users.delete_users %}
          if (data[1]){
            ret += btn + 'data-toggle="modal" data-target="#userdeleteconfirm" data-name="'+data[0]+'" data-url="{% url 'usersdelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          };
{% endif %}
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
{% if perms.users.suspend_users %}
{% include "widgets/confirmbutton.js" with selector='#userlockconfirmbutton, #userunlockconfirmbutton' %}
{% endif %}
{% if perms.auth.delete_user %}
{% include "widgets/confirmbutton.js" with selector='#userdeleteconfirmbutton' %}
{% endif %}
});
{% if perms.users.suspend_users %}
{% include 'widgets/confirmmodal1.js' with selector='#userlockconfirm, #userunlockconfirm' %}
{% endif %}
{% if perms.auth.delete_user %}
{% include 'widgets/confirmmodal1.js' with selector='#userdeleteconfirm' %}
{% endif %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='users.defined' %}