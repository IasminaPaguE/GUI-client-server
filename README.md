# GUI-client-server-


# File Transfer Analyzer (Client-Server GUI)

A PyQt5-based client-server application for sending files from a client to a server and visualizing transfer metrics (throughput, CPU, RAM) in real time on the server.

## Features
- Client GUI to select and send files to the server.
- Server GUI with:
  - Logs view.
  - Real-time charts for throughput (MB/s), CPU (%), and RAM (%).
  - Final transfer metrics summary.

## Tech Stack
- **Language:** Python 3.9+
- **GUI:** PyQt5
- **Charts:** pyqtgraph
- **System Metrics:** psutil
- **Networking:** Python `socket` (TCP)
- **Concurrency:** Python `threading`
- **OS:** Windows (tested); cross-platform expected with PyQt5


## Project Structure
- [main_client.py](main_client.py) — starts the client GUI.
- [main_server.py](main_server.py) — starts the server GUI.
- Client:
  - [`client.client_view.ClientWindow`](client/client_view.py)
  - [`client.client_controller.ClientController`](client/client_controller.py)
  - [`client.client_core.ClientCore`](client/client_core.py)
- Server:
  - [`server.server_gui.ServerWindow`](server/server_gui.py)
  - [`server.server_controller.ServerController`](server/server_controller.py)
  - [`server.server_core.ServerCore`](server/server_core.py)
  - [`server.server_model.FileTransferMetrics`](server/server_model.py)
- Received files: [received_files/](received_files/) (ignored by git).

## Requirements
Defined in [requirements.txt](requirements.txt):
- PyQt5
- psutil
- pyqtgraph

Install:

```sh
git clone https://github.com/IasminaPaguE/GUI-client-server.git
```


```sh
pip install -r requirements.txt
```

## Quick Setup (Windows PowerShell)
```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate

# Download the github project locally
git clone https://github.com/IasminaPaguE/GUI-client-server.git


# Install dependencies
pip install -r requirements.txt

# Run server and client (in separate terminals)
python main_server.py
python main_client.py
```

## How to Run
1. Start the server GUI:
```sh
python main_server.py
```
2. Start the client GUI (in a separate process/terminal):
```sh
python main_client.py
```

Both apps default to the local hostname and port 5000. The client connects to the server using [`client.client_core.ClientCore.connect`](client/client_core.py).

## Usage
- In the client:
  - Click “Select File/Directory” to choose a file.
  - Click “Send to Server” to transfer the file.
  - Controller: [`client.client_controller.ClientController`](client/client_controller.py) calls [`client.client_core.ClientCore.send_file`](client/client_core.py).

- On the server:
  - Click “Start Server” to begin listening.
  - Watch logs in the “Logs” tab.
  - View real-time charts and final metrics in “Metrics & Charts”.
  - Implementation:
    - GUI: [`server.server_gui.ServerWindow`](server/server_gui.py)
    - Controller: [`server.server_controller.ServerController`](server/server_controller.py)
    - Core: [`server.server_core.ServerCore`](server/server_core.py)

## Protocol Details
- Client sends header: `<file_name>|<file_size>|<file_type>\n` then file bytes.
  - See [`client.client_core.ClientCore.send_file`](client/client_core.py).
- Server reads header and writes file to [received_files/](received_files/), computes metrics:
  - Real-time sampling interval: 1 ms.
  - CPU/RAM via `psutil`.
  - Metrics model: [`server.server_model.FileTransferMetrics`](server/server_model.py).
  - Emission to GUI via Qt signals: [`server.server_controller.ServerController`](server/server_controller.py).

## Notes
- Ensure the server is started before sending from the client.
- The save directory is configurable via [`server.server_core.ServerCore`](server/server_core.py) constructor (`save_dir="received_files"`).
- `.gitignore` excludes large or generated directories (e.g., received files, caches): see [.gitignore](.gitignore).