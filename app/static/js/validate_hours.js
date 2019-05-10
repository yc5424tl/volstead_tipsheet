$(document).ready(function() {
    alert('script loaded');
    var total_hours = 0;
    $('#shift-details-form').submit(function(evt) {
    // $('#submit-button').onSelect(function(evt) {
        alert('in form submitted function');
        $('.select-hours').each(function(){
            var value = $(this).closest("option:selected").text();
                alert(value);
                total_hours += value;
                alert('Total Hours: ' + total_hours);
            });

        // $('.select-hours').forEach(function() {
        //     alert('in for each ');
        //     // var selection = $(this).options[slct.selectedIndex].value;
        //     var selection = $(this).options[$(this).selectedIndex].value;
        //     total_hours += selection;
        //     alert('Selection: ' + selection);
        //     alert('Total Hours: ' + total_hours);
        //});
        alert('after for each');
        check_total_hours(total_hours, evt);

    })
});

function check_total_hours(hours, event) {
    alert('Hours: ' + hours);
    if(hours === 0) {
            alert('in if loop');
            event.preventDefault();
            alert("Tip Hours Cannot Be Zero");
            window.history.back();
        }
}

