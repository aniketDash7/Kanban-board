const deadlineForm = document.querySelector('#deadlineCatch');
const selectorForm = document.querySelector('#selector');


selectorForm.addEventListener('change',function(){

    if (selectorForm.value == 'backlog' || selectorForm.value == 'todo' || selectorForm.value == 'done' || selectorForm.value == 'doing' ){
        deadlineForm.style.display = 'block';
    }else{
        deadlineForm.style.display = 'none';
    }

});
