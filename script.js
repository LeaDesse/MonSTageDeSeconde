let device;
let server;
let bluetoothCharacteristic;
let isOperationInProgress = false;
let commandQueue = [];

document.getElementById('connect-button').addEventListener('click', async () => {
    const button = document.getElementById('connect-button');
    const statusMessage = document.getElementById('status-text');
    const statutIndicator = document.getElementById('status-indicator');
    const deviceName = document.getElementById('device-name').value;

    if (button.textContent === 'Connect') {
        statusMessage.textContent = 'Status: Connection on going';

        try {
            device = await navigator.bluetooth.requestDevice({
                filters: [{ name: deviceName }],
                optionalServices: ['6e400001-b5a3-f393-e0a9-e50e24dcca9e']
            });

            if (device.name === deviceName) {
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
            server.disconnect();
            statusMessage.textContent = 'Status: Disconnected';
            button.textContent = 'Connect';
            statutIndicator.classList.remove('connected', 'failed');
            statutIndicator.classList.add('disconnected');
            console.log('Disconnected from', device.name);
        }
    }
});

const switches = document.querySelectorAll('.switch-label input[type="checkbox"]');
const bleRemote = document.getElementById('ble-remote');
const irRemote = document.getElementById('ir-remote');
const lineFollowing = document.getElementById('line-following');
const directionContainer = document.getElementById('direction-container');

switches.forEach(switchElement => {
    switchElement.addEventListener('change', () => {
        if (switchElement.checked) {
            switches.forEach(otherSwitch => {
                if (otherSwitch !== switchElement) {
                    otherSwitch.checked = false;
                }
            });

            if (bleRemote.checked) {
                enqueueCommand('Mode BLE');
                directionContainer.classList.add('show');
            } else if (irRemote.checked) {
                enqueueCommand('Mode IR');
                directionContainer.classList.remove('show');
            } else if (lineFollowing.checked) {
                enqueueCommand('Mode Line');
                directionContainer.classList.remove('show');
            }
        }
    });
});

const directionButtons = document.querySelectorAll('.direction-button');

directionButtons.forEach(button => {
    button.addEventListener('mousedown', () => {
        const command = button.id.charAt(0).toUpperCase() + ' pressed';
        enqueueCommand(command);
    });

    button.addEventListener('mouseup', () => {
        const command = button.id.charAt(0).toUpperCase() + ' released';
        enqueueCommand(command);
    });
});

async function processCommandQueue() {
    if (isOperationInProgress || commandQueue.length === 0) {
        return;
    }

    isOperationInProgress = true;
    const commandString = commandQueue.shift();

    try {
        if (!device || !server || !device.gatt.connected) {
            showError('Device is not connected');
            return;
        }

        if (!bluetoothCharacteristic) {
            const service = await server.getPrimaryService('6e400001-b5a3-f393-e0a9-e50e24dcca9e');
            bluetoothCharacteristic = await service.getCharacteristic('6e400002-b5a3-f393-e0a9-e50e24dcca9e');
        }

        const encoder = new TextEncoder();
        const data = encoder.encode(commandString);

        await bluetoothCharacteristic.writeValue(data);
        console.log('Command sent:', commandString);
    } catch (error) {
        showError('Failed to send Bluetooth command:', error);
        console.error('Send command error:', error);
    } finally {
        isOperationInProgress = false;
        processCommandQueue();
    }
}

function enqueueCommand(commandString) {
    commandQueue.push(commandString);
    processCommandQueue();
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
        server.disconnect();
        statusMessage.classList.remove('connected', 'failed');
        statusMessage.classList.add('disconnected');
        console.log('Disconnected from', device.name);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.title = 'Mon STage de Seconde';
});