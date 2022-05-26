#include <iostream>
#include "BigNumber.hpp"
//using namespace std;


int main()
{
	// test big number

	BigNumber num1({ 1 });
	BigNumber num2({ 44 }, true);

	auto num3 = num1.sub(num2);

	//auto num3 = num1.add(num2);


	std::cout << num3.print() << std::endl;
	return EXIT_SUCCESS;
}