#include "Location.hpp"

Location::Location(){
    x = 0;
    y = 0;
}

int Location::getX(){
    return x;
}

int Location::getY(){
    return y;
}

void Location::setCoords(const int& new_x, const int& new_y){
    x = new_x;
    y = new_y;
}

bool Location::operator==(const Location& rhs) {
    return (x == rhs.x && y == rhs.y);
}

bool Location::operator!=(const Location& rhs) {
    return !(*this == rhs);
}

Location Location::operator-(const Location& rhs) {
    Location result;
    result.x = x - rhs.x;
    result.y = y - rhs.y;
    return result;
}

Location Location::operator+(const Location& rhs){
    Location result;
    result.x = x + rhs.x;
    result.y = y + rhs.y;
    return result;
}

Location Location::operator+=(const Location& rhs){
    x += rhs.x;
    y += rhs.y;
    return *this;
}

Location Location::operator-=(const Location& rhs){
    x -= rhs.x;
    y -= rhs.y;
    return *this;
}