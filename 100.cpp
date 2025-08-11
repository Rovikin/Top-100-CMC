#include <iostream>
#include <string>
#include <curl/curl.h>
#include "json.hpp"

using json = nlohmann::json;

size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* s) {
    size_t totalSize = size * nmemb;
    s->append((char*)contents, totalSize);
    return totalSize;
}

std::string http_get(const std::string& url) {
    CURL* curl = curl_easy_init();
    std::string response;

    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0");

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << "\n";
        }
        curl_easy_cleanup(curl);
    }
    return response;
}

std::string format_price(double p) {
    char buffer[32];
    if (p >= 1.0) snprintf(buffer, sizeof(buffer), "$%.2f", p);
    else if (p >= 0.01) snprintf(buffer, sizeof(buffer), "$%.4f", p);
    else snprintf(buffer, sizeof(buffer), "$%.6f", p);
    return std::string(buffer);
}

std::string format_percent_colored(double pct) {
    const std::string RED = "\033[31m";
    const std::string GREEN = "\033[32m";
    const std::string RESET = "\033[0m";

    char buffer[16];
    if (pct > 0) {
        snprintf(buffer, sizeof(buffer), "+%.2f%%", pct);
        return GREEN + std::string(buffer) + RESET;
    } else {
        snprintf(buffer, sizeof(buffer), "%.2f%%", pct);
        return RED + std::string(buffer) + RESET;
    }
}

int main() {
    std::string url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&price_change_percentage=24h,7d,30d";

    std::string data = http_get(url);

    if (data.empty()) {
        std::cerr << "Failed to fetch data.\n";
        return 1;
    }

    try {
        auto j = json::parse(data);

        if (!j.is_array() || j.empty()) {
            std::cerr << "Unexpected JSON format.\n";
            return 1;
        }

        for (size_t i = 0; i < j.size(); ++i) {
            auto& coin = j[i];

            std::string symbol = coin.value("symbol", "N/A");
            double price = coin.value("current_price", 0.0);
            double change_24h = coin.value("price_change_percentage_24h", 0.0);
            double change_7d = coin.value("price_change_percentage_7d_in_currency", 0.0);
            double change_30d = coin.value("price_change_percentage_30d_in_currency", 0.0);
            double ath = coin.value("ath", 0.0);

            double from_ath = 0.0;
            double to_ath = 0.0;
            if (ath > 0.0) {
                from_ath = ((ath - price) / ath) * 100.0;
                to_ath = ((price - ath) / ath) * 100.0;
            }

            std::cout << "#" << (i+1) << " " << symbol << "\n";
            std::cout << "  Price       : " << format_price(price) << "\n";
            std::cout << "  24H Change  : " << format_percent_colored(change_24h) << "\n";
            std::cout << "  7D Change   : " << format_percent_colored(change_7d) << "\n";
            std::cout << "  30D Change  : " << format_percent_colored(change_30d) << "\n";
            std::cout << "  ↑ To ATH    : " << format_percent_colored(to_ath) << "\n";
            std::cout << "  ↓ From ATH  : " << format_percent_colored(from_ath) << "\n";
            std::cout << "----------------------------------------\n";
        }

    } catch (json::parse_error& e) {
        std::cerr << "JSON parse error: " << e.what() << "\n";
        return 1;
    } catch (std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
