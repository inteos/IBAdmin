<script>
{% include 'widgets/jobformeditinitialize.js' %}
{% include 'widgets/jobformbackupsch.js' %}
{% include 'widgets/jobformscheduleweek.js' %}
{% include 'widgets/jobformschedulemonth.js' %}
{% include 'widgets/jobformretention.js' %}
{% include 'widgets/jobformallvms.js' %}
  $("#editform").validate({
    rules: {
      {{ form.name.name }}: {
        required: true,
        remote: {
          url: "{% url 'jobsname' %}"
        },
      },
      {{ form.retention.name }}_0: {
        required: true,
        digits: true,
        min: 1,
      },
      {{ form.allvms.name }}: {
        required: "#{{ form.include.id_for_label }}:blank",
      },
      {{ form.include.name }}: {
        required: "#{{ form.allvms.id_for_label }}:blank",
      },
    },
    messages: {
      {{ form.name.name }}: {
        required: "You need to provide a Backup Job name.",
        remote: "Backup Job name already exist. Please choose another one.",
      },
      {{ form.retention.name }}_0: {
        required: "You need to provide a retention period.",
        digits: "Retention is a positive integer. Please correct."
      },
      {{ form.allvms.name }}: {
        required: 'One of: "Include All VM in backup" or "GuestVM to Backup" is required.'
      },
      {{ form.include.name }}: {
        required: 'One of: "Include All VM in backup" or "GuestVM to Backup" is required.'
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
{% include 'widgets/helpbutton.js' with helppage='jobs.editxenserver' %}