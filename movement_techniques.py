import random
import math

def movement_techniques(agent, model, radius, choice = None):
    if choice is None:
        choice = random.choice(["random_spot", "random_walk", "move_within_radius"]) # More techniques to come, implementation as random choice should be adjusted
        
    if choice == "random_spot":
        move_to_random_spot(agent, model)
        return
    elif choice == "random_walk":
        new_x, new_y = random_walk(agent, model)
    elif choice == "move_within_radius":
        new_x, new_y = move_within_radius(agent, model, radius)

    # Check if the cell is occupied by any agent
    is_occupied = any(agent.pos == (new_x, new_y) for agent in model.schedule.agents)

    if not is_occupied:
        model.grid.move_agent(agent, (new_x, new_y))

def move_to_random_spot(agent, model):
    while True:
        new_x = random.randint(0, model.grid.width - 1)
        new_y = random.randint(0, model.grid.height - 1)

        # Check if the cell is occupied by any agent
        is_occupied = any(agent.pos == (new_x, new_y) for agent in model.schedule.agents)

        if not is_occupied:
            model.grid.move_agent(agent, (new_x, new_y))
            return

def random_walk(agent, model):
    dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    new_x = max(0, min(model.grid.width - 1, agent.pos[0] + dx))
    new_y = max(0, min(model.grid.height - 1, agent.pos[1] + dy))
    return new_x, new_y

def move_within_radius(agent, model, radius):
    if radius is not None:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        x = agent.pos[0] + int(distance * math.cos(angle))
        y = agent.pos[1] + int(distance * math.sin(angle))

        # Ensure new position is within grid bounds
        new_x = max(0, min(model.grid.width - 1, x))
        new_y = max(0, min(model.grid.height - 1, y))

    return new_x, new_y
