<script>
$(function () {
  //Initialize Select2 Elements
  $(".select2").select2();
});
$("#addform").validate({
  rules: {
    {{ form.name.name }}: {
      required: true,
      remote: {
        url: "{% url 'storagename' %}"
      },
      componentname: true,
    },
    {{ form.address.name }}: {
      required: "#{{ form.storagelist.id_for_label }}:blank",
      remote: {
        url: "{% url 'storageaddress' %}"
      }
    },
    {{ form.storagelist.name }}: {
      required: "#{{ form.address.id_for_label }}:blank",
    },
    {{ form.archivedir.name }}: {
      required: true,
      remote: {
        url: "{% url 'storagearchivedir' %}"
      }
    },
  },
  messages: {
    {{ form.name.name }}: {
      remote: "Storage name already exist.",
      componentname: "Storage name can include simple letters, digits dash, space and underscore only.",
    },
    {{ form.address.name }}: {
      required: 'One of: "Storage address" or "Existing Storge" is required.',
      remote: "Address name not resolved. Please correct.",
    },
    {{ form.storagelist.name }}: {
      required: 'One of: "Storage address" or "Existing Storage" is required.',
    },
    {{ form.archivedir.name }}:{
      remote: "You have to provide archive directory name which exist on system.",
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
$(function (){
  $('#{{ form.archivedir.id_for_label }}').change(function(event){
    $('#archdirconfirm').modal('show');
  });
  $('#archdirconfirmbutton, #archdirconfirmbuttonx').on('click', function () {
    $('#archdirconfirm').modal('hide');
    $('#{{ form.archivedir.id_for_label }}').val('{{ form.archivedir.value }}');
  });
  $('#archdirconfirmbuttonyes').click(function () {
    $('#{{ form.archivedir.id_for_label }}').off('change');
  });
});
</script>
