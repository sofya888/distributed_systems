CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -Iinclude

SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin
LIB_DIR = lib

STATIC_LIB = $(LIB_DIR)/libmath_operations.a
DYNAMIC_DLL = $(BIN_DIR)/string_operations.dll
IMPLIB     = $(LIB_DIR)/libstring_operations.dll.a
APP        = $(BIN_DIR)/library_demo.exe

all: $(APP)

$(APP): $(OBJ_DIR)/main.o $(STATIC_LIB) $(DYNAMIC_DLL) | $(BIN_DIR)
	$(CXX) -o $@ $(OBJ_DIR)/main.o -L$(LIB_DIR) -lmath_operations -lstring_operations

$(STATIC_LIB): $(OBJ_DIR)/math_operations.o | $(LIB_DIR)
	ar rcs $@ $(OBJ_DIR)/math_operations.o

$(DYNAMIC_DLL): $(OBJ_DIR)/string_operations.o | $(BIN_DIR) $(LIB_DIR)
	$(CXX) -shared -o $@ $(OBJ_DIR)/string_operations.o -Wl,--out-implib,$(IMPLIB)

$(OBJ_DIR)/math_operations.o: $(SRC_DIR)/math_operations.cpp include/math_operations.h | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJ_DIR)/string_operations.o: $(SRC_DIR)/string_operations.cpp include/string_operations.h | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -DBUILDING_DLL -c $< -o $@

$(OBJ_DIR)/main.o: $(SRC_DIR)/main.cpp include/math_operations.h include/string_operations.h | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BIN_DIR) $(OBJ_DIR) $(LIB_DIR):
	mkdir -p $@

run: $(APP)
	./$(APP)

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR) $(LIB_DIR)

.PHONY: all clean run
