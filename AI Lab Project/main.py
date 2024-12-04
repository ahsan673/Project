

import matplotlib.pyplot as plt
from expense_tracker import Expense
import calendar
import datetime
import os
import csv

def main():
    print(f"Running Expense Tracker!")
    expense_file_path = "expenses.csv"
    budget_file_path = "budget.txt"

    budget = read_budget_from_file(budget_file_path)

    if budget is None:  
        budget = get_user_budget()
        save_budget_to_file(budget, budget_file_path)
        print(f"Your monthly budget is set to ${budget:.2f}")
    else:
        print(f"Your current monthly budget is ${budget:.2f}")
    
    if ask_to_change_budget():
        budget = get_user_budget()
        save_budget_to_file(budget, budget_file_path)
        print(f"Your new monthly budget is set to ${budget:.2f}")

    while True:
        expense = get_user_expense()
        save_expense_to_file(expense, expense_file_path)

        continue_input = input("Do you want to add another expense? (y/n): ").lower()
        if continue_input != 'y':
            break

    summarize_expenses(expense_file_path, budget)
    visualize_expense(expense_file_path)
    ai_suggestions(expense_file_path, budget)

def ask_to_change_budget():
    """Ask the user if they want to change their budget."""
    change_budget = input("Do you want to change your monthly budget? (y/n): ").lower()
    return change_budget == 'y'

def get_user_budget():
    """Prompt the user to enter their monthly budget and handle invalid input."""
    while True:
        try:
            budget = float(input("Enter your monthly budget: "))
            if budget <= 0:
                print("Budget must be a positive number. Please try again.")
            else:
                return budget
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def read_budget_from_file(budget_file_path):
    """Read the budget from a file. Returns None if no budget is set."""
    if os.path.exists(budget_file_path):
        with open(budget_file_path, "r") as f:
            try:
                budget = float(f.read().strip())
                return budget
            except ValueError:
                print("Error reading budget. Invalid format.")
                return None
    return None

def save_budget_to_file(budget, budget_file_path):
    """Save the budget to a file."""
    with open(budget_file_path, "w") as f:
        f.write(f"{budget}")

def get_user_expense():
    """Prompt the user to enter an expense and its details."""
    print(f"Getting User Expense")
    expense_name = input("Enter expense name: ")
    
    while True:
        try:
            expense_amount = float(input("Enter expense amount: "))
            if expense_amount <= 0:
                print("Expense amount must be positive. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    expense_categories = [
        "Food",
        "Home",
        "Work",
        "Fun",
        "Others",
    ]

    while True:
        print("Select a category: ")
        for i, category_name in enumerate(expense_categories):
            print(f"  {i + 1}. {category_name}")

        value_range = f"[1 - {len(expense_categories)}]"
        try:
            selected_index = int(input(f"Enter a category number {value_range}: ")) - 1
            if selected_index in range(len(expense_categories)):
                selected_category = expense_categories[selected_index]
                expense_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
                new_expense = Expense(
                    name=expense_name, category=selected_category, amount=expense_amount, date=expense_date
                )
                return new_expense
            else:
                print("Invalid category. Please try again!")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def save_expense_to_file(expense: Expense, expense_file_path):
    """Save the expense to the CSV file."""
    print(f"Saving User Expense: {expense} to {expense_file_path}")
    with open(expense_file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([expense.name, expense.amount, expense.category, expense.date])

def summarize_expenses(expense_file_path, budget):
    """Summarize the user's expenses and show the remaining budget."""
    print(f"Summarizing User Expense")
    
    expenses = []
    try:
        with open(expense_file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    try:
                        expense_name, expense_amount, expense_category, expense_date = row
                        line_expense = Expense(
                            name=expense_name,
                            amount=float(expense_amount),
                            category=expense_category,
                            date=expense_date
                        )
                        expenses.append(line_expense)
                    except ValueError:
                        print(f"Skipping invalid line: {row}")
                        continue
    except FileNotFoundError:
        print(f"Expense file {expense_file_path} not found.")
        return

    amount_by_category = {}
    for expense in expenses:
        key = expense.category
        if key in amount_by_category:
            amount_by_category[key] += expense.amount
        else:
            amount_by_category[key] = expense.amount

    print("Expenses By Category:")
    for key, amount in amount_by_category.items():
        print(f"  {key}: ${amount:.2f}")

    total_spent = sum([x.amount for x in expenses])
    print(f"Total Spent: ${total_spent:.2f}")

    remaining_budget = budget - total_spent
    if remaining_budget < 0:
        remaining_budget = 0  
    print(f"Budget Remaining: ${remaining_budget:.2f}")

    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day

    if remaining_days > 0:
        daily_budget = remaining_budget / remaining_days
        print(green(f"Budget Per Day: ${daily_budget:.2f}"))
    else:
        print("No remaining days in the month for daily budget calculation.")

def visualize_expense(expense_file_path):
    """Generate a pie chart to visualize the expenses by category."""
    print("Visualizing Expenses...")

    expenses = []
    try:
        with open(expense_file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    expense_name, expense_amount, expense_category, expense_date = row
                    line_expense = Expense(
                        name=expense_name,
                        amount=float(expense_amount),
                        category=expense_category,
                        date=expense_date
                    )
                    expenses.append(line_expense)
    except FileNotFoundError:
        print(f"Expense file {expense_file_path} not found.")
        return

    amount_by_category = {}
    for expense in expenses:
        key = expense.category
        if key in amount_by_category:
            amount_by_category[key] += expense.amount
        else:
            amount_by_category[key] = expense.amount

    categories = list(amount_by_category.keys())
    amounts = list(amount_by_category.values())

    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expenses By Category')
    plt.show()

def ai_suggestions(expense_file_path, budget):
    """Provide AI suggestions based on the user's spending behavior."""
    print("AI Suggestions to Avoid Irrelevant Spending:")

    expenses = []
    try:
        with open(expense_file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    expense_name, expense_amount, expense_category, expense_date = row
                    line_expense = Expense(
                        name=expense_name,
                        amount=float(expense_amount),
                        category=expense_category,
                        date=expense_date
                    )
                    expenses.append(line_expense)
    except FileNotFoundError:
        print(f"Expense file {expense_file_path} not found.")
        return

    fun_spending = sum([expense.amount for expense in expenses if expense.category == 'Fun'])
    if fun_spending > budget * 0.15:  
        print("Suggestion: Your spending on 'Fun' is relatively high. Consider reducing non-essential entertainment expenses.")

    food_spending = sum([expense.amount for expense in expenses if expense.category == 'Food'])
    if food_spending > budget * 0.2:  
        print("Suggestion: You may want to reduce spending on Food. Consider cooking at home instead of eating out.")

    total_spent = sum([expense.amount for expense in expenses])
    if total_spent > budget:
        print("Warning: You've exceeded your budget. Try to reduce non-essential expenses to stay within your limit.")

def green(text):
    """Color text green (for supported terminals)."""
    return f"\033[92m{text}\033[0m"

if __name__ == "__main__":
    main()
