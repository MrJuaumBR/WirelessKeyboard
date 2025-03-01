// script.js
var controlCheckbox = document.getElementById('control');
var shiftCheckbox = document.getElementById('shift');
var altCheckbox = document.getElementById('alt');


const volumeSlider = document.getElementById('volume-slider');
const volumeValue = document.getElementById('volume-value');

volumeSlider.addEventListener('input', (e) => {
  const volume = e.target.value;
  volumeValue.textContent = `${volume}%`;
  // Send the volume value to the Flask server
  fetch('/update_volume', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ volume: volume })
  });
});

const buttons_keys = document.getElementsByName('key');
for (const button of buttons_keys) {
  button.addEventListener('click', (e) => {
    const key = e.target.textContent;
    // Send the key to the Flask server
    fetch('/key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ key: key, control: controlCheckbox.checked, shift: shiftCheckbox.checked, alt: altCheckbox.checked })
    });
  });
}