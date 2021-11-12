# Frequent patterns using Apriori algorithm

Data mining technique to find frequent pattern using the Apriori algorithm.

For more information about the algorithm, you can find the related work [here](http://www.vldb.org/conf/1994/P487.PDF).

## Installation via PIP

```bash
$ pip install git+https://github.com/aaronestrada/frequent_apriori@<version>
```

### Example
```bash
$ pip install git+https://github.com/aaronestrada/frequent_apriori@1.0
```

## Example of usage

```python
import sys
from frequent_apriori import FrequentPatterns


def __box_word(word: str) -> str:
    stripes = '-' * len(word)
    return f'{stripes}\n{word}\n{stripes}'


if __name__ == '__main__':
    # Each internal list contains the items for one transaction
    transactions = [
        ['A', 'B', 'C'],
        ['A', 'B', 'C'],
        ['B', 'C'],
        ['X', 'Y', 'D', 'B', 'A']
    ]

    fp = FrequentPatterns(transactions=transactions)

    # --------------------------------------------------------------
    # - Default minimum support is a relative percentage [0.0, 1.0] 
    # - If is_relative_support is False, set the minimum support as 
    #   an absolute value [0, len(transactions)]
    # - To keep subsets and supersets, set prune=False
    # --------------------------------------------------------------
    fp_items = fp.get_frequent_item_sets(
        minimum_support=0.7,
        is_relative_support=True,
        prune=True
    )

    print(__box_word(word='Item sets'))

    for item in fp_items:
        print(item)

    # It is possible to find rules from different frequent item-sets
    assoc_rules = fp.association_rules(
        frequent_item_sets=fp_items,
        minimum_confidence=0.7,
        minimum_lift=0.8
    )

    print(__box_word(word='Rules'))

    for rule in assoc_rules:
        print(rule)

    sys.exit()
```