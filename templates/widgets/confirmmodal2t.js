$('{{ selector }}').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var name = button.data('name'); // Extract info from data-* attributes
    var taskid = button.data('taskid') // Extract info from data-* attributes
    var url = button.data('url');
    // Update the modal's content.
    var modal = $(this);
    modal.find('.modal-title').find('i').text(name);
    modal.find('.modal-title').find('b').text(taskid);
    modal.find('.modal-body').find('i').text(name);
    modal.find('.modal-body').find('u').text(taskid);
    var linkdata = url + taskid + '/';
    modal.find('.confirm').data('url', linkdata);
});
