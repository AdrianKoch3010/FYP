#include <iostream>
#include "BigNumber.hpp"
//using namespace std;


int main()
{
	// test big number

	BigNumber num1({ 0xFF, 0xFF });
	BigNumber num2({ 0xFF, 0x00 }, true);

	auto num3 = num1.add(num2);

	//auto num3 = num1.add(num2);


	std::cout << num3.print() << std::endl;
	return EXIT_SUCCESS;
}