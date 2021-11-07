from functools import reduce
from itertools import combinations
from typing import List, Set, Tuple
from abc import ABC, abstractmethod


class FrequentSet(object):
    def __init__(self, items: frozenset, support: int = 0, relative_support: float = 0.0):
        self.items = items
        self.support = support

        # Relative support value (percentage)
        self.relative_support = relative_support

    @property
    def all_items(self):
        return list(self.items)

    def __str(self):
        return f'{", ".join(self.items)} -> {self.relative_support}% ({self.support})'

    def __str__(self):
        """
        String representation for frequent set
        :return:
        """
        return self.__str()

    def __repr__(self):
        """
        Representation for frequent set
        :return:
        """
        return self.__str()

    def __lt__(self, other):
        return self.support < other.support


class AssociationRule(object):
    condition = None
    consequence = None

    # Likelihood that an items 'consequence' is also valid if items 'condition' is valid
    confidence = 0.0

    # Increase in the ratio of consequence when condition is valid
    lift = 0.0

    def __str__(self):
        """
        String representation for association rule

        :return:
        """
        condition = ', '.join(sorted(list(self.condition)))
        consequence = ', '.join(sorted(list(self.consequence)))
        confidence = round(self.confidence * 100, 3)

        return f'{condition} => {consequence} (Confidence: {confidence}%, Lift: {round(self.lift, 3)})'

    def __lt__(self, other):
        return self.confidence < other.confidence and self.lift < other.lift


class FrequentPatternsAbstract(ABC):
    def __init__(self, transactions: List[List[str]] = None):
        """
        Class constructor

        :param transactions: List of transactions
        """
        self._transaction_index = {}
        self._transaction_count = len(transactions)

        if transactions is not None:
            self._index_transactions(transactions=transactions)

    # -------------------------
    # Data indexing + retrieval
    # -------------------------
    @abstractmethod
    def _index_transactions(self, transactions: List[List[str]]):
        """
        Store transaction items in inverted index
        Abstract method to create different children classes where the items
        can be stored to disk, database, keep in memory, etc.

        :param transactions: List of transactions containing items
        :return:
        """
        pass

    @abstractmethod
    def _get_all_items(self) -> list:
        """
        Get all item keys from inverted index.
        Abstract method to create different children classes where the items
        can be gathered from disk, database, memory, etc.

        :return: List of items
        """
        return []

    @abstractmethod
    def _item_transactions(self, item: str) -> Set[int]:
        """
        Get list of transactions where an item is contained.
        Abstract method to create different children classes where the transactions
        can be gathered from disk, database, memory, etc.

        :param item: Item to retrieve
        :return: Set with transactions where an item is contained
        """
        return set()

    # -------
    # Private
    # -------
    def __support_value(self, candidate: frozenset) -> Tuple[int, float]:
        """
        Calculate support value for candidate set (how many times the set occurs in the transactions)

        :param candidate: Candidate set
        :return: Support value, Relative Support value
        """
        # -------------------------------------------------------------------------
        # Create set with all the transactions that have the items of the candidate.
        # Use inverted index to retrieve transaction intersection.
        # -------------------------------------------------------------------------
        transactions = reduce(
            set.intersection,
            [self._item_transactions(item=tr_item) for tr_item in candidate]
        )

        # ----------------------------------------------------------------
        # Calculate support by getting the length of the intersected items
        # ----------------------------------------------------------------
        support = len(transactions)
        relative_support = float(support) / self._transaction_count

        return support, relative_support

    # ------
    # Public
    # ------
    def get_frequent_item_sets(
            self,
            minimum_support: float = 0.5,
            is_relative_support: bool = True,
            prune: bool = True
    ) -> List[FrequentSet]:
        """
        Retrieve list of frequent items sets having a minimum support threshold

        :param minimum_support: Value of minimum support
        :param is_relative_support: Whether minimum support is relative (percentage).
                                    If False, support is absolute.
        :param prune: Prune final sets
        :return:
        """
        if is_relative_support is False:
            minimum_support = int(minimum_support)

            if minimum_support < 0 or minimum_support > self._transaction_count:
                minimum_support = self._transaction_count
        else:
            if not (0.0 <= minimum_support <= 1.0):
                minimum_support = 1.0

        iteration = 0
        next_iteration = True

        # ----------------------------------------------
        # Set initial candidate list from inverted index
        # ----------------------------------------------
        initial_set: List[FrequentSet] = []

        for key in self._get_all_items():
            initial_candidate = FrequentSet(
                items=frozenset([key]),
                relative_support=is_relative_support
            )
            initial_set.append(initial_candidate)

        # List of frequent sets for each iteration
        iterations_frequent_sets = {iteration: initial_set}

        while next_iteration is True:
            unique_items = set([
                set_item
                for item_set in iterations_frequent_sets[iteration]
                for set_item in item_set.items
            ])

            # -----------------------------------------------------------
            # Generate new possible candidate sets by combining all items
            # from frequent sets from previous iteration (L[iteration-1])
            # using iteration + 1 as candidate size.
            # -----------------------------------------------------------
            previous_frequent_sets = set([
                set_item.items
                for set_item in iterations_frequent_sets[iteration]
            ])

            possible_candidate_sets = (
                frozenset(candidate)
                for candidate in combinations(unique_items, iteration + 1)
            )

            if iteration > 0:
                # ------------------------------------------------
                # Check if all the subsets of an items-set are also
                # frequent sets from a previous iteration
                # ------------------------------------------------
                candidate_sets = []

                for candidate in possible_candidate_sets:
                    discard_candidate = False
                    for item_subset in combinations(candidate, iteration):
                        if frozenset(item_subset) not in previous_frequent_sets:
                            discard_candidate = True
                            break

                    if discard_candidate is False:
                        candidate_sets.append(candidate)

            else:
                # First iteration, do not prune list
                candidate_sets = [candidate for candidate in possible_candidate_sets]

            current_iteration_frequent_sets = []
            for candidate in candidate_sets:
                support, relative_support = self.__support_value(candidate=candidate)

                if is_relative_support is True:
                    not_minimum_support = relative_support < minimum_support
                else:
                    not_minimum_support = support < minimum_support

                if not_minimum_support is True:
                    continue

                candidate_frequent = FrequentSet(
                    items=frozenset(candidate),
                    support=support,
                    relative_support=relative_support
                )

                current_iteration_frequent_sets.append(candidate_frequent)

            if len(current_iteration_frequent_sets) > 0:
                iteration += 1
                iterations_frequent_sets[iteration] = current_iteration_frequent_sets
            else:
                next_iteration = False

        # First frequent set is not used, remove
        del iterations_frequent_sets[0]

        # ------------------------------------
        # Pruning: remove frequent set that is
        # a subset of another frequent set
        # ------------------------------------
        pruned_sets = set()

        joined_frequent_sets = [
            set_object
            for index, sets in iterations_frequent_sets.items()
            for set_object in sets
        ]

        # Verify that frequent set is not a subset of another frequent set
        if prune is True:
            for set1, set2 in combinations(joined_frequent_sets, 2):
                if set1 not in pruned_sets and set1.items.issubset(set2.items):
                    pruned_sets.add(set1)

        cleaned_frequent_sets = [
            new_item
            for new_item in joined_frequent_sets
            if new_item not in pruned_sets
        ]

        return sorted(cleaned_frequent_sets, reverse=True)

    def association_rules(
            self,
            frequent_item_sets: List[FrequentSet],
            minimum_confidence: float = 0.5,
            minimum_lift: float = 0.05
    ) -> List[AssociationRule]:
        """
        Retrieve association rules(condition -> consequence) supporting a minimum confidence

        :param frequent_item_sets: List of frequent items sets
        :param minimum_confidence: Minimum confidence threshold that rule must support
        :param minimum_lift: Minimum lift value threshold that rule must support
        :return: List of association rules
        """
        # List of association rules to return
        association_rules = []

        # Confidence value for each rule
        association_rules_confidence = {}

        # -----------------------------------------
        # Create subsets with all transaction items
        # that are part of the frequent items sets
        # -----------------------------------------
        maximum_cardinality = max([len(item_set.items) for item_set in frequent_item_sets]) \
            if len(frequent_item_sets) > 0 else 0

        global_item_subsets = set()
        global_item_subsets_support = []

        if maximum_cardinality > 1:
            for item_set in frequent_item_sets:
                frequent_set = item_set.items

                for subset_index in range(1, maximum_cardinality):
                    item_set_subsets = combinations(frequent_set, subset_index)

                    # Store subset only if not in list
                    for item_subset in item_set_subsets:
                        set_attempt = frozenset(item_subset)

                        if set_attempt not in global_item_subsets:
                            subset_item = FrequentSet(items=set_attempt)

                            # Calculate support values for generated subsets
                            support, relative_support = self.__support_value(candidate=set_attempt)
                            subset_item.support = support
                            subset_item.relative_support = relative_support

                            # Store unique subsets
                            global_item_subsets_support.append(subset_item)
                            global_item_subsets.add(set_attempt)

        subset_list_length = len(global_item_subsets_support)
        if subset_list_length > 0:
            # ------------------------------------------------------
            # Combination of each subset to check
            # confidence value for condition -> consequence subsets
            # ------------------------------------------------------
            rule_index = 0

            for global_index1 in range(0, subset_list_length):
                # Support for subset A
                global_subset_a = global_item_subsets_support[global_index1]

                subset_a = global_subset_a.items
                support_a = global_subset_a.support

                for global_index2 in range(0, subset_list_length):
                    # Only make combinations if the subsets are not the same
                    if global_index1 != global_index2:
                        global_subset_b = global_item_subsets_support[global_index2]

                        subset_b = global_subset_b.items

                        # Validate that intersection between A and B is empty (A is not contained in B)
                        if len(subset_a.intersection(subset_b)) == 0:
                            # Obtain union of both sets and retrieve support value
                            a_union_b_set = subset_a.union(subset_b)

                            # ----------------------------------------------------------
                            # Confidence value = Support_count(A U B) / Support_count(A)
                            # ----------------------------------------------------------
                            support_a_union_b, support_a_union_b_relative = self.__support_value(
                                candidate=a_union_b_set
                            )

                            rule_support = float(support_a_union_b) / support_a

                            # ----------------------------------------------------------------------------
                            # Lift value = (Support_count(A U B) / Support_count(A)) / Relative support(B)
                            # Lift value = (Confidence (A, B) / Relative support(B)
                            # ----------------------------------------------------------------------------
                            lift = float(support_a_union_b) / (support_a * global_subset_b.relative_support)

                            if rule_support >= minimum_confidence and lift >= minimum_lift:
                                new_rule = AssociationRule()
                                new_rule.condition = subset_a
                                new_rule.consequence = subset_b
                                new_rule.confidence = rule_support

                                new_rule.lift = lift
                                association_rules.append(new_rule)

                                association_rules_confidence[rule_index] = rule_support
                                rule_index += 1

        # Return association rules in descendent order (by confidence value)
        confidence_sorted = sorted(association_rules_confidence,
                                   key=association_rules_confidence.__getitem__,
                                   reverse=True)

        return sorted([
            association_rules[rule_index]
            for rule_index in confidence_sorted
        ], reverse=True)
