let addCardEventListerner = function () {
    let cards = document.querySelectorAll('.comment');
    cards.forEach((card) => {
        cardAddEventListeners(card)
    });
};

addCardEventListerner();