<script>
  $('#{{ form.storage.id_for_label }}').change(function(){
    var storage = $('#{{ form.storage.id_for_label }}').val();
    if (storage == 'file'){
      $('#divarchdir').show();
      $('#divdedupdir').hide();
      $('#divdedupidxdir').hide();
      $('#sbutton').html('Save');
      $('#initsetup').attr('action', "{% url 'initialsetup' %}");
    } else
    if (storage == 'dedup'){
      $('#divarchdir').hide();
      $('#divdedupdir').show();
      $('#divdedupidxdir').show();
      $('#sbutton').html('Save');
      $('#initsetup').attr('action', "{% url 'initialsetup' %}");
    } else {
      $('#divarchdir').hide();
      $('#divdedupdir').hide();
      $('#divdedupidxdir').hide();
      $('#sbutton').html('Next <i class="fa fa-chevron-right"></i>');
      $('#initsetup').attr('action', "{% url 'initiallibdetect' %}");
    }
  });
  $("#initsetup").validate({
    rules: {
      {{ form.admrpass.name }}: {
        equalTo: "#{{ form.admpass.id_for_label }}",
      },
      {{ form.email.name }}: {
        required: true,
        email: true,
      },
      {{ form.archivedir.name }}: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        }
      },
      {{ form.dedupdir.name }}: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        },
      },
      {{ form.dedupidxdir.name }}: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        }
      },
    },
    messages: {
      {{ form.dirname.name }}: "You have to provide a System name.",
      {{ form.admrpass.name }}: "Passords does not match. Retype again.",
      {{ form.archivedir.name }}: "You have to provide archive directory name which exist on system.",
      {{ form.dedupdir.name }}: "You have to provide deduplication index directory name which exist on system.",
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
