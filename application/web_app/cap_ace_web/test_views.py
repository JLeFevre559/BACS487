from django.shortcuts import render
from .models import SavingModule, SavingsGoal

def savings_lesson(request):
    modules = SavingModule.objects.all()
    return render(request, "savings_lesson.html", {"modules": modules})

def savings_goal(request):
    if request.method == "POST":
        target = request.POST["target_amount"]
        date = request.POST["goal_date"]
        goal = SavingsGoal(user=request.user, target_amount=target, goal_date=date)
        goal.save()
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, "savings_goal.html", {"goals": goals})
def budgeting_lesson(request):
    categories = BudgetCategory.objects.all()
    expenses = Expense.objects.filter(user=request.user)
    return render(request, "budgeting_lesson.html", {"categories": categories, "expenses": expenses})

def add_expense(request):
    if request.method == "POST":
        category = BudgetCategory.objects.get(id=request.POST["category_id"])
        amount = request.POST["amount"]
        expense = Expense(user=request.user, category=category, amount=amount)
        expense.save()
    return redirect("budgeting_lesson")
