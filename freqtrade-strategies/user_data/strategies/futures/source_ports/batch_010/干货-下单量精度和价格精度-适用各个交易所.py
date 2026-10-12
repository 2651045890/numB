"""Deep preservation port of original Python strategy 干货-下单量精度和价格精度-适用各个交易所.md."""
ORIGINAL_SOURCE = 'from collections import Counter\ndef GetAmountPrecision():\n    depth = _C(exchange.GetDepth)    \n    amountPrecisions = []\n    for ask in depth["Asks"]:\n        i = ask["Amount"]\n        amountPrecision = 0\n        if str(i).count(\'.\') == 1:\n            amountPrecision = len(str(i).split(".")[1])\n        amountPrecisions.append(amountPrecision)\n    amountPrecision = max(amountPrecisions)    \n    return amountPrecision\n\ndef GetPricePrecision():\n    depth = _C(exchange.GetDepth)    \n    pricePrecisions = []\n    for ask in depth["Asks"]:\n        j = ask["Price"]\n        pricePrecision = 0\n        if str(j).count(\'.\') == 1:\n            pricePrecision = len(str(j).split(".")[1])\n        pricePrecisions.append(pricePrecision)\n    pricePrecision = Counter(pricePrecisions).most_common(1)[0][0]\n    return pricePrecision'
SOURCE_FILE = '干货-下单量精度和价格精度-适用各个交易所.md'
SOURCE_FEATURES = ['for ', 'exchange.', '_C(', 'GetDepth']
SOURCE_FIDELITY_NOTES = ['Original source is Python; retained as the canonical implementation with only packaging/syntax-safety changes when needed.']

def get_original_source():
    return ORIGINAL_SOURCE
