#ifndef LOCATION_HPP
#define LOCATION_HPP



class Location {
    public:
        int x;
        int y;

        Location();
        Location(int x, int y);

        int getX();
        int getY();
        void setCoords(const int& x, const int& y);

        bool operator==(const Location& rhs);
        bool operator!=(const Location& rhs);
        
        Location operator-(const Location& rhs);
        Location operator+(const Location& rhs);
        Location operator+=(const Location& rhs);
        Location operator-=(const Location& rhs);

};

#endif //LOCATION_HPP