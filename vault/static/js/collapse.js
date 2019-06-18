$(function() {
    document.onchange = () => {
        if (event.target.matches('#collapse-toggle')) {
            $('.collapse').toggle();
        }
    }
});


