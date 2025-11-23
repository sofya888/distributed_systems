#ifndef STRING_OPERATIONS_H
#define STRING_OPERATIONS_H

#include <string>
#include <vector>

#ifdef _WIN32
  #ifdef BUILDING_DLL
    #define DLL_EXPORT __declspec(dllexport)
  #else
    #define DLL_EXPORT __declspec(dllimport)
  #endif
#else
  #define DLL_EXPORT
#endif

extern "C" {
    DLL_EXPORT void reverse_string(char* str);
    DLL_EXPORT bool is_palindrome(const char* str);
}

class DLL_EXPORT StringProcessor {
private:
    std::string data;
public:
    explicit StringProcessor(const char* str = "");
    void to_uppercase();
    void to_lowercase();
    std::string get_string() const;
    std::vector<std::string> split(char delimiter) const;
    static std::string join(const std::vector<std::string>& strings,
                            const std::string& delimiter);
};

#endif // STRING_OPERATIONS_H
