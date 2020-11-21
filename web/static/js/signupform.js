var signupform = document.getElementById("signupform")

var formlist = document.getElementById("formlist")

var firstname = document.getElementById("firstname");
var lastname = document.getElementById("lastname");
var username = document.getElementById("username");
var email = document.getElementById("email")
var password = document.getElementById("password");
var repeatpassword = document.getElementById("repeatpassword");
var adress = document.getElementById("adress")
var submitbtn = document.getElementById("submitbtn");

var firstnameerror;
var lastnameerror;
var usernameerror;
var emailerror;
var passworderror;
var adresserror;
var submitbtnerror;

var validfirstname = false;
var validlastname = false;
var validusername = false;
var validpassword = false;
var validemail = false;
var validadress = false;

function create_errors(){
    firstnameerror = formlist.insertBefore(document.createElement("li"), firstname.parentElement.nextElementSibling);
    lastnameerror = formlist.insertBefore(document.createElement("li"), lastname.parentElement.nextElementSibling);
    usernameerror = formlist.insertBefore(document.createElement("li"), username.parentElement.nextElementSibling);
    emailerror = formlist.insertBefore(document.createElement("li"), email.parentElement.nextElementSibling);
    passworderror = formlist.insertBefore(document.createElement("li"), password.parentElement.nextElementSibling);
    adresserror = formlist.insertBefore(document.createElement("li"), adress.parentElement.nextElementSibling);
    submitbtnerror = formlist.insertBefore(document.createElement("li"), submitbtn.parentElement.nextElementSibling);
}

function attach_events() {
    firstname.addEventListener("input", function(ev) {
        if (firstname.value.length > 0 && /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/.test(firstname.value)){
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
        if (lastname.value.length > 0 && /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/.test(lastname.value)){
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
        if (/^[a-z]{3,12}$/.test(username.value))
            checkusername();
        else{
            validusername = false;
            usernameerror.innerText = "Nazwa użytkownika musi się składać z 3-12 małych liter";
            usernameerror.className = "error shown";
        }
    })
    email.addEventListener("input", function(ev) {
        if (email.value.length > 0 && /(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/.test(email.value)){
            validemail = true;
            emailerror.innerText = "";
            emailerror.className = "error";
        }
        else {
            validemail = false;
            emailerror.innerText = "Proszę wpisać poprawny adres email";
            emailerror.className = "error shown";
        }
    })
    password.addEventListener("input", function(ev) {
        validatepassword()
    })
    repeatpassword.addEventListener("input", function(ev) {
        validatepassword()
    })
    adress.addEventListener("input", function(ev) {
        if (adress.value.length > 0){
            validadress = true;
            adresserror.innerText = "";
            adresserror.className = "error";
        }
        else {
            validadress = false;
            adresserror.innerText = "Proszę wpisać adres";
            adresserror.className = "error shown";
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
    xhr.open("GET", "/checklogin/" + username.value);
    xhr.onreadystatechange = function() {
        var DONE = 4;
        var OK = 200;
        if (xhr.readyState == DONE) {
            if (xhr.status == OK) {
                result = xhr.responseText;
                if (result=="available"){
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
    if (password.value.length > 0 && /.{8,}/.test(password.value.trim())){
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
        passworderror.innerText = "Hasło musi się składać z co najmniej 8 znaków";
        passworderror.className = "error shown";
    }
}

function formvalid(){
    if (validfirstname && validlastname && validusername &&  validemail && validpassword &&  validadress )
        return true;
    else
        return false;
}

create_errors();
attach_events();