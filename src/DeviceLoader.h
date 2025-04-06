#ifndef DEVICELOADER_H
#define DEVICELOADER_H

#include <vector>
#include <string>

void loadDevicesFromLog(const std::string& logFilePath, std::vector<std::pair<std::string, std::string>>& devices);

#endif // DEVICELOADER_H