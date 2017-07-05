{% load staticfiles %}
{% if Jobids != 'unavl' %}
<!-- page script -->
<script src="{% static 'plugins/jstree/jstree.min.js' %}"></script>
<script>
$(function () {
  var form = $("#restoreform");
  form.validate({
    rules: {
      {{ form.comment.name }}: {
        maxlength: 128,
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
                  return "{% url 'restoretree_rel' Jobids %}" + node.id + '/';
              }
          },
        }
      },
      "plugins": [ "checkbox", "search", "types", ]
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
  $.ajax({
    url: "{% url 'restoreupdatecache' Jobids %}",
    type: "GET",
    dataType: "json",
    success: onDataupdatecache,
  });
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
          url: "{% url 'restoreprepare' Jobids %}",
          type: "POST",
          data: formdata,
          dataType: "json",
          success: onPreparerestore,
        });
    };
  });
});
$(function () {
  //Initialize Select2 Elements
  $(".select2").select2();
});
</script>
{% endif %}
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='restore.jobid' %}
