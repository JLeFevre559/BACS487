from django import template

register = template.Library()

@register.simple_tag
def get_xp_data(user, path=None, category=None, xp_value=None):
    """
    Calculate XP data based on user and category
    
    Can be called in three ways:
    1. With path: {% get_xp_data user request.path as xp_data %}
    2. With category: {% get_xp_data user category="budget" as xp_data %}
    3. With explicit xp value: {% get_xp_data user xp_value=category.xp as xp_data %}
    """
    # If explicit XP value is provided, use it directly
    if xp_value is not None:
        total_xp = xp_value
    else:
        # Map path or category code to user XP field
        xp_mapping = {
            'budget': user.budget_xp,
            'savings': user.savings_xp,
            'investing': user.investing_xp,
            'taxes': user.taxes_xp,
            'credit': user.credit_xp,
            'balance': user.balance_sheet_xp
        }
        
        # If category is explicitly provided, use that
        if category and category in xp_mapping:
            total_xp = xp_mapping[category]
        # Otherwise try to determine from path
        elif path:
            total_xp = None
            for key in xp_mapping:
                if key in path:
                    total_xp = xp_mapping[key]
                    break
        else:
            return None
    
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