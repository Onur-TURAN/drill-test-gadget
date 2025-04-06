#ifndef NETWORKDRILLTEST_H
#define NETWORKDRILLTEST_H

#include <vector>
#include <string>

void sendData(const std::string& host, const std::string& port, const std::string& message);
void networkDrillTest(const std::vector<std::pair<std::string, std::string>>& devices, const std::string& message);

#endif // NETWORKDRILLTEST_H