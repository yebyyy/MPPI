def move(state: tuple, control: tuple) -> tuple:
    x, y = state
    dx, dy = control
    return (x + dx, y + dy)

