let txt = document.getElementById("txt");
let a = document.getElementById("send");

function update() {
  let message = "Following publications should be tagged as KiKIT and added to KITopen if necessary:\n\n";
  console.log(message);

  let sel = document.querySelectorAll("input:checked");

  for(ckb of sel) {
    let title = ckb.getAttribute("x-title");
    let doi = ckb.getAttribute("x-doi");
    let kit_id = ckb.getAttribute("x-kitid");
    message += "\n" + doi + "\t" + kit_id + "\t" + title;
  }

  a.href = encodeURI("mailto:weigl@kit.edu?subject=KiKIT-Tagging&body="+message);
  txt.value = message;
  console.log(message);
}

function selectAll() {
  document.querySelectorAll("input")
    .forEach(x => x.checked = true);
  update();
}

document.querySelectorAll("input")
  .forEach(x => x.onchange = update);
