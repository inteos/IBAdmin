<script>
{% for w in Section1 %}
{% include w.widget.templatejs with id=w.widget.widgetid %}
{% endfor %}
{% for w in Section2 %}
{% include w.widget.templatejs with id=w.widget.widgetid %}
{% endfor %}

  function fetchData() {
    {% for w in Section1 %}
    fetchData{{ w.widget.widgetid }}();
    {% endfor %}
    {% for w in Section2 %}
    fetchData{{ w.widget.widgetid }}();
    {% endfor %}
  };

  // flot init and refresh calls
  $(function () {
    fetchData();
    setInterval(fetchData, 60000);
  });

  $('.connectedSortable').sortable({
    placeholder: 'sort-highlight',
    connectWith: '.connectedSortable',
    handle: '.box-header, .nav-tabs, .status-service',
    forcePlaceholderSize: true,
    zIndex: 999999,
    update: function(){
      var data = $(this).sortable('serialize');
      var sectionid = $(this).attr('id');
      var url = "{% url 'changewidgets_rel' %}" + sectionid + '/?' + data
      $.ajax({
        url: url,
        type: "GET",
      });
    }
  });
  $('.connectedSortable .box-header, .connectedSortable .nav-tabs-custom, .connectedSortable .status-service').css('cursor', 'move');
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
