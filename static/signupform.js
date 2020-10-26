var signupform = document.getElementById("signupform")

var firstname = document.getElementById("firstname");
var lastname = document.getElementById("lastname");
var username = document.getElementById("username");
var password = document.getElementById("password");
var repeatpassword = document.getElementById("repeatpassword");
var image = document.getElementById("image")
var submitbtn = document.getElementById("submitbtn");

var firstnameerror = document.getElementById("firstnameerror")
var lastnameerror = document.getElementById("lastnameerror")
var usernameerror = document.getElementById("usernameerror")
var passworderror = document.getElementById("passworderror")
var repeatpassworderror = document.getElementById("repeatpassworderror")
var imageerror = document.getElementById("imageerror")
var submitbtnerror = document.getElementById("submitbtnerror")

var validfirstname = false;
var validlastname = false;
var validusername = false;
var validpassword = false;
var validimage = false;

function attach_events() {
    firstname.addEventListener("input", function(ev) {
        if (firstname.value.length > 0 && /[A-Z{PL}][a-z{pl}]+/.test(firstname.value)){
            validfirstname = true;
            firstnameerror.innerText = "";
            firstnameerror.className = "error";
        }
        else {
            validfirstname = false;
            firstnameerror.innerText = "Imię musi rozpoczynać się wielką literą a poza tym składać się z samych małch liter";
            firstnameerror.className = "error shown";
        }
    })
    lastname.addEventListener("input", function(ev) {
        if (lastname.value.length > 0 && /[A-Z{PL}][a-z{pl}]+/.test(lastname.value)){
            validlastname = true;
            lastnameerror.innerText = "";
            lastnameerror.className = "error";
        }
        else {
            validlastname = false;
            lastnameerror.innerText = "Nazwisko musi rozpoczynać się wielką literą a poza tym składać się z samych małch liter";
            lastnameerror.className = "error shown";
        }
    })
    username.addEventListener("input", function(ev) {
        if (/[a-z]{3,12}/.test(username.value))
            checkusername();
        else{
            validusername = false;
            usernameerror.innerText = "Nazwa użytkownika musi się składać z 3-12 małych liter";
            usernameerror.className = "error shown";
        }
    })
    password.addEventListener("input", function(ev) {
        validatepassword()
    })
    repeatpassword.addEventListener("input", function(ev) {
        validatepassword()
    })
    image.addEventListener("input", function(ev) {
        if (image.files.length > 0){
            validimage = true;
            imageerror.innerText = "";
            imageerror.className = "error";
        }
        else {
            validimage = false;
            imageerror.innerText = "Proszę wgrać poprawne zdjęcie w formacie .png lub .jpg";
            imageerror.className = "error shown";
        }
    })
    submitbtn.addEventListener("click", function(ev){
        if (formvalid()){  
            submitbtnerror.innerText = "";
            submitbtnerror.className = "error";
            signupform.submit();
        }
        else{
            submitbtnerror.innerText = "Proszę wypełnić wszystkie pola formularza";
            submitbtnerror.className = "error shown";
        }
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
                if (result[username.value]=="available"){
                    validusername = true;
                    usernameerror.innerText = "";
                    usernameerror.className = "error";
                } else {
                    usernameerror.innerText = "Nazwa użytkownika " + username.value + " jest już zajęta";
                    usernameerror.className = "error shown";
                }
            } else {
                console.log('Error: ' + xhr.status);
                usernameerror.innerText = "Nie można sprawdzić dostępności nazwy użytkownika";
                usernameerror.className = "error shown";
                
            }
        }
    }
    xhr.send(null);
}

function validatepassword() {
    if (password.value.length > 0 && /[A-Za-z]{8,}/.test(password.value)){
        if (password.value.localeCompare(repeatpassword.value) == 0) {
            validpassword = true;
            passworderror.innerText = "";
            passworderror.className = "error";
        } else {         
            validpassword = false;
            passworderror.innerText = "Wpisane hasła nie są takie same";
            passworderror.className = "error shown";
        }
    } else {
        validpassword = false;
        passworderror.innerText = "Hasło musi się składać z co najmniej 8 liter";
        passworderror.className = "error shown";
    }
}

function formvalid(){
    if (validfirstname && validlastname && validusername && validpassword &&  validimage)
        return true;
    else
        return false;
}

attach_events();