// Manage like button

let toggleLikeClass = function (targetBtn) {
    let el = targetBtn;
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


let likeButtons = document.querySelectorAll('.like-btn');


likeButtons.forEach(function (btn) {
    btn.addEventListener('click', function (event) {
        let updateAllLike = function () {
            let el = btn.querySelector('i');
            let regex = RegExp('referendum_');
            if (el !== undefined) {
                el.classList.forEach(function (cls) {
                    if (regex.test(cls)) {
                        let targetClassName = '.' + cls;
                        let sameReferendumLikeButtons = document.querySelectorAll(targetClassName);
                        sameReferendumLikeButtons.forEach(function (targetBtn) {
                            toggleLikeClass(targetBtn);
                        })
                    }
                });
            }
        };
        genericGetRequest(btn.getAttribute('data-url'), updateAllLike)
    });
})
