<!-- page script -->
<script>
$(function () {
  var table = $("#departmentslist").DataTable({
    "serverSide": true,
    "ajax": "{% url 'departsdefineddata' %}",
    "language": {
      "emptyTable": "No Departments defined."
    },
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align" },
      { "width": "120px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align" },
      { "width": "96px", "sClass": "vertical-align text-center", "render": function ( data, type, row ) { return renderlabel(data);}, },
      { "width": "64px", "orderable": false, "sClass": "vertical-align text-center", "render": function ( data, type, row ) { return rendermembers(data,'bg-orange');}, },
      { "width": "64px", "orderable": false, "sClass": "vertical-align text-center", "render": function ( data, type, row ) { return rendermembers(data,'bg-green');}, },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function ( data, type, row ) {
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var ret = btn + 'onclick="location.href=\'{% url 'departsinfo_rel' %}'+data[1]+'/\';"><i class="fa fa-users" data-toggle="tooltip" data-original-title="Members"></i></button>\n';
{% if perms.departments.change_departments %}
          ret += btn + 'onclick="location.href=\'{% url 'departsedit_rel' %}'+data[1]+'/\';"><i class="fa fa-wrench" data-toggle="tooltip" data-original-title="Edit"></i></button>\n';
{% endif %}
{% if perms.departments.delete_departments %}
          if (data[2]){
            ret += btn + 'data-toggle="modal" data-target="#departdeleteconfirm" data-name="'+data[0]+'" data-url="{% url 'departsmakedelete_rel' %}'+data[1]+'/"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          }
{% endif %}
          return '<div class="btn-group">' + ret + '</div>';
        },
      },
    ],
  });
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#departdeleteconfirmbutton' %}
});
{% include 'widgets/confirmmodal1a.js' with selector='#departdeleteconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='users.defined' %}