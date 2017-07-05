<script>
  var helppopover = $("#{{ id|default:'helpbutton' }}").popover({
    trigger: 'click',
    placement: 'bottom',
    html: 'true',
    container: "#{{ id|default:'helpbutton' }}",
  });
  $(function () {
    $.ajax({
      url: "{% url 'helppage' helppage %}",
      success: function (html) {
        helppopover.attr('data-content', html);
      }
    });
  });
</script>