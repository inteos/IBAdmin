function renderclientlink(client){
  if (client != null){
    return '<a href="{% url 'clientsinfo_rel' %}'+client+'/">'+client+'</a>';
  } else {
    return '<i>Internal</i>';
  };
};
function renderstoragelink(storage){
  if (storage != null){
    return '<a href="{% url 'storageinfo_rel' %}'+storage+'/">'+storage+'</a>';
  } else {
    return '<i>N/A</i>';
  };
};
function renderjoblink(job){
  return '<a href="{% url 'jobsinfo_rel' %}'+job+'/">'+job+'</a>';
};