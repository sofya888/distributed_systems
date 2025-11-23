#define BUILDING_DLL
#include "string_operations.h"
#include <algorithm>
#include <cctype>
#include <cstring>
#include <sstream>

void reverse_string(char* str){
    if(!str) return;
    int len = std::strlen(str);
    for(int i=0;i<len/2;++i) std::swap(str[i], str[len-i-1]);
}

bool is_palindrome(const char* str){
    if(!str) return false;
    int len = std::strlen(str);
    for(int i=0;i<len/2;++i)
        if(str[i] != str[len-i-1]) return false;
    return true;
}

StringProcessor::StringProcessor(const char* s): data(s ? s : "") {}
void StringProcessor::to_uppercase(){
    std::transform(data.begin(), data.end(), data.begin(),
                   [](unsigned char c){ return std::toupper(c); });
}
void StringProcessor::to_lowercase(){
    std::transform(data.begin(), data.end(), data.begin(),
                   [](unsigned char c){ return std::tolower(c); });
}
std::string StringProcessor::get_string() const { return data; }

std::vector<std::string> StringProcessor::split(char delimiter) const{
    std::vector<std::string> out;
    std::string token;
    std::istringstream is(data);
    while(std::getline(is, token, delimiter)) out.push_back(token);
    return out;
}

std::string StringProcessor::join(const std::vector<std::string>& v,
                                  const std::string& delim){
    std::string res;
    for(size_t i=0;i<v.size();++i){
        res += v[i];
        if(i+1<v.size()) res += delim;
    }
    return res;
}
