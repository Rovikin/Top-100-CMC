#include <iostream>
#include <string>
#include <curl/curl.h>
#include "json.hpp"

using json = nlohmann::json;

// Callback curl untuk nampung response
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
    const std::string BLUE = "\033[94m";
    const std::string RESET = "\033[0m";

    char buffer[32];
    if (p >= 1.0) snprintf(buffer, sizeof(buffer), "$%.2f", p);
    else if (p >= 0.01) snprintf(buffer, sizeof(buffer), "$%.4f", p);
    else snprintf(buffer, sizeof(buffer), "$%.6f", p);

    return BLUE + std::string(buffer) + RESET;
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

std::string format_percent_red_minus(double pct) {
    const std::string RED = "\033[31m";
    const std::string RESET = "\033[0m";

    char buffer[20];
    snprintf(buffer, sizeof(buffer), "-%.2f%%", pct);
    return RED + std::string(buffer) + RESET;
}

std::string format_percent_yellow_plus(double pct) {
    const std::string YELLOW = "\033[33m";
    const std::string RESET = "\033[0m";

    char buffer[20];
    snprintf(buffer, sizeof(buffer), "+%.2f%%", pct);
    return YELLOW + std::string(buffer) + RESET;
}

void print_colored_line(const std::string& label, const std::string& colored_value) {
    size_t esc_start = colored_value.find("\033[");
    if (esc_start == std::string::npos) {
        std::cout << label << colored_value << "\n";
        return;
    }
    size_t esc_end = colored_value.find("m", esc_start);
    if (esc_end == std::string::npos) {
        std::cout << label << colored_value << "\n";
        return;
    }
    std::string color_code = colored_value.substr(esc_start, esc_end - esc_start + 1);

    const std::string RESET = "\033[0m";

    std::cout << color_code << label << RESET << colored_value << "\n";
}

double safe_get_double(const json& j, const std::string& key) {
    if (j.contains(key) && !j[key].is_null()) {
        return j[key].get<double>();
    }
    return 0.0;
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

        const std::string BROWN_LIGHT = "\033[93m";
        const std::string BLUE = "\033[94m";
        const std::string BROWN_DARK = "\033[33m";
        const std::string RESET = "\033[0m";

        for (size_t i = 0; i < j.size(); ++i) {
            auto& coin = j[i];

            std::string symbol = coin.value("symbol", "N/A");
            for (auto & c: symbol) c = toupper(c);

            double price = safe_get_double(coin, "current_price");
            double change_24h = safe_get_double(coin, "price_change_percentage_24h");
            double change_7d = safe_get_double(coin, "price_change_percentage_7d_in_currency");
            double change_30d = safe_get_double(coin, "price_change_percentage_30d_in_currency");
            double ath = safe_get_double(coin, "ath");

            double from_ath = 0.0;
            double to_ath = 0.0;
            if (price > 0.0 && ath > 0.0) {
                from_ath = ((ath - price) / ath) * 100.0;
                if (from_ath < 0) from_ath = 0;

                to_ath = ((ath - price) / price) * 100.0;
                if (to_ath < 0) to_ath = 0;
            }

            std::string price_str = format_price(price);
            std::string ath_str = format_price(ath);
            std::string change_24h_str = format_percent_colored(change_24h);
            std::string change_7d_str = format_percent_colored(change_7d);
            std::string change_30d_str = format_percent_colored(change_30d);
            std::string from_ath_str = format_percent_red_minus(from_ath);
            std::string to_ath_str = format_percent_yellow_plus(to_ath);

            std::cout << BLUE << "#" << (i+1) << RESET << " " << BROWN_LIGHT << symbol << RESET << "\n";

            print_colored_line("  Price       : ", price_str);
            print_colored_line("  24H Change  : ", change_24h_str);
            print_colored_line("  7D Change   : ", change_7d_str);
            print_colored_line("  30D Change  : ", change_30d_str);
            print_colored_line("  ↓ From ATH  : ", from_ath_str);
            print_colored_line("  ↑ To ATH    : ", to_ath_str);
            print_colored_line("  ATH Price   : ", ath_str);

            std::cout << BROWN_DARK << "----------------------------------------" << RESET << "\n";
        }

    } catch (json::exception& e) {
        std::cerr << "JSON error: " << e.what() << "\n";
        return 1;
    } catch (std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
