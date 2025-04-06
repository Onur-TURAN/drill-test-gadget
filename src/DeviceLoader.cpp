#include "DeviceLoader.h"
#include <fstream>
#include <sstream>

void loadDevicesFromLog(const std::string& logFilePath, std::vector<std::pair<std::string, std::string>>& devices) {
    devices.clear();
    std::ifstream logFile(logFilePath);
    std::string line;
    while (std::getline(logFile, line)) {
        std::istringstream iss(line);
        std::string ip, port;
        if (std::getline(iss, ip, ':') && std::getline(iss, port)) {
            devices.emplace_back(ip, port);
        }
    }
}