#include "NetworkDrillTest.h"
#include <asio.hpp>
#include <iostream>
#include <thread>

using asio::ip::tcp;

void sendData(const std::string& host, const std::string& port, const std::string& message) {
    try {
        asio::io_context io_context;

        tcp::resolver resolver(io_context);
        tcp::resolver::results_type endpoints = resolver.resolve(host, port);

        tcp::socket socket(io_context);
        asio::connect(socket, endpoints);

        asio::write(socket, asio::buffer(message));

        std::cout << "Data sent to " << host << ":" << port << std::endl;
    } catch (std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

void networkDrillTest(const std::vector<std::pair<std::string, std::string>>& devices, const std::string& message) {
    std::vector<std::thread> threads;

    for (const auto& device : devices) {
        threads.emplace_back(sendData, device.first, device.second, message);
    }

    for (auto& thread : threads) {
        if (thread.joinable()) {
            thread.join();
        }
    }
}