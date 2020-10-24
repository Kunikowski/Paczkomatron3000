var signupform = document.getElementById("signupform")

var firstname = document.getElementById("firstname");
var lastname = document.getElementById("lastname");
var username = document.getElementById("username");
var password = document.getElementById("password");
var repeatpassword = document.getElementById("repeatpassword");
var image = document.getElementById("image")
var submitbtn = document.getElementById("submitbtn");

var validfirstname = false;
var validlastname = false;
var validusername = false;
var validpassword = false;
var validimage = true;

function attach_events() {
    firstname.addEventListener("change", function(ev) {
        if (firstname.value.length > 0)
            validfirstname = true;
        else {
            validfirstname = false;
            alert("Proszę wpisać imię");
        }
    })
    lastname.addEventListener("change", function(ev) {
        if (lastname.value.length > 0)
            validlastname = true;
        else{
            validlastname = false;
            alert("Proszę wpisać nazwisko");
        }
    })
    username.addEventListener("change", function(ev) {
        if (username.value.length > 0)
            checkusername();
        else{
            validusername = false;
            alert("Proszę wpisać nazwę użytkownika");
        }
    })
    password.addEventListener("change", function(ev) {
        validatepassword()
    })
    repeatpassword.addEventListener("change", function(ev) {
        validatepassword()
    })
    submitbtn.addEventListener("click", function(ev){
        if (formvalid())
            signupform.submit();
        else
            alert("Proszę poprawnie wypełnić formularz");
    })
}

function checkusername() {
    validusername = false;
    var result;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "https://infinite-hamlet-29399.herokuapp.com/check/" + username.value);
    xhr.onreadystatechange = function() {
        var DONE = 4;
        var OK = 200;
        if (xhr.readyState == DONE) {
            if (xhr.status == OK) {
                result = JSON.parse(xhr.responseText);
                console.log(result);
                if (result[username.value]=="available"){
                    validusername = true;
                } else {
                    alert("Nazwa użytkownika " + username.value + " jest już zajęta");
                }
            } else {
                console.log('Error: ' + xhr.status);
                alert("Nie można sprawdzić dostępności nazwy użytkownika");
            }
        }
    }
    xhr.send(null);
}

function validatepassword() {
    if (password.value.length > 0){
        if (repeatpassword.value.length > 0){
            if (password.value.localeCompare(repeatpassword.value) == 0) {
                validpassword = true;
            } else {         
                validpassword = false;
                alert("Wpisane hasła nie są takie same")
            }
        } else {
            validpassword = false;
        }
    } else {
        validpassword = false;
        alert("Proszę wpisać hasło");
    }
}

function formvalid(){
    if (validfirstname && validlastname && validusername && validpassword &&  validimage)
        return true;
    else
        return false;
}

attach_events();