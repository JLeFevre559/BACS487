class SavingModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SavingsGoal(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    goal_date = models.DateField()
class BudgetCategory(models.Model):
    name = models.CharField(max_length=100)

class Expense(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
