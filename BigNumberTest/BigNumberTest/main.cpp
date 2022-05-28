#include <iostream>
#include "BigNumber.hpp"
//using namespace std;


int main()
{
	// test big number

	BigNumber num1({ 0xFF, 0xFF });
	BigNumber num2({ 0xFF });

	auto num3 = num1.mul(num2);

	//auto num3 = num1.add(num2);

	std::cout << "Test mul:" << std::endl;
	std::cout << num3.print() << std::endl;
	std::cout << std::hex << num3.toInt() << std::endl;
	std::cout << "Correct: " << ((num1.toInt() * num2.toInt() == num3.toInt()) ? "True" : "False") << std::endl;

	num1 = BigNumber({ 0xFE, 0xAA, 0x22 });
	num2 = BigNumber({ 0xFF, 0xFF });
	num3 = num1.add(num2);
	std::cout << "\n\nTest add:" << std::endl;
	std::cout << num3.print() << std::endl;
	std::cout << std::hex << num3.toInt() << std::endl;
	std::cout << "Correct: " << ((num1.toInt() + num2.toInt() == num3.toInt()) ? "True" : "False") << std::endl;

	return EXIT_SUCCESS;
}