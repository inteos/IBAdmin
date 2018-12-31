<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
//    $('#{{ form.clusterlist.id_for_label }}').select2({
//      placeholder: "Select defined cluster name",
//      allowClear: true
//    });
//  $('#{{ form.clusterlist.id_for_label }}').on('change', function(event){
//    if (!this.value){
//      $('#{{ form.cluster.id_for_label }}').prop('disabled', false);
//    } else {
//      $('#{{ form.cluster.id_for_label }}').prop('disabled', true);
//      $('#{{ form.cluster.id_for_label }}').closest('.form-group').removeClass('has-error');
//      $('#clustername-error').hide();
//    };
//  });
//  $('#{{ form.cluster.id_for_label }}').on('input', function(event){
//    if (!this.value){
//      $('#{{ form.clusterlist.id_for_label }}').prop('disabled', false);
//    } else {
//      $('#{{ form.clusterlist.id_for_label }}').prop('disabled', true);
//      $('#{{ form.clusterlist.id_for_label }}').closest('.form-group').removeClass('has-error');
//    };
//  });
  });
  $("#addform").validate({
//    groups: {
//      clustername: "{{ form.cluster.name }} {{ form.clusterlist.name }}",
//    },
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
        componentname: "Storage name must include simple letters, digits, dashes, spaces and underscore only.",
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
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.adddedup' %}