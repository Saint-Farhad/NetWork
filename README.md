# Network Configuration and Monitoring Tool

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Introduction
This tool is designed for easy and intuitive network configuration and monitoring using Python. It enables users, even those without advanced technical knowledge, to configure their network settings and monitor their network traffic efficiently. 

The tool focuses on user-friendliness and simplicity while providing powerful network configuration and monitoring capabilities.

## Features
- **Basic Linux Network Configuration:** 
  - Manage network settings such as IP addresses, routes, and DNS configurations.
  
- **Firewall Management (NFTables):** 
  - Set up and manage firewall rules using NFTables.
  
- **Open vSwitch Management:** 
  - Configure Open vSwitch (OVS) bridges, ports, and settings.
  
- **Network Monitoring:** 
  - Real-time monitoring of network traffic and statistics.

- **Script Install/Update:** 
  - Convenient installation and updating process using the provided installer.

## Prerequisites
Ensure that the following packages and tools are installed on your system before using this tool:

- **Git** - To clone the repository.
- **Python 3** - To execute Python scripts.
- **Pip3** - To install required Python packages.
- **NFTables** - Required for firewall management.
- **nload, sysstat, net-tools, openvswitch-switch, tcpdump, dnsutils, iproute2, ifstat** - For network management and monitoring functionalities.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Saint-Farhad/NetWork.git
   ```
   
2. Run the installation script to install the required dependencies:
   ```bash
   sudo bash install.sh
   ```

3. Install the Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage
Once everything is set up, you can start using the tool:

- To run the main interface, use the following command:
  ```bash
  python3 tui_main.py
  ```

The tool provides an interactive text-based user interface for configuring network settings, firewall rules, and monitoring the network traffic.

## Project Structure
- **firewall_config.py**: Handles firewall configuration logic.
- **network_config.py**: Deals with basic network configurations like IP address setup, routing, and DNS.
- **network_monitor.py**: Contains logic for monitoring network traffic.
- **vSwitch_config.py**: Used for Open vSwitch configuration and management.
- **menu.py**: Manages the user interface menu for selecting operations.
- **welcome.py**: Displays a welcome message when starting the tool.
- **tui_main.py**: The main entry point of the text-based user interface.
- **firewall_modules/**, **network_modules/**, **monitor_modules/**, **ovs_modules/**: Modules for respective configurations and functionalities.
- **install.sh**: Script for installing necessary dependencies.
- **requirements.txt**: Python dependencies for the project.

## Contributing
Contributions are welcome! To contribute:

1. Fork the project.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This enhanced version includes more comprehensive instructions and organizes the sections better for clarity. Let me know if you'd like to add or modify anything!
