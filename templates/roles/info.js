<!-- page script -->
<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2({
        placeholder: 'Select permission'
    });
  });
  function refreshPermissions(){
    $("#permissionsgroup").load("{% url 'rolesinfoperms' Role.group.name %}");
  };
  $(function(){
    refreshPermissions();
  });
{% if perms.roles.change_roles %}
  $(document).on('click', '.perms-delete', function(){
    var codename = $(this).data('codename');
    var applabel = $(this).data('applabel');
    if (codename != null & applabel != null){
      function onDeletemember(data){
        if (data[0]){
          refreshPermissions();
          var group = data[1];
          var value = data[2];
          var text = data[3];
          var optgroup = $('#{{ form.perms.id_for_label }}').find('optgroup[label="'+group+'"]')
          if (optgroup.length){
            optgroup.append($('<option>', {
                value: value,
                text: text,
              })
            );
          };
          $('#{{ form.perms.id_for_label }}').select2("destroy").select2({
            placeholder: 'Select permission'
          }).val(null).trigger("change");
        };
      };
      {% include 'widgets/onErrorReceived.js' %}
      url = "{% url 'rolesdeleteperms_rel' Role.group.name %}"+applabel+'/'+codename+'/';
      $.ajax({
        url: url,
        type: "GET",
        success: onDeletemember,
        error: onErrorReceived,
      });
    };
  });
  var form = $("#addform");
  form.validate({
    rules: {
      {{ form.perms.name }}: {
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
  $('#addperm').on('click', function (e){
    if (form.valid()){
      var formdata = $("#addform").serialize();
      {% include 'widgets/onErrorReceived.js' %}
      function onSavedata(data){
        if (data[0]){
          if (data[1]){
            var applabel = data[2];
            $('#{{ form.perms.id_for_label }}').find('optgroup').each(function(index){
              var label = $(this).attr('label');
              if (applabel == label){
                $(this).find('option').each(function(i){
                  $(this).remove()
                });
                $('#{{ form.perms.id_for_label }}').select2("destroy").select2({
                  placeholder: 'Select permission'
                }).val(null).trigger("change");
              };
            });
          } else {
            $('#{{ form.perms.id_for_label }} option[value="'+data[2]+'"]').remove();
            $('#{{ form.perms.id_for_label }}').select2("destroy").select2({
              placeholder: 'Select permission'
            }).val(null).trigger("change");
          }
          refreshPermissions();
        } else {
          onErrorReceived(null,'Processing Error',data[2]);
        };
      };
      $.ajax({
        url: "{% url 'rolesaddperms' Role.group.name %}",
        type: "POST",
        data: formdata,
        dataType: "json",
        success: onSavedata,
        error: onErrorReceived,
      });
    };
  });
{% endif %}
{% if perms.roles.delete_roles %}
{% url 'rolesdefined' as drhrefurl %}
{% include "widgets/confirmbuttonhref.js" with selector='#roledeleteconfirmbutton' href=drhrefurl %}
{% include 'widgets/confirmmodal1.js' with selector='#roledeleteconfirm' %}
{% endif %}
</script>
{% if perms.roles.change_roles %}
{% include 'widgets/helpbutton.js' with helppage='roles.permissions' %}
{% else %}
{% include 'widgets/helpbutton.js' with helppage='roles.info' %}
{% endif %}