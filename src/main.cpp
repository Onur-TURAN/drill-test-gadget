#include <iostream>
#include <vector>
#include "DeviceLoader.h"
#include "NetworkDrillTest.h"

int main() {
    std::vector<std::pair<std::string, std::string>> devices;

    const std::string logFilePath = "/data/ip.log";

    // Load devices from the log file at the start of the program
    loadDevicesFromLog(logFilePath, devices);

    std::string testMessage = "Network Drill Test Message";

    std::cout << "Starting network drill test..." << std::endl;

    networkDrillTest(devices, testMessage);

    std::cout << "Network drill test completed." << std::endl;

    return 0;
}