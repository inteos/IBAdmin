<script>
  $('#storage').change(function(){
    if ($('#storage').val() == 'file'){
      $('#divarchdir').show();
      $('#divdedupdir').hide();
      $('#divdedupidxdir').hide();
    } else
    if ($('#storage').val() == 'dedup'){
      $('#divarchdir').hide();
      $('#divdedupdir').show();
      $('#divdedupidxdir').show();
    } else {
      $('#divarchdir').hide();
      $('#divdedupdir').hide();
      $('#divdedupidxdir').hide();
    }
  });
  $("#initsetup").validate({
    rules: {
      admrpass: {
        equalTo: "#admpass",
      },
      email: {
        required: true,
        email: true,
      },
      archivedir: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        }
      },
      dedupdir: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        },
      },
      dedupidxdir: {
        required: true,
        remote: {
          url: "{% url 'initialarchivedir' %}"
        }
      },
    },
    messages: {
      dirname: "You have to provide a System name.",
      admrpass: "Passords does not match. Retype again.",
      archivedir: "You have to provide archive directory name which exist on system.",
      dedupdir: "You have to provide deduplication index directory name which exist on system.",
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
