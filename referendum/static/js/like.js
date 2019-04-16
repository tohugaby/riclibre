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

let genericGetRequest = function (url, callback) {
    const req = new XMLHttpRequest();
    req.onreadystatechange = function (event) {
        if (this.readyState == XMLHttpRequest.DONE) {
            if (this.status === 200) {
                callback()
            } else {
                console.log("Status de la réponse: %d (%s)", this.status, this.statusText)
            }
        }
    };

    req.open('GET', url, true);
    req.send(null)
};


likeBtn.addEventListener('click', function (event) {
    likeBtn.parentElement
    genericGetRequest(event.target.parentElement.getAttribute('data-url'), toggleLikeClass)
});