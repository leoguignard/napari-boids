import numpy as np
from scipy.spatial import KDTree

class BoidFlock:
    def get_neighbours(self, dist=None):
        kdt = KDTree(self.pos)
        if dist is None:
            neighbs = kdt.query_ball_tree(kdt, self.vision)
            self.neighbours = [self.pos[k[1:]] for k in neighbs]
            self.neighbours_velocity = [self.velocity[k[1:]] for k in neighbs]
        else:
            neighbs = kdt.query_ball_tree(kdt, dist)
            return [self.pos[k[1:]] for k in neighbs]

    def displacement_to_com(self):
        coms = np.array([np.mean(k, axis=0) for k in self.neighbours])
        coms[np.isnan(coms)] = self.pos[np.isnan(coms)]
        return (coms - self.pos)

    def away_from_each_other(self):
        close_neighbs = self.get_neighbours(self.repulsion_range)
        AFEO = np.array([np.sum(self.pos[i] - n, axis=0) for i, n in enumerate(close_neighbs)])
        AFEO[np.isnan(AFEO)] = 0
        return AFEO

    def velocity_match(self):
        avg_velocity = np.array([np.mean(v, axis=0) if 0<len(v) else [0,]*self.dim
                                 for v in self.neighbours_velocity])
        return avg_velocity - self.velocity

    def keep_in(self):
        change = np.zeros_like(self.pos)
        change[self.pos<self.margin] = 1
        change[self.arena_shape-self.margin<self.pos] = -.5
        return change

    def limit_speed(self):
        speed = np.linalg.norm(self.velocity, axis=1)
        fast_mask = self.speed_limit<speed
        too_fast = self.velocity[fast_mask]
        too_fast = (too_fast.T/speed[fast_mask] * self.speed_limit).T
        self.velocity[fast_mask] = too_fast

        slow_mask = speed<self.speed_limit_low
        too_slow = self.velocity[slow_mask]
        too_slow = (too_slow.T/speed[slow_mask] * self.speed_limit_low).T
        self.velocity[slow_mask] = too_slow

    def _move_boids(self):
        self.get_neighbours()
        dp1 = self.displacement_to_com();
        dp2 = self.away_from_each_other();
        dp3 = self.velocity_match();
        keep_in = self.keep_in()
        self.velocity = (self.velocity +
                         self.rdp1*dp1 +
                         self.rdp2*dp2 +
                         self.rdp3*dp3 +
                         keep_in)
        self.limit_speed()
        self.pos += self.velocity

        return dp1, dp2, dp3

    def move_boids(self, nb_it=1):
        for i in range(nb_it):
            self._move_boids()

    def add_boid(self, pos):
        self.nb_boids += 1
        self.pos = np.vstack([self.pos, pos])
        self.velocity = np.vstack([self.velocity, (np.random.random([1, 2])-.5)*self.speed_limit])

    def remove_boid(self, pos):
        self.nb_boids -= 1
        old_id = np.where(self.pos==pos)[0][0]
        self.pos = np.vstack((self.pos[:old_id], self.pos[old_id+1:]))
        self.velocity = np.vstack((self.velocity[:old_id], self.velocity[old_id+1:]))

    def __init__(self, nb_boids, vision=5, init_positions=None,
                 arena_shape=(100, 100), init_shape=None, reflection=True,
                 rdp1=.2, rdp2=.2, rdp3=.2, speed_limit=15, margin=10,
                repulsion_range=20):
        self.nb_boids = nb_boids
        self.boids = set(range(nb_boids))
        self.vision = vision
        self.arena_shape = np.array(arena_shape)
        self.dim = len(arena_shape)
        self.reflection = reflection
        self.rdp1 = rdp1
        self.rdp2 = rdp2
        self.rdp3 = rdp3
        self.speed_limit = speed_limit
        self.margin = margin
        self.repulsion_range = repulsion_range
        if init_shape == None:
            self.init_shape = np.array([[0, arena_shape[0]], [0, arena_shape[1]]])
        else:
            init_shape = np.array(init_shape)
            init_shape[:, 0][init_shape[:, 0]<0] = 0
            init_shape[:, 1][self.arena_shape < init_shape[:, 1]] = self.arena_shape[self.arena_shape <
                                                                                     init_shape[:, 1]]-1
            self.init_shape = init_shape
        if init_positions is None or init_positions.shape!=(self.nb_boids, self.dim):
            pos = np.random.random((self.nb_boids, self.dim))
            pos *= (self.init_shape[:, 1] - self.init_shape[:, 0])
            pos += self.init_shape[:, 0]
            self.pos = pos
        else:
            self.pos = init_positions

        # self.velocity = np.zeros_like(self.pos)
        self.speed_limit_low = .5
        self.velocity = (np.random.random(self.pos.shape)-.5)*self.speed_limit
        self.color = np.random.random((self.pos.shape[0]))