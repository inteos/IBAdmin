{% if messages %}
<script>
$(function(){
    $('.messagesbox').fadeTo(5000, 500).slideUp(500,
    function(){
        $(".messagesbox").slideUp(500);
    });
});
</script>
{% endif %}