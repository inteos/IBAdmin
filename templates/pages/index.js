<script>
{% include 'pages/cpuutilwidget.js' with id='cpuutilwidget' %}
{% include 'pages/backupsizewidget.js' with id='backupsizewidget' %}
{% include 'pages/lastjobswidget.js' with id='lastjobswidget' %}
{% include 'pages/runningjobswidget.js' with id='runningjobswidget' %}
{% include 'pages/servicestatus.js' with id='servicestatuswidget' %}
{% include 'pages/alljobswidget.js' with id='alljobswidget' %}

  function fetchData() {
    fetchDatacpuutilwidget();
    fetchDatabackupsizewidget();
    fetchDatalastjobswidget();
    fetchDatarunningjobswidget();
    fetchDataservicestatuswidget();
    fetchDataalljobswidget();
  };

  // flot init and refresh calls
  $(function () {
    fetchData();
    setInterval(fetchData, 60000);
  });
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
