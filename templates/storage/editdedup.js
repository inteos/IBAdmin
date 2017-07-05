<script>
$(function () {
  //Initialize Select2 Elements
  $(".select2").select2();
});
$("#editform").validate({
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
    {{ form.dedupidxdir.name }}: {
      required: true,
      remote: {
        url: "{% url 'storagearchivedir' %}"
      }
    },
    {{ form.dedupdir.name }}: {
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
    {{ form.dedupidxdir.name }}:{
      remote: "You have to provide archive directory name which exist on system.",
    },
    {{ form.dedupdir.name }}:{
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
  $('#{{ form.dedupidxdir.id_for_label }}').change(function(event){
    $('#dedupidxdirconfirm').modal('show');
  });
  $('#dedupidxdirconfirmbutton, #dedupidxdirconfirmbuttonx').on('click', function () {
    $('#dedupidxdirconfirm').modal('hide');
    $('#{{ form.dedupidxdir.id_for_label }}').val('{{ form.dedupidxdir.value }}');
  });
  $('#dedupidxdirconfirmbuttonyes').click(function () {
    $('#{{ form.dedupidxdir.id_for_label }}').off('change');
  });
  $('#{{ form.dedupdir.id_for_label }}').change(function(event){
    $('#dedupdirconfirm').modal('show');
  });
  $('#dedupdirconfirmbutton, #dedupdirconfirmbuttonx').on('click', function () {
    $('#dedupdirconfirm').modal('hide');
    $('#{{ form.dedupdir.id_for_label }}').val('{{ form.dedupdir.value }}');
  });
  $('#dedupdirconfirmbuttonyes').click(function () {
    $('#{{ form.dedupdir.id_for_label }}').off('change');
  });
});
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.editdedup' %}