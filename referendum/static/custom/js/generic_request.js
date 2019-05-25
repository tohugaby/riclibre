// Generic ajax Requests functions used by other scripts

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


let genericPostRequest = function (url, data, callback) {
    const req = new XMLHttpRequest();
    req.onreadystatechange = function (event) {
        if (this.readyState == XMLHttpRequest.DONE) {
            if (this.status === 200) {
                callback(this.responseText);
            } else {
                console.log("Status de la réponse: %d (%s)", this.status, this.statusText)
            }
        }
    };
    req.open('POST', url, true);
    req.send(data)
};