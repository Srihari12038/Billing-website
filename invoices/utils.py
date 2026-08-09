from decimal import Decimal


ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _under_thousand(number):
    number = int(number)
    words = []
    if number >= 100:
        words.append(f"{ONES[number // 100]} Hundred")
        number %= 100
    if number >= 20:
        words.append(TENS[number // 10])
        number %= 10
    if number:
        words.append(ONES[number])
    return " ".join(words)


def amount_in_words(amount):
    rupees = int(Decimal(amount).quantize(Decimal("1.")))
    if rupees == 0:
        return "Zero Rupees Only"
    parts = []
    crore, rupees = divmod(rupees, 10000000)
    lakh, rupees = divmod(rupees, 100000)
    thousand, rupees = divmod(rupees, 1000)
    if crore:
        parts.append(f"{_under_thousand(crore)} Crore")
    if lakh:
        parts.append(f"{_under_thousand(lakh)} Lakh")
    if thousand:
        parts.append(f"{_under_thousand(thousand)} Thousand")
    if rupees:
        parts.append(_under_thousand(rupees))
    return f"{' '.join(parts)} Rupees Only"
