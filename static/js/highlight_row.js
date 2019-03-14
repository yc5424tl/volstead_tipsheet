$(document).ready(function() {
    alert("script loaded ");
    let selects = document.getElementsByClassName('select-hours');
    Object.entries(selects).map(function(obj) {
        alert("adding event listeners");
        alert('obj[0]: ' + obj[0]);
        alert('obj[1]: ' + obj[1]);
        obj[1].addEventListener(onchange, function() {
            let selected_opt = obj[1].options[obj[1].selectedIndex].value;
            alert("selected option: " + selected_opt);
            if(selected_opt > 0.0) {
                alert('selected_opt is > 0.0');
                obj[1].closest('.row').setAttribute('opacity', '1')
            }
        })
    })
});