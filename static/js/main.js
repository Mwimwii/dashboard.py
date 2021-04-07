var addSiteBtn = document.getElementById('addNeWebsite');
var addSiteDialog = document.getElementById('add-website');
var outputBox = document.querySelector('output');
var saveBtn = document.getElementById('saveBtn');
const hostname = "127.0.0.1:8000"
// Form modal for site modal
const siteForm = document.getElementById("siteModal")

// fuction to upload the website entered in the modal form
function saveWebsite(event){
  let url = "/addsite"
  const formdData = new FormData(siteForm);
  const website = Object.fromEntries(formdData.entries())
  // upload form data
  fetch(url, {
    method: "POST",
    body: JSON.stringify(website),
    headers: {"Content-type": "application/json; charset=UTF-8"}
  })
  .then(response => response.json)
  .then(json => console.log(json))
  .catch(err => alert("Failed to add site"))
}

// "Add new website" button opens the <dialog> modally
addSiteBtn.addEventListener('click', function onOpen() {
  if (typeof addSiteDialog.showModal === "function") {
    addSiteDialog.showModal();
  } else {
    alert("The <dialog> API is not supported by this browser");
  }
});
// "Confirm" button of form triggers "close" on dialog because of [method="dialog"]
addSiteDialog.addEventListener('close', function onClose() {
  outputBox.value = addSiteDialog.returnValue + " button clicked - " + (new Date()).toString();
});
// "save" button saves a website and uploads a fetch
saveBtn.addEventListener('click', saveWebsite);
