import numpy as np
import matplotlib.pyplot as plt

class MPPI():
    def __init__(self, grid_size, num_samples=10, num_iterations=20, lambda_ = 1):
        self.cost_map = np.zeros([grid_size,grid_size])
        self.num_samples = num_samples
        self.num_iterations = num_iterations
        self.lambda_ = lambda_
        self.obstacle_cost = 100
        self.grid_size = grid_size

    def make_obstacles(self, num_obstacles,cost_map,obstacle_size,build_wall):
        
        # add obstacles until num_obstacles are added
        while num_obstacles != 0:
            
            # Randomly select coordinates for obstacles
            rand_idx = np.random.choice(cost_map.shape[0]**2)
            obs_center_x,obs_center_y = np.unravel_index(rand_idx, cost_map.shape)
            
            x_min = int(obs_center_x-obstacle_size/2)
            x_max = int(obs_center_x+obstacle_size/2)
            y_min = int(obs_center_y-obstacle_size/2)
            y_max = int(obs_center_y+obstacle_size/2)
            
            # Ensure obstacles are not going over sides
            if x_min < 0 or x_max > cost_map.shape[0] or y_min < 0 or y_max > cost_map.shape[0]:
                continue
            
            # Assign extra cost to obstacle area
            cost_map[x_min:x_max,y_min:y_max] = self.obstacle_cost
            num_obstacles -= 1
            
        # Build a heavy wall in the middle of the path
        if build_wall == True:
            cost_map[round(self.grid_size/2),round(self.grid_size/10):self.grid_size - round(self.grid_size/10)] = self.obstacle_cost * 5
            
        self.cost_map = cost_map
        
    def draw_path(self,path):
        plt.plot(path[:,0],path[:,1])

    def set_goal(self, x, y):
        # Check if the goal is on the map and not on an obstacle
        assert (0 <= x < self.grid_size) and (0 <= y < self.grid_size), 'Goal is not on the map.'
        assert self.cost_map[x,y] != self.obstacle_cost, 'Goal cannot be an obstacle.'
        
        # Assign goal
        plt.scatter(x,y,color='red', linewidth = 3)
        self.goal = (x, y)
        
    def set_start(self, x, y):
        # Check if the start is on the map and not on an obstacle
        assert (0 <= x < self.grid_size) and (0 <= y < self.grid_size), 'Start is not on the map.'
        assert self.cost_map[x,y] != self.obstacle_cost, 'Start cannot be an obstacle.'
        
        # Assign the goal
        plt.scatter(x,y,color='green',linewidth = 3)
        self.start = (x, y)

    def cost_function(self, position, control):
        distance_cost = np.linalg.norm(position - self.goal)  # linalg.norm is the euclidean distance

        collision_cost = 0
        if position[0] < 0 or position[0] >= self.cost_map.shape[0] or position[1] < 0 or position[1] >= self.cost_map.shape[1]:
            collision_cost = 100
        else:
            collision_cost = self.cost_map[int(position[0]), int(position[1])]
        
        # experiment
        direction_cost = np.dot((position - self.goal) / np.linalg.norm(position - self.goal), control / np.linalg.norm(control))

        return distance_cost + collision_cost * 1e15 + direction_cost * 1e8

    def generate_path(self):
        # MPPI implementation
        position = self.start
        path = [position]
        prediction_horizon = 30 # Was num_samples
        control_horizon = 5 # Was num_iterations
        control_sequence = np.array([(0, 0) for _ in range(control_horizon)])
        
        # While the robot is not within some tolerance of the goal position
        while abs(int(position[0]) - self.goal[0]) > 0.5 or abs(int(position[1]) - self.goal[1]) > 0.5:
            
            # Random simulated noise
            noise = np.random.normal(0, 1, (control_horizon, prediction_horizon, 2))
            controls = control_sequence[:, None, :] + noise
            
            # Build control sequence over 
            simulated_position = position
            cost = np.array([0 for _ in range(prediction_horizon)])
            for i in range(prediction_horizon):
                for j in range(control_horizon):
                    simulated_position = simulated_position + controls[j, i]
                    cost[i] += self.cost_function(simulated_position, controls[j, i])
            # weights cannot be too small thus add np.min(cost)
            weights = np.exp(((-cost)+np.min(cost)) / self.lambda_)
            total_weight = np.sum(weights)
            print(weights, total_weight)
            if total_weight == 0:  # Handle division by zero
                weights = np.ones_like(weights) / len(weights)  # Assign uniform weights
            else:
                weights /= total_weight
            for i in range(control_horizon):
                control_sequence[i] = np.sum(weights[:, None] * controls[i, :], axis=0)
                
            # Apply first control in the sequence
            position = position + control_sequence[0]
            path.append(position)
            control_sequence = np.roll(control_sequence, -1, axis=0)
            control_sequence[-1] = (0, 0)
        return np.array(path)
        
        
def main():
    
    # Generate costmap and make obstacles
    mppi_obj = MPPI(grid_size=100)
    mppi_obj.make_obstacles(num_obstacles=50,cost_map=mppi_obj.cost_map, obstacle_size=5,build_wall=True)
    plt.matshow(mppi_obj.cost_map)
    plt.colorbar()  # Add a color scale for reference
    
    mppi_obj.set_start(10, 10)
    mppi_obj.set_goal(90, 90)

    # Generate the map
    path = mppi_obj.generate_path()
    
    mppi_obj.draw_path(path)
    plt.show()
    
if __name__ == "__main__":
    main()