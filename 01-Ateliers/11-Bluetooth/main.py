from bluetooth import BLE
from stm32_ble_uart import UART_BLE

ble = BLE()
uart = UART_BLE(ble, name="Alphabot")

while True:
  # If data has been received
  if uart.any():
    # Read the data and decode it
    bleData = uart.read().decode().replace("\x00", "")
    # Print the data
    print(bleData)
