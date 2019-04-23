let commentForm = document.querySelector('#comment-form');
let fake_card = document.querySelector('#fake_comment');

let addCreated = function (created) {
    let addedComment = JSON.parse(created);
    let first_card = document.querySelector('.comment');
    let card = fake_card.cloneNode(true);

    card.setAttribute('id', 'comment_' + addedComment.pk);
    card.querySelector(".comment-text").innerHTML = addedComment.text;
    card.querySelector(".comment-author").innerHTML = addedComment.author;
    card.querySelector(".comment-publication-date").innerHTML = addedComment.publication_date;
    card.querySelector(".comment-publication-time").innerHTML = addedComment.publication_time;
    card.querySelector(".comment-last_update-date").innerHTML = addedComment.last_update_date;
    card.querySelector(".comment-last_update-time").innerHTML = addedComment.last_update_time;
    card.querySelector('.comment_update_form').action = addedComment.update_url;
    first_card.parentNode.insertBefore(card, first_card);
    toggleElementHide(card);
    cardAddEventListeners(card);
    commentForm.querySelector("textarea[name='text']").value = ''
};


commentForm.addEventListener('submit', function (event) {
    event.preventDefault();
    data = new FormData(event.target);
    genericPostRequest(event.target.getAttribute("action"), data, addCreated)
});


