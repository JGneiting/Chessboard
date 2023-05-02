// Get references to the Set White and Set Black buttons
const setWhiteBtn = document.querySelectorAll('#setWhiteBtn');
const setBlackBtn = document.querySelectorAll('#setBlackBtn');
const whiteHuman = document.getElementById('white-human-checkbox');
const blackHuman = document.getElementById('black-human-checkbox');
const whiteEngineName = document.getElementById('whiteName');
const blackEngineName = document.getElementById('blackName');
const whiteELO = document.getElementById('whiteELO');
const blackELO = document.getElementById('blackELO');
const whiteSection = document.getElementById("whiteSection");
const blackSection = document.getElementById("blackSection");
const launchBtn = document.getElementById("launch-button");
const autoplayBox = document.getElementById("autoplay-checkbox");

autoplayBox.addEventListener('change', function() {
    const xhr = new XMLHttpRequest();
      xhr.open('POST', '/set_autoplay');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"autoplay": this.checked}));
});

// Add checkbutton event listeners
whiteHuman.addEventListener('change', function() {
  if (this.checked) {
    console.log('Checkbox is checked');
    whiteSection.style.display = "none";
  } else {
    console.log('Checkbox is not checked');
    whiteSection.style.display = "block";
  }

  // Send an AJAX request to the Python Flask app
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/set_white_human');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"human": this.checked}));
});

blackHuman.addEventListener('change', function() {
  if (this.checked) {
    console.log('Checkbox is checked');
    blackSection.style.display = "none";
  } else {
    console.log('Checkbox is not checked');
    blackSection.style.display = "block";
  }

  // Send an AJAX request to the Python Flask app
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/set_black_human');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"human": this.checked}));
});

// Add event listeners to the Set White and Set Black buttons
setWhiteBtn.forEach(button => {
  button.addEventListener('click', () => {
    // Get the name of the currently selected engine
    console.log("Set White");
    const enginePath = button.dataset.engine;
    const engineName = button.dataset.name;
    const engineELO = button.dataset.elo;

    // Check the human checkbox indicator
    if (!whiteHuman.checked) {
      console.log("Configuring Properties");
      whiteEngineName.innerHTML = "Name: " + engineName;
      whiteELO.innerHTML = "ELO: " + engineELO;

      // Send an AJAX request to the Python Flask app
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/set_white');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"engineName": enginePath}));
    }
    });
});

setBlackBtn.forEach(button => {
  button.addEventListener('click', () => {
    // Get the name of the currently selected engine
    console.log("Set Black");
    const enginePath = button.dataset.engine;
    const engineName = button.dataset.name;
    const engineELO = button.dataset.elo;

    // Check the human checkbox indicator
    if (!blackHuman.checked) {
      console.log("Configuring Properties");
      blackEngineName.innerHTML = "Name: " + engineName;
      blackELO.innerHTML = "ELO: " + engineELO;

      // Send an AJAX request to the Python Flask app
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/set_black');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"engineName": enginePath}));
    }
    });
});

launchBtn.addEventListener('click', () => {
  // Send an AJAX request to the Python Flask app
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/launch_game');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({"launch": "True"}));
});
