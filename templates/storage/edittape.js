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
{% include "widgets/rescanconfirm.js" %}
{% include 'widgets/confirmmodal1a.js' with selector='#rescanconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.edittape' %}