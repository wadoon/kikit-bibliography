let txt = document.getElementById("txt");

function update() {
  let message = "Liebes KITopen-Team,\n\n";
  console.log(message);

  let sel = document.querySelectorAll("input:checked");

  for(ckb of sel) {
    let txt = sel.parentElement.nextElementSibling.innerText;

    message += "  * " + txt;
  }


  message += "Freundliche Grüße, \n\n " + PI_NAME;
  txt.value = message;
}

document.querySelectorAll("input")
  .forEach(x => x.onchange = update);
