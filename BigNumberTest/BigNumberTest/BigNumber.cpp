#include "BigNumber.hpp"
#include <cmath>
#include <sstream>

BigNumber::BigNumber() :
	negative(false)
{
}

BigNumber::BigNumber(Data val, bool negative) :
	data(val),
	negative(negative)
{
}

BigNumber BigNumber::add(BigNumber other) const
{
	auto cmp = internalCompare(*this, other);
	// check for signs
	if (this->negative || other.negative)
	{
		// If both are negative
		if (this->negative && other.negative)
		{
			if (cmp > 0) // left is bigger
				return BigNumber(internalAdd(this->data, other.data), true);
			else
				return BigNumber(internalAdd(other.data, this->data), true);
		}
		else
		{
			if (cmp > 0) // left is bigger
				return BigNumber(internalSub(this->data, other.data), this->negative);
			else
				return BigNumber(internalSub(other.data, this->data), !this->negative);
		}
	}
	// if neither one is negative
	else
	{
		if (cmp > 0) // left is bigger
			return BigNumber(internalAdd(this->data, other.data));
		else
			return BigNumber(internalAdd(other.data, this->data));
	}
}

BigNumber BigNumber::sub(BigNumber other) const
{
	auto cmp = internalCompare(*this, other);
	// check for signs
	if (this->negative || other.negative)
	{
		// If both are negative
		if (this->negative && other.negative)
		{
			if (cmp > 0) // left is bigger
				return BigNumber(internalSub(this->data, other.data), true);
			else
				return BigNumber(internalSub(other.data, this->data), false);
		}
		else
		{
			if (cmp > 0) // left is bigger
				return BigNumber(internalAdd(this->data, other.data), this->negative);
			else
				return BigNumber(internalAdd(other.data, this->data), this->negative);
		}
	}
	// if neither one is negative
	else
	{
		if (cmp > 0) // left is bigger
			return BigNumber(internalSub(this->data, other.data), false);
		else
			return BigNumber(internalSub(other.data, this->data), true);
	}
}

std::string BigNumber::print() const
{
	std::stringstream ss;
	if (negative)
		ss << "-";
	for (auto item : data)
	{
		ss << "[" << (int)item << "]";
	}
	return ss.str();
}

// Always interpreted as unsigned
BigNumber::Data internalAdd(BigNumber::Data max, BigNumber::Data min)
{
	const unsigned int shifter = pow(2, 8);
	const unsigned int lowerMask = shifter - 1;

	BigNumber::Data result;
	uint16_t carry = 0;
	for (int i = 0; i < max.size(); i++)
	{
		// As long as there are still min bytes available
		uint16_t intermediate = 0;
		if (i < min.size())
			// Add the min corresponding min byte
			intermediate = (uint16_t)max[i] + (uint16_t)min[i] + carry;
		else
			intermediate = (uint16_t)max[i] + carry;
		uint8_t lower = intermediate & lowerMask;

		result.push_back(lower);

		// Rember the carry for the next operation
		carry = intermediate / shifter;
	}

	// If there remains a carry, add it to the result
	if (carry != 0)
		result.push_back(carry);

	return result;
}

BigNumber::Data internalSub(BigNumber::Data max, BigNumber::Data min)
{
	BigNumber::Data result;
	int16_t carry = 0;
	for (int i = 0; i < max.size(); i++)
	{
		int16_t intermediate = 0;

		if (i < min.size())
			intermediate = (int16_t)max[i] - (int16_t)min[i] - carry;
		else
			intermediate = (int16_t)max[i] - carry;

		if (intermediate < 0)
		{
			intermediate += 256;
			carry = 1;
		}
		else
			carry = 0;

		result.push_back(intermediate);
	}

	// Clean up potentially 0 cells (but leave at least 1)
	while (result.back() == 0 && result.size() > 1)
		result.pop_back();

	return result;
}


// This does not take the sign into account
int internalCompare(BigNumber left, BigNumber right, bool isSigned)
{
	// Check for 0

	int trigger = 1;

	if (isSigned)
	{
		// If both numbers are negative the result should be inverted
		if (left.negative && right.negative)
			trigger = -1;
		// Otherwise, the negative one will be the smaller one
		else if (left.negative == false && right.negative == true)
			return 1;
		else if (left.negative == true && right.negative == false)
			return -1;
	}
	
	// The shorter one will be the smaller / bigger one depending on the sign
	if (left.data.size() > right.data.size())
		return 1 * trigger;
	if (right.data.size() > left.data.size())
		return -1 * trigger;

	// From here on we know that both numbers are the same bit size
	// Therefore, the most significant byte matters
	if (left.data.back() == right.data.back())
		return 0;
	
	if (left.data.back() > right.data.back())
		return 1 * trigger;
	return -1 * trigger;
}