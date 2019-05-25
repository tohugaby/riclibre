// Manage like button

let likeBtn = document.querySelector('#like-btn i');
let toggleLikeClass = function () {
    let el = likeBtn
    let likeCssClass = 'fa-star';
    let unLikeCssClass = 'fa-star-o';
    if (el.classList.contains(unLikeCssClass)) {
        el.classList.remove(unLikeCssClass);
        el.classList.add(likeCssClass)
    } else {
        el.classList.remove(likeCssClass);
        el.classList.add(unLikeCssClass)
    }
};


likeBtn.addEventListener('click', function (event) {
    likeBtn.parentElement
    genericGetRequest(event.target.parentElement.getAttribute('data-url'), toggleLikeClass)
});