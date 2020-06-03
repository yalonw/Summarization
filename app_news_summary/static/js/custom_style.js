const checkbox = document.getElementById("daynightswitch");
const body = document.getElementsByTagName("body")[0];
const main = document.getElementsByTagName("main")[0];

const table = document.getElementsByTagName("table");
const thead = document.getElementsByTagName("thead");
var logo_bw = document.getElementById("logo");

checkbox.addEventListener("change", function(){
  body.classList.toggle("day");
  main.classList.toggle("day");

  for (var i = 0; i < table.length; i++) {
    if (table[i].style.color == "rgb(255, 255, 255)") {
      table[i].style.color = "#212529";
      thead[i].style.color = "#212529";
    } else if (table[i].style.color == "rgb(33, 37, 41)") {
      table[i].style.color = "#ffffff";
      thead[i].style.color = "#ffffff";
    } else {
      table[i].style.color = "#212529";
      thead[i].style.color = "#212529";
    }
  };

  if ( logo_bw.src.indexOf("ss_logo_word-white.png") > -1) {
    logo_bw.src = "/static/images/ss_logo.png"
  } else {
    logo_bw.src = "/static/images/ss_logo_word-white.png"
  };
});