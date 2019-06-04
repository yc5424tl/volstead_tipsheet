
$(function() {
   document.onchange = () => {
       if (event.target.matches('.select-hours')) {

           let selected_option_value = parseFloat(event.target[(event.target).selectedIndex].value);
           let parent_row = (event.target).closest('.row');

           if (selected_option_value > 0.0) {
               document.getElementById(parent_row.id).style.setProperty('background-color', "#9C4434", undefined);
               document.getElementById(parent_row.id).style.setProperty('opacity', '0.8', undefined);
           }

           else if (selected_option_value === 0.0) {
               document.getElementById(parent_row.id).style.setProperty('background-color', '', undefined);
               document.getElementById(parent_row.id).style.setProperty('opacity', '', undefined);
               document.getElementById(parent_row.id).style.setProperty('color', '', undefined);
           }
       }
   }
});



