function renderdataar(data){
  if (data[0] != null){
    return data[0];
  } else {
    return data[1];
  }
};
function renderdata(data){
  if (data != null){
    return data;
  } else {
    return "-";
  }
};
function renderdatana(data){
  if (data != null){
    return data;
  } else {
    return "<i>N/A</i>";
  }
};
function renderdatadis(enabled,data){
  if (enabled == 'No'){
    return '<span class="label bg-red">Disabled by user</span>';
  };
  if (data != null){
    return data;
  } else {
    return "<i>Disabled</i>";
  }
};
function renderbadge(data){
    return '<span class="badge '+data[0]+'">'+data[1]+'</span>';
};
function renderlabel(data){
  return '<span class="label '+data[0]+'">'+data[1]+'</span>';
};
function bytestext(bytes) {
  if (typeof bytes !== 'undefined' && bytes != ''){
      if (bytes < 1024){
        return bytes + " Bytes";
      }
      bytes = bytes / 1024;
      var s;
      var suffix = [' kB',' MB',' GB',' TB',' PB'];
      for (s of suffix){
          if (bytes < 1024){
            return bytes.toFixed(2) + s;
          };
          bytes = bytes / 1024;
      }
  }
  return '0 Bytes';
};
function bytessectext(bytes){
  return bytestext(bytes) + '/s';
}
function renderclientaddress(addr, alias){
  if (alias != null){
    return '<i class="fa fa-external-link-square" data-toggle="tooltip" data-original-title="Alias client"></i> '+alias;
  } else {
    return addr;
  };
};
function renderclientcluster(name,service){
  if (name != null){
    return '<i class="fa fa-cubes" data-toggle="tooltip" data-original-title="Cluster Node"></i> '+name;
  };
  if (service != null){
    return '<i class="fa fa-cube" data-toggle="tooltip" data-original-title="Cluster Service"></i> '+service;
  } else {
    return '-';
  };
};
function renderdepartmentlabel(data){
  if (data[0] != null){
    return renderlabel(data);
  } else {
    return data[1];
  }
};
function statusbgcolor(status){
    if (status == 1){
        return 'bg-green';
    };
    if (status == 0){
        return 'bg-red';
    } else {
        return 'bg-gray';
    };
};
function statustext(status){
    if (status == 1){
        return 'Online';
    };
    if (status == 0){
        return 'Offline';
    } else {
        return 'Unknown';
    };
};
function renderstatus(status){
    return '<span class="label '+statusbgcolor(status)+'">'+statustext(status)+'</span>';
};
function mediaicon(mediatype){
  if (mediatype.startsWith('Dedup')){
    return "fa-cubes";
  }
  if (mediatype.startsWith('Tape')){
    return "fa-simplybuilt";
  }
  return "fa-database";
};

function mediacolor(mediatype){
  if (mediatype.startsWith('Dedup')){
    return "bg-maroon";
  }
  if (mediatype.startsWith('Tape')){
    return "bg-aqua";
  }
  return "bg-green";
};

function rendermediatype(mediatype){
  return '<span class="badge '+mediacolor(mediatype)+'"><i class="fa '+mediaicon(mediatype)+'"></i></span>'+mediatype;
};

function volstatusbgcolor(status) {
  switch (status){
    case 'Append':
      return "bg-green";
    case 'Used':
      return "bg-aqua";
    case 'Error':
      return "bg-red";
    case 'Full':
      return "bg-blue";
    case 'Purged':
    case 'Recycle':
      return "bg-yellow";
    case 'Cleaning':
      return "bg-purple-gradient";
  }
  return "bg-gray";
};

function rendervolstatus(volstatus){
  return '<span class="badge '+volstatusbgcolor(volstatus)+'">'+volstatus+'</span>';
};

function rendertaskprogressbar(progress){
  return '<div class="progress">\n<div class="progress-bar progress-bar-primary" style="width: '+progress+'%" role="progressbar" aria-valuenow="'+progress+'" aria-valuemin="0" aria-valuemax="100">\n<span>'+progress+'% Complete</span></div></div>';
};

function rendertaskstatusbadge(status, klass){
  var color = "bg-aqua";
  var text = "Running";
  if (status == 'N'){
    color = "bg-maroon";
    text = "New";
  } else
  if (status == 'E'){
    color = "bg-red";
    text = "Failed";
  } else
  if (status == 'F'){
    color = "bg-green";
    text = "Success";
  };
  if (status == 'C'){
    color = "bg-orange";
    text = "Canceled";
  };
  return '<span class="'+klass+' '+color+'">'+text+'</span>'
};

$.validator.addMethod("componentname", function(value, element) {
  return this.optional(element) || /^[a-z0-9\-_\s]+$/i.test(value);
}, "Name must contain only letters, numbers, dashes or spaces.");

$(function(){
  $("[data-hide]").on("click", function(){
    $(this).closest("." + $(this).attr("data-hide")).hide();
  });
});

function renderuserstatus(active){
  if (active){
    data = ['label-success', 'Active'];
    return renderlabel(data);
  } else {
    data = ['label-danger', 'Locked'];
    return renderlabel(data);
  }
};

function renderusertype(data){
  var superuser = data[0];
  var staff = data[1];
  var param = [];
  if (superuser){
    if (staff){
      param[0] = 'bg-maroon';
      param[1] = 'Superuser!';
    } else {
      param[0] = 'bg-orange';
      param[1] = 'Administrator';
    }
  } else {
    param[0] = 'bg-light-blue';
    param[1] = 'Standard';
  };
  return renderbadge(param);
};

function rendermembers(data, color){
  if (data > 0){
    var param = [];
    param[0] = color;
    param[1] = data;
    return renderbadge(param);
  } else {
    return '-';
  }
};
