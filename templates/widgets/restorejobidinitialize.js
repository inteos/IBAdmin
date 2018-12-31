{% load staticfiles %}
<script>
$(function () {
  //Initialize Select2 Elements
  $(".select2").select2();
  $('.jobselected').on('click', function (e){
    var client = $(this).data('client');
    $('#Three').collapse('toggle');
    $('#Three').on('hidden.bs.collapse', function () {
        url = "{% url 'restoreclient_rel' %}" + client + '/';
        location.href = url;
    });
  });
  $('.jobidselected').on('click', function (e){
    var job = $(this).data('job');
    $('#Three').collapse('toggle');
    $('#Three').on('hidden.bs.collapse', function () {
        url = "{% url 'restorejob_rel' %}" + job + '/';
        location.href = url;
    });
  });
  $('input').iCheck({
    //Initialize iCheck - boxes
    checkboxClass: 'icheckbox_square-blue',
    radioClass: 'iradio_square-blue',
  });
});
</script>
{% if Jobids != 'unavl' %}
<script src="{% static 'plugins/jstree/jstree.min.js' %}"></script>
<script>
$(function () {
  var treeview;
  var selected = 0;
  function onDataupdatecache (){
    treeview = $('#jstreediv').jstree({
      "core": {
        "check_callback" : true,
        "themes": {
          'name': 'proton',
          'responsive': true,
        },
        'data': {
          'url': function (node) {
              if (node.id == '#'){
                return "{{ JobTypeURL }}";
              } else {
                  return "{{ JobTypeQueryURL }}" + node.id + '/';
              }
          },
        }
      },
      "plugins": [ "checkbox", "types", ]
    });
    $('#treeviewloading').hide();
    treeview.on('changed.jstree', function(event, data){
      if (data.selected.length > 0 && data.node.id != 'NO'){
        // selected
        $('#restorebutton').removeClass('disabled');
      } else {
        $('#restorebutton').addClass('disabled');
      };
    });
  };
  function onErrorReceived(request,status,error){
    {% include 'widgets/errorprocessingajax.js' %}
  };
  $.ajax({
    url: "{% url 'restoreupdatecache' Jobids %}",
    type: "GET",
    dataType: "json",
    success: onDataupdatecache,
    error: onErrorReceived,
  });
  var form = $("#restoreform");
  $('#restorebutton').on('click', function (e){
    $('#restoreinfo').modal('show');
    $('#{{ form.rselected.id_for_label }}').val(treeview.jstree(true).get_selected());
    if (form.valid()){
        var formdata = $("#restoreform").serialize();
        function onPreparerestore(data){
            if (data[0] != false){
                rjobid = data[1];
                $('#restoreinfo').modal('hide');
                location.href="{% url 'jobslog_rel' %}"+rjobid+'/';
            } else {
                logid = data[1];
                $('#restoreinfo').modal('hide');
                $('#restoreerror').modal('show');
            };
        };
        $.ajax({
          url: "{{ JobTypePrepareURL }}",
          type: "POST",
          data: formdata,
          dataType: "json",
          success: onPreparerestore,
          error: onErrorReceived,
        });
    };
  });
});
</script>
{% endif %}