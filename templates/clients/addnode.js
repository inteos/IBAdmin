<script>
{% include 'widgets/osicon.js' %}
  $(function () {
    var curos = $("#{{ form.os.id_for_label }}").val();
    var icon = set_osicon(curos);
    $('#{{ form.os.id_for_label }}icon').removeClass().addClass(icon);
  });
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
    $('#{{ form.clusterlist.id_for_label }}').select2({
      placeholder: "Select defined cluster name",
      allowClear: true
    });
    $("#{{ form.os.id_for_label }}").on('change', function(event){
      var icon = set_osicon(this.value);
      $('#{{ form.os.id_for_label }}icon').removeClass().addClass(icon);
    });
  });
  $(function () {
    $('input').iCheck({
      //Initialize iCheck - boxes
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue',
    });
  });
  $('#{{ form.clusterlist.id_for_label }}').on('change', function(event){
    var cluster = this.value
    if (!cluster){
      $('#{{ form.cluster.id_for_label }}').prop('disabled', false);
    } else {
      $('#{{ form.cluster.id_for_label }}').prop('disabled', true);
      $('#{{ form.cluster.id_for_label }}').closest('.form-group').removeClass('has-error');
      $('#clustername-error').hide();

      $.ajax({
        url: '{% url 'clientsclusterparam_rel' %}' + cluster + '/',
        type: "GET",
        dataType: "json",
        success: function(data){
          $('#{{ form.os.id_for_label }}').val(data['os']).trigger('change');
          $('#{{ form.departments.id_for_label }}').val(data['department']).trigger('change');
        },
      });

    };
  });
  $('#{{ form.cluster.id_for_label }}').on('input', function(event){
    if (!this.value){
      $('#{{ form.clusterlist.id_for_label }}').prop('disabled', false);
    } else {
      $('#{{ form.clusterlist.id_for_label }}').prop('disabled', true);
      $('#{{ form.clusterlist.id_for_label }}').closest('.form-group').removeClass('has-error');
    };
  });
  $("#addform").validate({
    groups: {
      clustername: "{{ form.cluster.name }} {{ form.clusterlist.name }}",
    },
    rules: {
      {{ form.name.name }}: {
        required: true,
        remote: {
          url: "{% url 'clientsname' %}"
        },
        componentname: true,
      },
      {{ form.address.name }}: {
        required: true,
        remote: {
          url: "{% url 'addressresolution' %}"
        }
      },
      {{ form.cluster.name }}: {
        required: "#{{ form.clusterlist.id_for_label }}:blank",
        remote: {
          url: "{% url 'clientsclustername' %}"
        }
      },
      {{ form.clusterlist.name }}: {
        required: "#{{ form.cluster.id_for_label }}:blank",
      },
    },
    messages: {
      {{ form.name.name }}: {
        remote: "Client name already exist.",
        componentname: "Client name can include simple letters, digits dash, space and underscore only.",
      },
      {{ form.address.name }}: {
        remote: "Address name not resolved. Please correct."
      },
      {{ form.cluster.name }}: {
        required: 'One of: "New Cluster name" or "Existing Cluster" is required.',
        remote: "Cluster name already exist.",
      },
      {{ form.clusterlist.name }}: {
        required: 'One of: "New Cluster name" or "Existing Cluster" is required.'
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
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='clients.addnode' %}