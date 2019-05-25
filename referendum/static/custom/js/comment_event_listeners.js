let cardAddEventListeners = function (comment) {
    let updateButton = comment.querySelector('.update_button');
    let updateSubmit = comment.querySelector('.update_submit');
    let cancelUpdate = comment.querySelector('.cancel_update');
    let commentUpdateForm = comment.querySelector('.comment_update_form');
    // set initial data for update form.
    commentUpdateForm.querySelector("textarea[name='text']").innerHTML = comment.querySelector(".comment-text").innerHTML;

    // Hide or show several update elements
    let toggleUpdateForm = function () {
        toggleElementHide(updateButton);
        toggleElementHide(updateSubmit);
        toggleElementHide(cancelUpdate);
        toggleElementHide(commentUpdateForm)
    };

    // apply update on comment card.
    let applyUpdate = function (updated) {
        let updatedComment = JSON.parse(updated);
        comment.querySelector(".comment-text").innerHTML = updatedComment.text;
        comment.querySelector(".comment-last_update-date").innerHTML = updatedComment.last_update_date;
        comment.querySelector(".comment-last_update-time").innerHTML = updatedComment.last_update_time;
    };

    // set event on update button
    if (updateButton !== null) {
        updateButton.addEventListener('click', function (event) {
            toggleUpdateForm()
        })
    }
    // set event listener on submit update button
    if (updateSubmit !== null) {
        updateSubmit.addEventListener('click', function (event) {
            toggleUpdateForm();
            let url = commentUpdateForm.action;
            let data = new FormData(commentUpdateForm);
            genericPostRequest(url, data, applyUpdate)
        })
    }
    if (cancelUpdate !== null) {
        cancelUpdate.addEventListener('click', function (event) {
            toggleUpdateForm();
        })
    }
};
