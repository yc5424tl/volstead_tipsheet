
$(function() {
   document.onchange = () => {
       if (event.target.matches('.select-hours')) {
           let selected_option_value = parseFloat(event.target[(event.target).selectedIndex].value);
           // alert('Selected Option Value = ' + selected_option_value);
           // alert(typeof selected_option_value);
           let parent_row = (event.target).closest('.row');
    /*       let this_parent_row = this.closest('.row');
           alert('this parent row = ' + this_parent_row);
           alert('this_parent_row[0] = ' + this_parent_row[0]);*/
           // alert('parent_row = ' + parent_row);
           // alert('parent_row.id = ' + parent_row.id);
           if (selected_option_value > 0.0) {
               // alert('in selected_option_value > 0.0');
               document.getElementById(parent_row.id).style.setProperty('background-color', "#9C4434", undefined);
               document.getElementById(parent_row.id).style.setProperty('opacity', '0.8', undefined);
               // document.getElementById(parent_row.id).style.setProperty('color', '#000000', undefined);
               // document.getElementById(parent_row.id).css({ 'opacity': '0.8', 'background-color': '#527593' });
               // document.getElementById(parent_row.id).style.backgroundColor = "#5c5750";
               // alert(document.getElementById(parent_row.id));
               // document.getElementById('#' + parent_row.id).style['opacity'] = "1.0";
               // alert('after set to blue');
           }

           else if (selected_option_value === 0.0) {
               // alert('in selected_option_value === 0.0');
               document.getElementById(parent_row.id).style.setProperty('background-color', '', undefined);
               document.getElementById(parent_row.id).style.setProperty('opacity', '', undefined);
               document.getElementById(parent_row.id).style.setProperty('color', '', undefined);
               // document.getElementById(parent_row.id).css({ 'opacity': '0.7', 'background-color': '#5c5750' })
               // alert('in sekected_option_value === 0.0');
               // document.getElementById(parent_row.id).css({ 'opacity': '', 'background-color': ''});
               // document.getElementById('#' + parent_row.id).style.backgroundColor = "";
               // document.getElementById('#' + parent_row.id).style.opacity = "";
               // alert('after set to grey');
           }

           // else {
           //     alert('selected_option_value is not (> or === 0.0)');
           // }
       }
   }
});



// $(function() {
//     alert('in function');
//     let x = document.querySelectorAll(".select-hours");
//         x.forEach(function(sel) {
//             alert('in forEach');
//             alert(sel[sel.selectedIndex].value);
//             x.addEventListener('change', function () {
//                 alert('sel[sel.selectedIndex].value = ' + sel[sel.selectedIndex].value);
//                 alert('in addEventListener');
//                 alert('Selection: ' + sel[sel.selectedIndex].value);
//                 alert('Closest .row = ' + sel.closest('.row'));

//                 let closestRow = sel.closest('.row');
//                 alert(closestRow);
//                 alert(closestRow[0]);
//                 alert('value > 0 = ' + sel[sel.selectedIndex].value > 0.0);
//                 alert('sel val === 0.0 = ' + sel[selectedIndex].value === 0.0);
//                 if (sel[sel.selectedIndex].value<=0.0) {
//                     alert('selection greater than 0.0');
//                     sel.closest('.row').css({'opacity': '1.0'});
//                    alert(ow.attr();
//                 else if (sel[sel.selectedIndex].value === 0.0) {
//                         sel.closest('.row').css({'opacity': '0.7'});
//                         closestRow.style.opacity = "0.7";
//                         alert('selectiobTn === 0.0');}
//                 else {
//                     alert('selection not matched');
//                 }
// /     shifts.forEach(function (shift) {
//
// });
//         shifts.addEventListener("change", function() {
//             let selected_option = item[item.selectedIndex].value;
//             let target_row = item.closest('.row');
//             if (selected_option > 0.0) {
//                 $(target_row).css({ 'opacity': '1.0' });
//                 $(target_row).style.opacity = 1.0;
//                 item.closest('.row').set
//             }
//             else if (selected_option === 0) {
//                 $(target_row).css({ 'opacity': '0.7'});
//                 $(target_row).style.opacity = 0.7;
//             }
//         })
//     }
// })



// $(document).ready(function() {
//     // alert("script loaded ");
//     // let selects =  document.getElementsByClassName('select-hours');
//     // alert('have selects');
//     // alert('selects = ' + selects);
//     Array.from(document.getElementsByClassName('select-hours')).forEach(function (item) {
//         // var items = document.getElementByClassName('select-hours');
//         // for (let item of items) {
//         //     foo.use.item
//         // }
//         alert('select.id = ' + item.id);
//         let selected_option = item[item.selectedIndex].value;
//         alert('selected_option = ' + selected_option );
//         item.addEventListener('change', function() {
//             alert(this[0]);
//             alert(this[1]);
//             alert(this[2]);
//             alert('this = ' + this);
//             alert('this.closest(.row) = ' + this.closest('.row'));
//             alert('change detected');
//             alert('item.selectedIndex.value: ');
//             alert(item[item.selectedIndex].value);
//             // alert('Type: ' + item[item.selectedIndex].value.type);
//             if(item[item.selectedIndex].value > 0.0) {
//                 alert('selectedIndex > 0');
//                 let closestRow = item.closest('.row');
//                 alert('closestRow = ' + closestRow);
//                 alert(closestRow.name)
//                 $(closestRow).css({ opacity: 1 });
//                 alert(closestRow.name)
//                 // item.closest('.row').css('opacity', '1.0');
//                 // item.closest('.row').style.opacity = 1.0;
//             }
//             else if (item[item.selectedIndex].value === 0.0) {
//                 alert('selectedIndex = 0.0');
//                 let closestRow = item.closest('.row');
//                 closestRow.style.opacity = ".7";
//                 // item.closest('.row').setAttribute('opacity', '0.7');
//                 // item.closest('.row').css('opacity', '0.7');
//             }
//         })
//     });
// });
//             alert('have selector:');
//             alert(element);
//         })
//     });
//     alert('selects.type = ' + selects.type);
//     selects.forEach(function() {
//         this.addEventListener('change', function() {
//             alert('event detected');
//             alert('this = ' + this);
//             let selected_option = this.options.selectedIndex.value();
//             alert('selected_option = ' + selected_option);
//         });
//     })
//         alert('this = ' + this);
//         let selected_option = this.options._getSelectedItem();
//         alert('selected_option = ' + selected_option);
//         this.addEventListener('change', function() {
//             let selected_value = selected_option.val();
//             alert('selected_value = ' + selected_value);
//             if(selected_value > 0.0) {
//                 alert('selected_value > 0.0');
//                 alert('this = ' + this);
//                 let element_id = this.id;
//                 alert('this.id = ' + element_id);
//                 let parent_row = this.closest('.row');
//                 alert('parent_row = ' + parent_row);
//                 parent_row.style.opacity = 1.0;
//             }
//             else if (selected_value === 0.0) {
//                 let element_id = this.id;
//                 let parent_row = this.closest('.row');
//                 parent_row.style.opacity = 0.7;
//             }
//         });
//
//     })
// });
//
//     Object.entries(selects).map(function(obj) {
//         // alert("adding event listeners");
//         // alert('obj[0]: ' + obj[0]);
//         // alert('obj[1]: ' + obj[1]);
//         let options = obj[1].options;
//         // alert('Options: ' + options);
//         let selected_option = options[obj[1].selectedIndex];
//         // alert('Selected Option: ' + selected_option);
//         let selected_value = selected_option.value;
//         // alert('Selected Value: ' + selected_value);
//         obj[1].addEventListener('change', function() {
//             let selected_opt = obj[1].options[obj[1].selectedIndex].value;
//             alert("selected option: " + selected_opt);
//             if(selected_opt > 0.0) {
//                 alert('this = ' + this);
//                 alert('selected_opt is > 0.0');
//                 // alert('this.parent ' + this.parent);
//                 alert('this.ID ' + this.ID);
//                 let target = document.getElementById(this.ID);
//                 alert('target.ID = ' + target.ID);
//
//                 // alert(this.parent().parent());
//                 alert('after opacity');
//                 // $(this).closest('.row').css('opacity', '1');
//                 // alert('$(this).closest(): ' + $(this).closest('.form-group.row.role-hours.no-gutters'));
//                 //
//                 // let row = this.closest('.row');
//                 // if(row) {
//                 //     alert('Row: ' + row);
//                 // }
//                 // else {
//                 //     alert('No .row found');
//                 // }
//
//                 // row.css('opacity', 1);
//                 //
//                 // this.closest('.row').css('opacity', 1);
//                 // this.closest('.form-group.row.role-hours.no-gutters').css('opacity', 1);
//             }
//         })
//     })
// });