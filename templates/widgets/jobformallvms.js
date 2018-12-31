{% if not form.allvms.value %}
    $('#{{ form.exclude.id_for_label }}-group').hide();
{% else %}
   $('#{{ form.include.id_for_label }}-group').hide();
{% endif %}
  $(function(){
    $('input').on('ifChanged', function(e) {
      var isChecked = e.currentTarget.checked;
      if (isChecked){
        $('#{{ form.include.id_for_label }}-group').hide();
        $('#{{ form.exclude.id_for_label }}-group').show();
      } else {
        $('#{{ form.include.id_for_label }}-group').show();
        $('#{{ form.exclude.id_for_label }}-group').hide();
      };
    });
  });