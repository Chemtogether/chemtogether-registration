$(".max_length_indicator").each(function() {
    $(this).keyup( updateCharacterIndicator )
    $(this).keyup()
});

function updateCharacterIndicator() {
    name = $(this).attr("name")
    max_length = $(this).attr("maxlength")
    current_length = this.value.length

    if ($('#max_length_indicator_'+String(name)).length) {
        $('#max_length_indicator_'+String(name)).text("Characters: "+String(current_length)+"/"+String(max_length))
    } else {
        $(this).after("<small class='' style='display:block' id='max_length_indicator_"+String(name)+"'>Characters: "+String(current_length)+"/"+String(max_length)+"</small>")
    }
}