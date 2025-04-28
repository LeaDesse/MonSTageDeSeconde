let device;
let server;
let bluetoothCharacteristic;
let isOperationInProgress = false; // Initialize the flag

document.getElementById('connect-button').addEventListener('click', async () => {
    const button = document.getElementById('connect-button');
    const statusMessage = document.getElementById('status-text');
    const statutIndicator = document.getElementById('status-indicator');
    const deviceName = document.getElementById('device-name').value;

    if (button.textContent === 'Connect') {
        statusMessage.textContent = 'Status: Connection on going';

        try {
            // Request Bluetooth device with the specified name and optional services
            device = await navigator.bluetooth.requestDevice({
                filters: [{ name: deviceName }],
                optionalServices: ['6e400001-b5a3-f393-e0a9-e50e24dcca9e'] // Nordic UART Service UUID
            });

            if (device.name === deviceName) {
                // Connect to the GATT server
                server = await device.gatt.connect();
                console.log('Connected to', device.name);
                statusMessage.textContent = `Status: Connected to ${device.name}`;
                statutIndicator.classList.remove('disconnected');
                statutIndicator.classList.add('connected');
                button.textContent = 'Disconnect';
            } else {
                statusMessage.textContent = 'Status: Device not found';
            }
        } catch (error) {
            statusMessage.textContent = 'Status: Connection failed';
            statutIndicator.classList.remove('disconnected');
            statutIndicator.classList.add('failed');
            console.error('Connection error:', error);
        }
    } else if (button.textContent === 'Disconnect') {
        if (device && server) {
            // Disconnect from the GATT server
            server.disconnect();
            statusMessage.textContent = 'Status: Disconnected';
            button.textContent = 'Connect';
            statutIndicator.classList.remove('connected', 'failed');
            statutIndicator.classList.add('disconnected');
            console.log('Disconnected from', device.name);
        }
    }
});

// Select all switches
const switches = document.querySelectorAll('.switch-label input[type="checkbox"]');
const bleRemote = document.getElementById('ble-remote');
const irRemote = document.getElementById('ir-remote');
const lineFollowing = document.getElementById('line-following');
const directionContainer = document.getElementById('direction-container');

// Add an event listener to each switch
switches.forEach(switchElement => {
    switchElement.addEventListener('change', () => {
        if (switchElement.checked) {
            // Deactivate all other switches
            switches.forEach(otherSwitch => {
                if (otherSwitch !== switchElement) {
                    otherSwitch.checked = false;
                }
            });

            // Send mode command based on the switch activated
            if (bleRemote.checked) {
                sendBluetoothCommand('Mode BLE');
                directionContainer.classList.add('show');
            } else if (irRemote.checked) {
                sendBluetoothCommand('Mode IR');
                directionContainer.classList.remove('show');
            } else if (lineFollowing.checked) {
                sendBluetoothCommand('Mode Line');
                directionContainer.classList.remove('show');
            }
        }
    });
});

// Debounce function to limit how often a function can be called
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Add event listeners for directional buttons with debouncing
const directionButtons = document.querySelectorAll('.direction-button');

directionButtons.forEach(button => {
    button.addEventListener('mousedown', debounce(() => {
        const command = button.id.charAt(0).toUpperCase() + ' pressed';
        sendBluetoothCommand(command);
    }, 300));

    button.addEventListener('mouseup', debounce(() => {
        const command = button.id.charAt(0).toUpperCase() + ' released';
        sendBluetoothCommand(command);
    }, 300));
});

async function sendBluetoothCommand(commandString) {
    const serviceUuid = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'; // Nordic UART Service UUID
    const characteristicUuid = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'; // TX Characteristic UUID

    if (isOperationInProgress) {
        showError('GATT operation already in progress');
        return;
    }

    try {
        if (!device || !server || !device.gatt.connected) {
            showError('Device is not connected');
            return;
        }

        isOperationInProgress = true;

        // If the characteristic isn’t cached yet, retrieve it
        if (!bluetoothCharacteristic) {
            const service = await server.getPrimaryService(serviceUuid);
            bluetoothCharacteristic = await service.getCharacteristic(characteristicUuid);
        }

        // Convert the command string to bytes
        const encoder = new TextEncoder();
        const data = encoder.encode(commandString);

        // Write the bytes to the characteristic
        await bluetoothCharacteristic.writeValue(data);
        console.log('Command sent:', commandString);
    } catch (error) {
        showError('Failed to send Bluetooth command:', error);
        console.error('Send command error:', error);
    } finally {
        isOperationInProgress = false;
    }
}

function showError(message, error) {
    const alertBox = document.getElementById('error-alert');
    alertBox.textContent = `⚠️ ${message} ${error ? error.message : ''}`;
    alertBox.classList.remove('hidden');
    alertBox.classList.add('show');

    setTimeout(() => {
        alertBox.classList.remove('show');
        setTimeout(() => {
            alertBox.classList.add('hidden');
        }, 400);
    }, 4000);
}

window.addEventListener('beforeunload', () => {
    if (device && server) {
        // Disconnect from the GATT server before unloading the page
        server.disconnect();
        statusMessage.classList.remove('connected', 'failed');
        statusMessage.classList.add('disconnected');
        console.log('Disconnected from', device.name);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.title = 'Mon STage de Seconde';
});