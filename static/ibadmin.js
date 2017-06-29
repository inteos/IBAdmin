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

function jobtypetext(type){
  switch (type){
  case 'B':
    return "Backup";
  case 'R':
    return "Restore";
  case 'D':
    return "Admin";
  case 'C':
    return "Copied";
  case 'c':
    return "CopyJob";
  case 'M':
    return "Migrated";
  case 'g':
    return "Migration";
  case 'V':
    return "Verify";
  case 'V':
    return "Verify";
  case 'S':
    return "ScanJob";
  default:
    return "Unknown";
  };
};

function jobleveltext(level,type){
  if (type == 'D' || type == 'Admin' || (level == ' ' && type == '')){
    return "Admin";
  }
  if (type == 'R' || type == 'Restore'){
    return "Restore";
  }
  switch (level){
  case 'F':
  case 'Full':
    return "Full";
  case 'D':
  case 'Differential':
    return "Diff";
  case 'I':
  case 'Incremental':
    return "Incr";
  case 'B':
    return "Base";
  case 'f':
    return "VFull";
  case 'S':
    return "Since";
  case 'C':
    return "Ver2Cat";
  case 'O':
    return "Vol2Cat";
  case 'd':
    return "Disk2Cat";
  case 'A':
    return "VerData";
  default:
    return "Unknown";
  };
};

function joblevelbgcolor(level,type){
  if (type == 'D' || type == 'Admin' || type == ''){
    return "bg-maroon";
  }
  if (type == 'R' || type == 'Restore'){
    return "bg-purple";
  }
  if (level == 'I' || level == 'Incremental'){
      return "label-info";
  }
  if (level == 'D' || level == 'Differential'){
      return "label-success";
  }
  return "label-primary";
};

function jobtypebgcolor(type) {
  switch (type){
  case 'B':
  case 'Backup':
    return "bg-aqua";
  case 'R':
    return "bg-purple";
  case 'D':
    return "bg-maroon";
  case 'C':
    return "bg-teal";
  case 'c':
    return "bg-aqua";
  case 'M':
    return "bg-aqua";
  case 'g':
    return "bg-aqua";
  case 'V':
    return "bg-aqua";
  case 'V':
    return "bg-aqua";
  case 'S':
    return "bg-aqua";
  default:
    return "bg-gray";
  };
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

function jobstatustext(status,errors) {
  if (typeof status !== 'undefined'){
    switch (status){
    case 'A':
      return 'Canceled';
    case 'C':
    case 'F':
    case 'S':
    case 'M':
    case 'm':
    case 's':
    case 'j':
    case 'c':
    case 'd':
    case 't':
    case 'p':
      return 'Queued';
    case 'E':
    case 'f':
      return 'Error';
    case 'I':
      return 'Incomplete';
    case 'R':
      return 'Running';
    case 'T':
      if (errors < 1){
        return 'Success';
      }
    case 'W':
      return 'Warning';
    default:
      return 'Unknown';
    }
  }
};

function jobstatus_running_bgcolor(stat) {
  if (stat > 0){
      return 'bg-aqua';
  }
  return 'bg-gray';
};

function jobstatus_cancel_bgcolor(stat) {
  if (stat > 0){
      return 'bg-fuchsia';
  }
  return 'bg-gray';
};

function jobstatus_queued_bgcolor(stat) {
  if (stat > 0){
      return 'bg-orange';
  }
  return 'bg-gray';
};

function jobstatus_finished_bgcolor(stat) {
  if (stat > 0){
      return 'bg-green';
  }
  return 'bg-gray';
};

function jobstatus_error_bgcolor(stat) {
  if (stat > 0){
      return 'bg-red';
  }
  return 'bg-gray';
};

function jobstatus_warning_bgcolor(stat) {
  if (stat > 0){
      return 'bg-yellow';
  }
  return 'bg-gray';
};

function jobstatusbgcolor(status,errors) {
  if (typeof status !== 'undefined'){
    switch (status){
    case 'A':
      return jobstatus_cancel_bgcolor(1);
    case 'C':
    case 'F':
    case 'S':
    case 'M':
    case 'm':
    case 's':
    case 'j':
    case 'c':
    case 'd':
    case 't':
    case 'p':
      return jobstatus_queued_bgcolor(1);
    case 'E':
    case 'f':
      return jobstatus_error_bgcolor(1);
    case 'I':
      return "bg-teal";
    case 'R':
      return jobstatus_running_bgcolor(1);
    case 'T':
      if (errors < 1){
          return jobstatus_finished_bgcolor(1);
      }
    case 'W':
      return jobstatus_warning_bgcolor(1);
    }
  }
  return "bg-gray";
};

function renderlevelbadge(level,type){
  return '<span class="badge '+joblevelbgcolor(level,type)+'">'+jobleveltext(level,type)+'</span>';
};

function rendererrorsnr(errors,status){
  if (status == 'A'){
      return '<span class="badge '+jobstatus_cancel_bgcolor(1)+'">'+jobstatustext(status,errors)+'</span>';
  }
  return '<span class="badge '+jobstatus_error_bgcolor(errors)+'">'+errors+'</span>';
};

function renderwarningnr(errors,status){
  if (status == 'A'){
      return '<span class="badge '+jobstatus_cancel_bgcolor(1)+'">'+jobstatustext(status,errors)+'</span>';
  }
  return '<span class="badge '+jobstatus_warning_bgcolor(errors)+'">'+errors+'</span>';
};

function renderstatuslabel(status,errors){
  return '<span class="label '+jobstatusbgcolor(status,errors)+'">'+jobstatustext(status,errors)+'</span>';
};

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

function osbgcolor(value){
    // Linux
    if (value == 'rhel'){
        return "bg-red";
    };
    if (value == 'deb'){
        return "bg-orange";
    };
    // Windows
    if (value == 'win32' || value == 'win64'){
        return "bg-teal";
    };
    // OSX
    if (value == 'osx'){
        return "bg-gray";
    };
    // Solaris
    if (value == 'solsparc' || value == 'solintel'){
        return "bg-aqua";
    };
    // AIX
    if (value == 'aix'){
        return "bg-green";
    };
    // HP-UX
    if (value == 'hpux'){
        return "bg-orange";
    };
    return "bg-primary";
};

function ostext(value){
    if (value == 'rhel'){
        return "RHEL/Centos";
    };
    if (value == 'deb'){
        return "Debian/Ubuntu";
    };
    if (value == 'win32'){
        return "Windows 32bit";
    };
    if (value == 'win64'){
        return "Windows 64bit";
    };
    if (value == 'osx'){
        return "MacOS X";
    };
    if (value == 'solsparc'){
        return "Solaris SPARC";
    };
    if (value == 'solintel'){
        return "Solaris x86";
    };
    if (value == 'aix'){
        return "AIX";
    };
    if (value == 'hpux'){
        return "HP-UX";
    };
    return "Unknown";
};

function renderosbadge(os){
    return '<span class="badge '+osbgcolor(os)+'">'+ostext(os)+'</span>';
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
