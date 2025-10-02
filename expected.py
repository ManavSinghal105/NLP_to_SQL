# expected.py
# Expectations keyed by a human-readable test name or index.
# You can use either expected row_count, or expected scalar_value (for COUNT, MAX, etc.),
# or must_include (strings that should appear in the tabulated result).

EXPECTED = {
    "Show all customers.": {"row_count": 3},
    "List all the products purchased.": {"row_count": 3, "must_include": ["Laptop", "Phone", "Mouse"]},
    "What are all the cities where customers live?": {"row_count": 2, "must_include": ["New York", "San Francisco"]},
    "Show all orders placed.": {"row_count": 3},
    "Get all customer names in alphabetical order.": {"row_count": 3, "must_include": ["Alice", "Bob", "Charlie"]},
    "Show customers from New York.": {"row_count": 2, "must_include": ["Alice", "Charlie"]},
    "List all orders where amount is greater than 100.": {"row_count": 2},
    "Show all customers who signed up in 2023.": {"row_count": 1, "must_include": ["Alice"]},
    "Find all orders for product 'Laptop'.": {"row_count": 1},
    "List customers whose name starts with 'A'.": {"row_count": 1, "must_include": ["Alice"]},
    "Show each customer with the products they purchased.": {"row_count": 3},
    "List all customers and their total number of orders.": {"row_count": 2, "must_include": ["Alice", "Bob"]},
    "Show customer names with total money spent.": {"row_count": 2, "must_include": ["Alice", "Bob"]},
    "Which customer purchased 'Phone'?": {"row_count": 1, "must_include": ["Bob"]},
    "Show orders along with customer city.": {"row_count": 3, "must_include": ["New York", "San Francisco"]},
    "What is the total number of customers?": {"scalar_value": "3"},
    "How many orders were placed in January 2024?": {"scalar_value": "0"},
}
