// script.js
let device;
let server;
let bluetoothCharacteristic;

document.getElementById('connect-button').addEventListener('click', async () => {
    const button = document.getElementById('connect-button');
    const statusMessage = document.getElementById('status-text');
    const statutIndicator = document.getElementById('status-indicator');
    const deviceName = document.getElementById('device-name').value;

    if (button.textContent === 'Connect') {
        statusMessage.textContent = 'Status: Connection on going';

        try {
            // Request Bluetooth device with the specified name           
            device = await navigator.bluetooth.requestDevice({
                filters: [{ name: deviceName }]
            });

            if (device.name === deviceName) {
                // Connect to the GATT server
                server = await device.gatt.connect();
                console.log('Connected to', device.name);
                statusMessage.textContent = `Status: Connected to ${device.name}`;
                statutIndicator.classList.remove('disconnected');
                statutIndicator.classList.add('connected')
                button.textContent = 'Disconnect';
            } else {
                statusMessage.textContent = 'Status: Device not found';
            }
        } catch (error) {
            statusMessage.textContent = 'Status: Connection failed';
            statutIndicator.classList.remove('disconnected')
            statutIndicator.classList.add('failed')
        }
    } else if (button.textContent === 'Disconnect') {
        if (device && server) {
            // Disconnect from the GATT server
            server.disconnect();
            statusMessage.textContent = 'Status: Disconnected';
            button.textContent = 'Connect';
            statutIndicator.classList.remove('connected', 'failed')
            statutIndicator.classList.add('disconnected')
        }
    }
});

const bleRemote = document.getElementById('ble-remote');
const directionContainer = document.getElementById('direction-container');

bleRemote.addEventListener('change', () => {
    if (bleRemote.checked) {
        directionContainer.classList.add('show');
    } else {
        directionContainer.classList.remove('show');
    }
});


async function sendBluetoothCommand(commandString) {
    const serviceUuid = 'your-service-uuid'; // Replace with actual UUID
    const characteristicUuid = 'your-characteristic-uuid'; // Replace with actual UUID

    try {
        if (!device || !server || !device.gatt.connected) {
            showError('Device is not connected');
            return;
        }

        // If the characteristic isn’t cached yet, retrieve it
        if (!bluetoothCharacteristic) {
            const service = await server.getPrimaryService(serviceUuid);
            bluetoothCharacteristic = await service.getCharacteristic(characteristicUuid);
        }

        // Convert the command to bytes
        const encoder = new TextEncoder();
        const commandBytes = encoder.encode(commandString);

        // Write the value
        await bluetoothCharacteristic.writeValue(commandBytes);
        console.log('Command sent:', commandString);
    } catch (error) {
        showError('Failed to send Bluetooth command:');
    }
}

window.addEventListener('beforeunload', () => {
    if (device && server) {
        // Disconnect from the GATT server before unloading the page
        server.disconnect();
        statusMessage.classList.remove('connected', 'failed')
        statusMessage.classList.add('disconnected')
        console.log('Disconnected from', device.name);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.title = 'Mon STage de Seconde';
});


function showError(message) {
    const alertBox = document.getElementById('error-alert');
    alertBox.textContent = `⚠️ ${message}`;
    alertBox.classList.remove('hidden');
    alertBox.classList.add('show');

setTimeout(() => {
    alertBox.classList.remove('show');
    setTimeout(() => {
    alertBox.classList.add('hidden');
    }, 400);
}, 4000);
}