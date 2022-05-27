#ifndef BIG_NUMBER_HPP
#define BIG_NUMBER_HPP

#include <vector>
#include <string>

class BigNumber
{
public:
	typedef std::vector<uint8_t> Data;

public:
	BigNumber();
	BigNumber(Data val, bool negative = false);

public:
	//BigNumber add(const BigNumber& other) const;
	friend BigNumber::Data internalAdd(BigNumber::Data max, BigNumber::Data min);
	friend BigNumber::Data internalSub(BigNumber::Data max, BigNumber::Data min);
	friend BigNumber::Data internalMul(BigNumber::Data max, BigNumber::Data min);
	friend int internalCompare(BigNumber left, BigNumber right, bool isSigned);

	BigNumber add(BigNumber other) const;

	BigNumber sub(BigNumber other) const;

	BigNumber mul(BigNumber other) const;

	//BigNumber mul(const BigNumber& other) const;

	std::string print() const;

private:
	// All values are signed
	Data data;
	bool negative;
};

BigNumber::Data internalAdd(BigNumber::Data max, BigNumber::Data min);
BigNumber::Data internalSub(BigNumber::Data max, BigNumber::Data min);
BigNumber::Data internalMul(BigNumber::Data max, BigNumber::Data min);

// 1 -->  left >  right
// 0 -->  left == right
// -1 --> left <  right
int internalCompare(BigNumber left, BigNumber right, bool isSigned = false);

#endif