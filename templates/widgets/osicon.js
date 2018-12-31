function set_osicon(value){
  var icon = 'fa fa-server';
  switch (value){
    case 'rhel':
    case 'deb':
      icon = 'fa fa-linux';
      break;
    case 'win32':
    case 'win64':
      icon = 'fa fa-windows';
      break;
    case 'osx':
      icon = 'fa fa-apple'
      break;
    case 'proxmox':
    case 'xen':
    case 'kvm':
    case 'vmware':
      icon = 'fa fa-cloud';
      break;
  };
  return icon;
};