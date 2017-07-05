<!-- page script -->
<script>
$(function () {
  var table = $("#volumeslist").DataTable({
  "serverSide": true,
    "ajax": "{% url 'storagevolumesdata' %}",
    "language": {
      "emptyTable": "No Volumes currently available."
    },
    "order": [[ 0, 'asc' ]],
    "bAutoWidth": false,
    "columns": [
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "90px", "sClass": "vertical-align text-center storage-media-type", "render": function (data,type,row){ return rendermediatype(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return rendervolstatus(data)} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "128px", "orderable": false, "sClass": "vertical-align text-center", // 32px for every button
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var url = '{% url 'storagevolumeinfo_rel' %}';
          var binf = btn + 'onclick="location.href=\''+url+data[0]+'\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var ret = binf;
          if (data[1] != 'Cleaning'){
              var buse = btn + 'data-toggle="modal" data-target="#volusedconfirm" data-name="'+data[0]+'" data-url="{% url 'storagemakeused_rel' %}"><i class="fa fa-lock" data-toggle="tooltip" data-original-title="Close"></i></button>\n';
              if (data[1] == 'Append'){
                ret += buse;
              };
              var bopn = btn + 'data-toggle="modal" data-target="#volopenconfirm" data-name="'+data[0]+'" data-url="{% url 'storagemakeappend_rel' %}"><i class="fa fa-unlock-alt" data-toggle="tooltip" data-original-title="Open"></i></button>\n';
              if (data[1] == 'Used'){
                ret += bopn;
              };
              var bpur = btn + 'data-toggle="modal" data-target="#volpurgeconfirm" data-name="'+data[0]+'" data-url="{% url 'storagemakepurged_rel' %}"><i class="fa fa-recycle" data-toggle="tooltip" data-original-title="Recycle"></i></button>\n';
              if (data[1] != 'Purged' && data[1] != 'Recycle'){
                ret += bpur;
              };
              var bdel = btn + 'data-toggle="modal" data-target="#voldeleteconfirm" data-name="'+data[0]+'" data-url="{% url 'storagemakedeletevolume_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
              if (data[1] != 'Append'){
                ret += bdel;
              };
          };
          return '<div class="btn-group">'+ret+'</div>';
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#volusedconfirmbutton, #volopenconfirmbutton, #volpurgeconfirmbutton, #voldeleteconfirmbutton' %}
});
{% include 'widgets/confirmmodal1.js' with selector='#volusedconfirm, #volopenconfirm, #volpurgeconfirm, #voldeleteconfirm' %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='storage.volumes' %}