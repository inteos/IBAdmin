<script>
  $(function () {
    //Initialize Select2 Elements
    $(".select2").select2();
    $('input').iCheck({
      //Initialize iCheck - boxes
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue',
    });
    $("#{{ form.thumbprint.id_for_label }}-btn").on('click', function(){
        var button = $(this);
        var ico = button.find("i");
        var address = $('#{{ form.url.id_for_label }}').val();
        if (address.length > 0){
            button.removeClass('btn-success').removeClass('btn-danger').addClass('btn-default');
            ico.removeClass('fa-search').removeClass('fa-thumbs-o-up').addClass('fa-refresh fa-spin');
            encoded = encodeURIComponent(address);
            $.ajax({
                url: "{% url 'vmsgetvcenterthumbprint' %}?url=" + encoded,
                type: "GET",
                dataType: "json",
                success: function(data){
                    ico.removeClass('fa-refresh fa-spin');
                    if (data[0]){
                        button.removeClass('btn-default').addClass('btn-success');
                        ico.addClass('fa-thumbs-o-up');
                        $('#{{ form.thumbprint.id_for_label }}').val(data[1]).valid();
                    } else {
                        ico.addClass('fa-search');
                        button.removeClass('btn-default').addClass('btn-danger')
                    }
                },
                error: function(request,status,error){
                  ico.removeClass('fa-refresh fa-spin');
                  ico.addClass('fa-search');
                  button.removeClass('btn-default').addClass('btn-danger')
                  {% include 'widgets/errorprocessingajax.js' %}
                },
            });
        };
    });
    $('#{{ form.address.id_for_label }}').change(function(){
        var address = $(this).val();
        var url = '';
        if (address.length > 0){
            url = 'https://' +  address + '/sdk';
        }
        $('#{{ form.url.id_for_label }}').val(url).valid();
    });
  });
  $("#addform").validate({
    rules: {
      {{ form.name.name }}: {
        required: true,
        remote: {
          url: "{% url 'vmsvcentername' %}"
        },
        componentname: true,
      },
      {{ form.address.name }}: {
        required: true,
        remote: {
          url: "{% url 'addressresolution' %}"
        }
      },
      {{ form.client.name }}: {
        required: true,
      },
    },
    messages: {
      {{ form.name.name }}: {
        remote: "vCenter name already exist.",
        componentname: "vCenter name can include simple letters, digits dash, space and underscore only.",
      },
      {{ form.address.name }}: {
        remote: "Address name not resolved. Please correct."
      },
      {{ form.client.name }}: {
        required: "You have to add at least one Backup Client for this vCenter.",
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
{% include 'widgets/helpbutton.js' with helppage='vmhosts.addvcenter' %}