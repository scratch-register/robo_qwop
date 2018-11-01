'''

This runs the box2d engine with pygame visualizations

'''

import Box2D
import Box2D.b2 as b2
import pygame
import pygame.font
import pygame.gfxdraw
import sys

# =====
# Globals
# =====

PPM = 30.0 # Pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
GROUND_WIDTH = 300
GROUND_START = GROUND_WIDTH - 40

# ======
# Accessory functions
# =====

def usim_draw_poly(polygon, body, fixture, screen, camera_x=0, camera_y=0):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    vertices = [(v[0] - camera_x, SCREEN_HEIGHT - v[1] - camera_y) for v in vertices]
    pygame.draw.polygon(screen, body.color, vertices)

    if body.userData['name'] == 'ground':
        # Texture ground
        try:
            grass = pygame.image.load('grass.jpg').convert()
            pygame.gfxdraw.textured_polygon(
                screen, vertices, grass, int(-camera_x), int(-camera_y)
            )
        except:
            pass
b2.polygonShape.draw = usim_draw_poly

def usim_draw_circle(circle, body, fixture, screen, camera_x=0, camera_y=0):
    position = body.transform * circle.pos * PPM
    position = (position[0] - camera_x, SCREEN_HEIGHT - position[1] - camera_y)
    pygame.draw.circle(
        screen, body.color,
        [int(x) for x in position],
        int(circle.radius * PPM)
    )
b2.circleShape.draw = usim_draw_circle

def convert_coords_world2disp(point, camera_x=0, camera_y=0):
    point = [v * PPM for v in point]
    point = [point[0] - camera_x, SCREEN_HEIGHT - point[1] - camera_y]
    return point

def convert_coords_disp2world(point):
    point = [point[0], SCREEN_HEIGHT - point[1]]
    point = [int(v / PPM) for v in point]
    return point

# =====
# Basically the engine object
# =====
class Engine():

    # =====
    # Physics parameters
    # =====
    world = None

    # =====
    # Rendering parameters
    # =====

    # Frames and dimensions
    screen = None
    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    clock = pygame.time.Clock()

    # Render destination
    render_window = True # Show rendering in a window
    render_video = False # Save rendering to video on disk
    video_file = None

    # Decorations
    font = None

    # =====
    # World objects and state
    # =====
    num_ticks = 0
    bodies = {}
    joints = {}

    def __init__(
        self,
        contactListener=None,
        render_window=True, render_video=False, video_file=None,
        font='arial', font_size=16
    ):
        # Initialize rendering destination params
        self.render_window = render_window
        self.render_video = render_video
        self.video_file = video_file
        if self.render_video and video_file is None:
            raise ValueError('Engine error: Specified rendering to video, but did not specify file name')

        # Initialize world
        self.world = b2.world(
            gravity = (0, -50),
            doSleep = True,
            contactListener = contactListener
        )

        # Create ground
        self.add_object(
            'ground',
            {
                'position': (GROUND_START, 0)
            },
            'poly',
            {
                'box': (GROUND_WIDTH, 5),
                'friction': 0.5
            },
            (80, 80, 80, 255),
            True,
            0x01
        )

        # Create mouse
        self.add_object(
            'mouse',
            {
                'position': (0, 0)
            },
            None,
            None
        )

        # Initialize pygame modules
        pygame.init()
        pygame.font.init()

        # Initialize rendering decorations
        self.font = pygame.font.SysFont(font, font_size)

    def reset(self):
        # Remove joints
        for joint_key in self.joints:
            joint = self.joints[joint_key]
            if joint is not None:
                self.world.DestroyJoint(self.joints[joint_key])
                self.joints[joint_key] = None

        # Remove objects
        for body_key in self.bodies:
            body = self.bodies[body_key]
            if body is not None and body_key != 'mouse' and body_key != 'ground':
                self.world.DestroyBody(self.bodies[body_key])
                self.bodies[body_key] = None

        # Reset time
        self.num_ticks = 0

        # Clean up internal data structures
        self.cleanup()

    def cleanup(self):
        joint_keys = list(self.joints.keys())
        for key in joint_keys:
            if self.joints[key] is None:
                self.joints.pop(key)

        body_keys = list(self.bodies.keys())
        for key in body_keys:
            if self.bodies[key] is None:
                self.bodies.pop(key)

    def add_object(self, name, obj_args, shape_type, shape_args, color=(50, 50, 50, 100), fixed=False, category=0x00):
        # And objects to the world
        if fixed:
            obj = self.world.CreateStaticBody(**obj_args)
        else:
            obj = self.world.CreateDynamicBody(**obj_args)

        if shape_type == 'poly':
            obj.CreatePolygonFixture(**shape_args)
        elif shape_type == 'circle':
            obj.CreateCircleFixture(**shape_args)
        obj.color = color
        obj.userData = {
            'name': name
        }
        self.bodies[name] = obj
        if len(self.bodies[name].fixtures) > 0:
            self.bodies[name].fixtures[0].filterData.categoryBits = category

    def add_joint(self, name, joint_type, obj1_name, obj2_name, joint_args, anchor_offset=None):
        joint = None

        if anchor_offset is None:
            anchor_offset = 0
        anchor = self.bodies[obj1_name].worldCenter + anchor_offset

        if joint_type == 'revolute':
            joint = self.world.CreateRevoluteJoint(
                bodyA = self.bodies[obj1_name],
                bodyB = self.bodies[obj2_name],
                anchor = anchor,
                **joint_args
            )
        elif joint_type == 'prismatic':
            joint = self.world.CreatePrismaticJoint(
                bodyA = self.bodies[obj1_name],
                bodyB = self.bodies[obj2_name],
                anchor = anchor,
                **joint_args
            )
        elif joint_type == 'weld':
            joint = self.world.CreateWeldJoint(
                bodyA = self.bodies[obj1_name],
                bodyB = self.bodies[obj2_name],
                anchor = anchor
            )
            joint.frequencyHz = 0
            joint.dampingRatio = 1
        elif joint_type == 'rope':
            r_joint = Box2D.b2RopeJointDef(
                bodyA = self.bodies[obj1_name],
                bodyB = self.bodies[obj2_name],
                **joint_args
            )
            joint = self.world.CreateJoint(r_joint)

        if joint is not None:
            self.joints[name] = joint
        else:
            raise ValueError('Unsupported joint type ' + joint_type + ' was specified')

    def get_state(self):
        state = {
            'ticks': self.num_ticks,
            'bodies': {},
            'joints': {}
        }

        for body in self.bodies:
            state['bodies'][body] = {}
            state['bodies'][body]['position'] = list(self.bodies[body].position)
            state['bodies'][body]['angle'] = self.bodies[body].angle
            state['bodies'][body]['lin_vel'] = self.bodies[body].linearVelocity
            state['bodies'][body]['ang_vel'] = self.bodies[body].angularVelocity
            state['bodies'][body]['custom_data'] = self.bodies[body].userData

        for joint in self.joints:
            state['joints'][joint] = {}
            if hasattr(self.joints[joint], 'motorSpeed'):
                state['joints'][joint]['force'] = self.joints[joint].motorSpeed
            else:
                state['joints'][joint]['force'] = 0

        return state

    def get_camera_position(self, obj_to_track='', follow_x=True, follow_y=True):
        # Get camera offsets
        camera_x = 0
        camera_y = 0
        if obj_to_track in self.bodies and (follow_x or follow_y):
            position = list(self.bodies[obj_to_track].position)
            camera_x, camera_y = convert_coords_world2disp(position)
            camera_x -= 0.5 * SCREEN_WIDTH
            camera_y -= 0.5 * SCREEN_HEIGHT
            if not follow_x:
                camera_x = 0
            if not follow_y:
                camera_y = 0

        return camera_x, camera_y

    def loop(self, key_events=[], controls=[]):
        while True:
            self.loop_once(key_events, controls)

    def loop_once(self, key_events=[], controls=[]):
        self.handle_controls(key_events, controls)
        self.render()

    def handle_controls(self, key_events=[], controls=[], custom_dat=None):
        # Capture events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                sys.exit()
            #elif (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
            #    for joint_key in self.joints:
            #        world.DestroyJoint(self.joints[joint_key])
            #        self.joints[joint_key] = None 
            for key_event in key_events:
                if event.type == key_event['type']:
                    if key_event['key'] is None or event.key == key_event['key']:
                        key_event['fn'](
                            self,
                            self.world,
                            self.bodies,
                            key_event['body_names'],
                            self.joints,
                            key_event['joint_names'],
                            custom_dat
                        )

        # Handle custom controls
        for control in controls:
            control['fn'](
                self,
                self.world,
                self.bodies,
                control['body_names'],
                self.joints,
                control['joint_names'],
                custom_dat
            )

        # Cleanup if necessary
        self.cleanup()

        # Update mouse
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos = convert_coords_disp2world(mouse_pos)
        self.bodies['mouse'].position = mouse_pos

        # Update bodies attached to mouse
        if 'joint_mouse' in self.joints:
            self.joints['joint_mouse'].bodyA.position = mouse_pos

    def step(self):
        # Advance timestep
        self.num_ticks += 1
        self.world.Step(TIME_STEP, 10, 10)
        self.clock.tick(TARGET_FPS)

    def render(self, obj_to_track='', follow_x=True, follow_y=True, custom_render=[]):
        if not self.render_window and not self.render_video:
            raise AttributeError(
                'Attempted to render, but user set Engine render_window and render_video flags to False'
            )

        # Define screen if it does not exist yet
        if self.screen is None:
            size = self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
            if self.render_window:
                # Create display
                self.screen = pygame.display.set_mode(size)
                pygame.display.set_caption('usim2.0')
            else:
                # Create surface and do NOT display it
                self.screen = pygame.Surface(size)

        # Clear canvas
        #self.screen.fill((0, 180, 255))
        self.screen.fill((60, 120, 216))

        camera_x, camera_y = self.get_camera_position(obj_to_track, follow_x, follow_y)

        # Render objects
        for body_key in self.bodies:
            body = self.bodies[body_key]
            if body.fixtures is not None:
                for fixture in body.fixtures:
                    fixture.shape.draw(
                        body, fixture, self.screen, camera_x, camera_y
                    )

        # Render joints
        for joint_key in self.joints:
            joint = self.joints[joint_key]
            if joint is not None:
                point1 = list(joint.anchorA)
                point2 = list(joint.anchorB)
                vert1 = convert_coords_world2disp(point1, camera_x, camera_y)
                vert2 = convert_coords_world2disp(point2, camera_x, camera_y)
                pygame.draw.line(self.screen, (200, 100, 80, 100), vert1, vert2, 2)

        # Custom rendering
        for custom in custom_render:
            custom['fn'](
                self,
                **custom['args']
            )

        # Swap buffers (draw new frame)
        if self.render_window:
            pygame.display.flip()

    def quit(self):
        pygame.quit()

if __name__ == '__main__':
    eng = Engine()

    eng.loop()
