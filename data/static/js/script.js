const controlCheckbox = document.getElementById('control');
const shiftCheckbox = document.getElementById('shift');
const altCheckbox = document.getElementById('alt');


const buttons_keys = document.getElementsByName('key');
for (const button of buttons_keys) {
  button.addEventListener('click', (e) => {
    // Send the key to the Flask server
    fetch('/api/key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ key: e.target.value, control: controlCheckbox.checked, shift: shiftCheckbox.checked, alt: altCheckbox.checked })
    });
  });
}

function update_volume(volume) {
  const volumeValue = document.getElementById('volume-value');
  volumeValue.textContent = `${volume}%`;
  fetch('/api/update_volume', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ volume: volume })
  });
}

function genQRCode() {
    const qrcode = new QRCode(document.getElementById("barcode"), {
        text: `http://${document.location.host}/`,
        width: 64,
        height: 64,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });

    qrcode.mak
}

genQRCode();