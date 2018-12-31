<!-- page script -->
<script>
$(function () {
  var table = $("#roleslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'rolesdefineddata' %}",
    "language": {
      "emptyTable": "No Roles defined?"
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "96px", "sClass": "vertical-align text-center", "render": function(data,type,row){return renderlabel(data);},},
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var ret = btn + 'onclick="location.href=\'{% url 'rolesinfo_rel' %}'+data[0]+'/\';"><i class="fa fa-calendar-check-o" data-toggle="tooltip" data-original-title="Permissions"></i></button>\n';
{% if perms.roles.change_roles or perms.roles.delete_roles %}
          if (!data[1]){
{% if perms.roles.change_roles %}
            ret += btn + 'onclick="location.href=\'{% url 'rolesedit_rel' %}'+data[0]+'/\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
{% endif %}
{% if perms.roles.delete_roles %}
            ret += btn + 'data-toggle="modal" data-target="#roledeleteconfirm" data-name="'+data[0]+'" data-url="{% url 'rolesdelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
{% endif %}
          };
{% endif %}
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
{% if perms.roles.delete_roles %}
{% include "widgets/confirmbutton.js" with selector='#roledeleteconfirmbutton' %}
{% endif %}
});
{% if perms.roles.delete_roles %}
{% include 'widgets/confirmmodal1.js' with selector='#roledeleteconfirm' %}
{% endif %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='roles.defined' %}