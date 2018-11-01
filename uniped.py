'''

This implements the unipedal kangaroo and pogo using the OpenAI Gym interface

'''

# external libraries
import Box2D.b2 as b2
import gym
import gym.utils

# internal libraries
import engine
import contact

# Time (in seconds) to be considered finished with the simulation
MAX_TIME = 60.0 * 2.0

# Helper functions
def draw_text(eng, text, location):
    text_surface = eng.font.render(text, True, (80, 80, 80))
    eng.screen.blit(text_surface, location)

# Uniped class
class Uniped(gym.Env):
    # The (box2d-based) physics engine
    eng = None

    # World params
    objects = []
    joints = []
    key_events = []
    control_events = []

    # State
    prev_state = None
    curr_epoch = 0
    prev_dist = 0
    prev_foot = False

    # Render params
    obj_to_follow = None

    # RL params
    actions = []

    # ===== OPENAI GYM STUFF =====
    # (ignore for now)

    # RL params
    # TODO
    action_space = None
    observation_space = None
    reward_range = None

    # OpenAI Gym params
    metadata = {
        'render.modes': ['human'],
        'video.frames_per_second' : 60
    }

    def __init__(
        self,
        objects=[], joints=[], key_events=[], control_events=[],
        obj_to_follow='',
        render_window=True, render_video=False, video_file=None
    ):
        # Create members
        self.eng = engine.Engine(
            contact.Hit_body_ground(),
            render_window, render_video, video_file
        )
        self.objects = objects
        self.joints = joints
        self.key_events = key_events
        self.control_events = control_events
        self.obj_to_follow = obj_to_follow

        # Create action space
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        for m in range(3):
                            self.actions.append([i, 3 + j, 6 + k, 9 + l, 12 + m])

        # Initialize engine and objects in engine
        self._reset()

        # Run initialization functions
        self._seed()

    # =====
    # OpenAI Gym interface
    # =====

    def _seed(self, seed=None):
        pass

    def _reset(self):
        # Clear all objects from the engine
        self.eng.reset()

        # Re-add all the objects to the engine
        for obj in self.objects:
            self.eng.add_object(**obj)

        for joint in self.joints:
            self.eng.add_joint(**joint)

        # Increment current epoch
        self.curr_epoch += 1

        # Get state
        return self._get_vector_state()

    def _render(self, mode='human', close=False):
        if not close:
            state = self._get_state()
            body_pos = state['bodies']['body']['position']
            text = [
                {
                    'fn': draw_text,
                    'args': {
                        'text': 'x-distance: ' + str(body_pos[0]),
                        'location': (8, 0)
                    }
                },
                {
                    'fn': draw_text,
                    'args': {
                        'text': 'current epoch: ' + str(self.curr_epoch),
                        'location': (8, 16)
                    }
                }
            ]
            self.eng.render(self.obj_to_follow, True, False, text)

    def _step(self, action):
        # Apply action
        if action in range(0, 8):
            control_idx = self.actions[action]
            controls = [self.control_events[idx] for idx in control_idx]
        else:
            controls = []
        self.eng.handle_controls(self.key_events, controls, self)
        self.eng.step()

        state = self._get_state()
        # Return:
        # observation (object),
        observation = self._get_vector_state()
        # reward (float),
        reward = self._get_reward(state)
        # done (bool),
        done = self._is_done(state)
        # custom info (dict)
        custom = {
            "foot_hit_ground": self._foot_hit_ground(state),
            "foot_edge": self._get_and_set_edge_foot(state)
        }
        return observation, reward, done, custom

    def _close(self):
        if self.eng is not None:
            self.eng.quit()

    # =====
    # Helpers and custom functions
    # =====

    # ===== State checks =====

    def _get_state(self):
        return self.eng.get_state()

    def _get_vector_state(self):
        state = self._get_state()
        vec_state = []

        offset_x, offset_y = state['bodies']['body']['position']
        offset_y = 0

        for key in sorted(state['bodies'].keys()):
            if key != 'ground' and key != 'mouse' and key != 'foot':
                position = state['bodies'][key]['position']
                relative_x = position[0] - offset_x
                relative_y = position[1] - offset_y

                vec_state.append(relative_x)
                vec_state.append(relative_y)
                vec_state.append(state['bodies'][key]['angle'])

                vec_state += state['bodies'][key]['lin_vel']
                vec_state.append(state['bodies'][key]['ang_vel'])

        for key in sorted(state['joints'].keys()):
            if key != 'joint_mouse' and key != 'joint_bottom':
                vec_state.append(state['joints'][key]['force'])

        return vec_state

    def _get_distance(self, state, obj_name, get_x=True, value='position'):
        if obj_name in state['bodies']:
            if get_x:
                return state['bodies'][obj_name][value][0]
            else:
                return state['bodies'][obj_name][value][1]
        else:
            return 0

    def _get_total_distance(self, state):
        return self._get_distance(state, 'body')

    def _get_and_reset_delta_distance(self, state):
        curr_dist = self._get_total_distance(state)
        delta = curr_dist - self.prev_dist
        self.prev_dist = curr_dist
        return delta

    def _check_hit_ground(self, state, obj_name):
        if obj_name in state['bodies']:
            if (
                'hit_ground' in state['bodies'][obj_name]['custom_data'] and 
                state['bodies'][obj_name]['custom_data']['hit_ground']
            ):
                return True
            else:
                return state['bodies'][obj_name]['position'][1] <= 0
        else:
            return False

    def _foot_hit_ground(self, state):
        return self._check_hit_ground(state, 'foot')

    def _get_and_set_edge_foot(self, state):
        prev_foot = self.prev_foot
        curr_foot = self._foot_hit_ground(state)
        self.prev_foot = curr_foot
        return prev_foot == curr_foot

    # ===== Rewards =====

    def _get_reward(self, state):
        if self._done_hit_ground(state):
            return -1.0
        else:
            y_vel = self._get_distance(state, 'body', False, 'lin_vel')
            head_y = self._get_distance(state, 'head', False)
            body_y = self._get_distance(state, 'body', False)
            foot_y = self._get_distance(state, 'foot', False)
            return (
                #0.01 * self._get_total_distance(state) + 
                0.8 * self._get_and_reset_delta_distance(state) + 
                0#0.005 * int(y_vel > 0.0) * y_vel +
                #-1 * int(y_vel < 0.0) +
                #2 * int(head_y > body_y) + 
                #5 * int(foot_y < body_y) +
                #-10 * int(foot_y > body_y)
            )

    # ===== Finished conditions =====

    def _is_done(self, state):
        return (
            self._done_hit_ground(state) or
            self._done_reached_time(state) or
            self._done_reached_distance(state)
        )

    def _done_hit_ground(self, state):
        return self._done_body_hit_ground(state) or self._done_head_hit_ground(state)

    def _done_body_hit_ground(self, state):
        return self._check_hit_ground(state, 'body')

    def _done_head_hit_ground(self, state):
        return self._check_hit_ground(state, 'head')

    def _done_reached_time(self, state):
        if state['ticks'] * engine.TIME_STEP >= MAX_TIME:
            return True
        else:
            return False

    def _done_reached_distance(self, state):
        if self._get_total_distance(state) >= engine.GROUND_WIDTH:
            return True
        else:
            return False
