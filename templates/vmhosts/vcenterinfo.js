<!-- page script -->
<script>
$(function () {
{% include "widgets/refreshbutton.js" %}
  $('#deletevcenterconfirmbutton').on('click', function () {
    var button = $(this);
    var text = button.text();
    button.button('loading');
    var url = button.data('url');
    function onDataReceived(data) {
      button.button('Done...');
      var modal = button.closest('.modal')
      modal.modal('hide');
      if (data['status']) {
        location.href="{% url 'vmsvcenterdefined' %}";
      }
      modal.on('hidden.bs.modal', function (){
        button.text(text);
      });
    };
    {% include 'widgets/onErrorReceivedbutton.js' %}
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: onDataReceived,
      error: onErrorReceived,
    });
  });
});
{% include 'widgets/confirmmodal1.js' with selector='#deletevcenterconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" %}
{% include 'widgets/helpbutton.js' with helppage='vmhosts.vcenterinfo' %}