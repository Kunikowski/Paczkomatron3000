var packageform = document.getElementById("packageform")
var deletebtn = document.getElementsByClassName("deletebtn")

var showbtn = document.getElementById("showbtn")

function attach_events() {
    showbtn.addEventListener("click", function(ev) {
        if (packageform.className === "signupform"){
            packageform.className = "signupform hidden"
        } else {
            packageform.className = "signupform"
        }
    })
    Array.prototype.slice.call(deletebtn).forEach(element => {
        element.addEventListener("click", function(ev){
            var label = ev.target.parentNode.getElementsByClassName("label")[0].textContent
            var xhr = new XMLHttpRequest();
            xhr.open("DELETE", "/sender/dashboard/" + label);
            xhr.onreadystatechange = function() {
                var DONE = 4;
                var OK = 200;
                if (xhr.readyState == DONE) {
                    if (xhr.status == OK) {
                        location.reload();
                    } else {
                        console.log('Error: ' + xhr.status);
                        alert("Nie można usunąć paczki")
                    }
                }
            }
            xhr.send(null);
            });
        })
}
attach_events()