from typing import List, Set
from .Abstracts import FrequentPatternsAbstract


class FrequentPatterns(FrequentPatternsAbstract):
    """
    Frequent Pattern class (all transactions in memory)
    """

    # -------------------------
    # Data indexing + retrieval
    # -------------------------
    def _index_transactions(self, transactions: List[list]):
        """
        Store transaction items in inverted index
        :param transactions: List of transactions containing items
        :return:
        """
        transaction_index = {}
        transaction_row = 0

        for transaction in transactions:
            transaction_row += 1

            for item in transaction:
                item = str(item)

                if item not in transaction_index:
                    transaction_index[item]: Set[int] = set()

                # Inverted index with transaction index
                transaction_index[item].add(transaction_row)

        self._transaction_index = transaction_index

    def _get_all_items(self):
        """
        Get all item keys from inverted index

        :return: List of items
        """
        return self._transaction_index.keys()

    def _item_transactions(self, item: str) -> Set[int]:
        """
        Get list of transactions where an item is contained

        :param item: Item to retrieve
        :return: Set with transactions where an item is contained
        """
        return self._transaction_index.get(item, set())
