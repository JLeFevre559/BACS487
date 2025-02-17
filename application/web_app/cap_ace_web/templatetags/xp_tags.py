from django import template

register = template.Library()

@register.simple_tag
def get_xp_data(user, path):
    """Calculate XP data based on user and current path"""
    xp_mapping = {
        'budget': user.budget_xp,
        'savings': user.savings_xp,
        'investing': user.investing_xp,
        'taxes': user.taxes_xp,
        'credit': user.credit_xp,
        'balance': user.balance_sheet_xp
    }
    
    # Find which type of XP we're dealing with
    total_xp = None
    for key in xp_mapping:
        if key in path:
            total_xp = xp_mapping[key]
            break
    
    if total_xp is None:
        return None
        
    # Calculate all XP related values
    current_level = total_xp // 140
    current_xp = total_xp % 140
    xp_progress = (current_xp * 100) / 140
    
    return {
        'total_xp': total_xp,
        'current_level': current_level,
        'current_xp': current_xp,
        'xp_progress': xp_progress
    }

@register.filter(name='subtract')  # Explicitly naming the filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0