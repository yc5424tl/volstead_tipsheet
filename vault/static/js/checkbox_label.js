$(function() {
    document.onchange = () => {
        if (event.target.matches('#remember-me')) {
            let parent = (event.target).closest('label');

            if (event.target.checked == true) {
                document.getElementById(parent.id).style.setProperty('color', '#348c9c', undefined);
                document.getElementById(parent.id).style.setProperty('opacity','0.7', undefined);
                document.getElementById(parent.id).style.setProperty('box-shadow', '0 0 3px #eee8d5', undefined);
            }

            else {
                document.getElementById(parent.id).style.setProperty('color', 'white', undefined);
                document.getElementById(parent.id).style.setProperty('box-shadow', '', undefined);
            }
        }
    }
});