checkNotifications = function() {
     xhr = new XMLHttpRequest();
     xhr.open("GET","/notifications");
     xhr.onreadystatechange = function(){
          if (xhr.readyState == 4 && xhr.status == 200){
               notifs = JSON.parse(xhr.responseText)
               notifs.forEach(n => {alert(n)})
          }
     }
     xhr.send();
}
setInterval(checkNotifications, 10000)