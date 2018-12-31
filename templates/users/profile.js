<!-- page script -->
<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2({placeholder:'No users available.'});
  });
  $('.widgetswitch').change(function(){
    checked = $(this).prop('checked');
    widgetid = $(this).data('widgetid');
    if (checked){
        url = "{% url 'usersprofiledash_rel' 'on' %}";
    } else {
        url = "{% url 'usersprofiledash_rel' 'off' %}";
    };
    url += widgetid + '/';
    $.ajax({
      url: url,
      type: "GET",
    });
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='users.profile' %}
{% include 'widgets/helpbutton.js' with helppage='users.resources' id='userres' %}