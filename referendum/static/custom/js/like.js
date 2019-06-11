// Manage like button

let likeButtons = document.querySelectorAll('.like-btn i');


likeButtons.forEach(function (btn) {
    let toggleLikeClass = function () {
        let el = btn;
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

    btn.addEventListener('click', function (event) {


        btn.parentElement;
        genericGetRequest(event.target.parentElement.getAttribute('data-url'), toggleLikeClass)
    });
})
