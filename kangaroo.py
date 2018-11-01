import Box2D.b2 as b2

import engine
import pygame

# Groups for filtering collisions
# NOTE: the ground by default has collision category 01
ROBOT_NOGROUND = 0x01 # do not collide some robot components with the ground
ROBOT = 0x02 # do not collide robot components with themselves

objects = [
    {
        "name": "body",
        "obj_args": {
            "position": (0, 10),
            "angle": 0
        },
        "shape_type": "poly",
        "shape_args": {
            "box": (0.8, 0.5),
            "density": 0.5,
            "friction": 0.3
        },
        "category": ROBOT
    },
    {
        "name": "leg_thigh",
        "obj_args": {
            "position": (0, 9.7),#(-0.3, 9.7),
            "angle": 0
        },
        "shape_type": "poly",
        "shape_args": {
            "box": (0.25, 0.4),
            "density": 1,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "leg_upper",
        "obj_args": {
            "position": (0, 8.65),#(-0.3, 8.65),
            "angle": 0
        },
        "shape_type": "poly",
        "shape_args": {
            "box": (0.1, 0.6),
            "density": 1,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "leg_lower",
        "obj_args": {
            "position": (0, 7.5),#(-0.3, 7.5),
            "angle": 0
        },
        "shape_type": "poly",
        "shape_args": {
            "box": (0.1, 0.6),
            "density": 1,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "foot",
        "obj_args": {
            "position": (0, 6.9),#(-0.3, 6.9),
            "angle": 0
        },
        "shape_type": "circle",
        "shape_args": {
            "radius": 0.15,
            "density": 1,
            "friction": 3.5
        },
        "category": ROBOT
    },
    {
        "name": "tail1",
        "obj_args": {
            "position": (-(0.5 + 0.8), 10),
            "angle": 0
        },
        "shape_type": "circle",
        "shape_args": {
            "radius": 0.2,
            "density": 0.5,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "tail2",
        "obj_args": {
            "position": (-(1.0 + 0.8), 10),
            "angle": 0
        },
        "shape_type": "circle",
        "shape_args": {
            "radius": 0.12,
            "density": 0.5,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "tail3",
        "obj_args": {
            "position": (-(1.5 + 0.8), 10),
            "angle": 0
        },
        "shape_type": "circle",
        "shape_args": {
            "radius": 0.08,
            "density": 0.5,
            "friction": 0.3
        },
        "category": ROBOT | ROBOT_NOGROUND
    },
    {
        "name": "head",
        "obj_args": {
            "position": ((1.8 + 0.8), 10),
            "angle": 0
        },
        "shape_type": "circle",
        "shape_args": {
            "radius": 0.25,
            "density": 1,
            "friction": 0.3
        },
        "category": ROBOT
    }
]

'''
foot

        "shape_type": "poly",
        "shape_args": {
            "box": (0.15, 0.05),
            "density": 1,
            "friction": 0.3
        },


        "shape_type": "circle",
        "shape_args": {
            "radius": 0.15,
            "density": 1,
            "friction": 0.9
        },






head

        "shape_type": "poly",
        "shape_args": {
            "box": (0.3, 0.2),
            "density": 1,
            "friction": 0.3
        },

        "shape_type": "circle",
        "shape_args": {
            "radius": 0.25,
            "density": 1,
            "friction": 0.3
        },

'''

joints = [
    {
        "name": "joint_thigh",
        "joint_type": "revolute",
        "obj1_name": "body",
        "obj2_name": "leg_thigh",
        "joint_args": {
            "lowerAngle": -1.0 * b2.pi, # -90 degrees
            "upperAngle": b2.pi, # 90 degrees
            "enableLimit": True,
            "maxMotorTorque": 500.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0, 0)#(-0.3, 0)
    },
    {
        "name": "joint_top",
        "joint_type": "revolute",
        "obj1_name": "leg_thigh",
        "obj2_name": "leg_upper",
        "joint_args": {
            "lowerAngle": -1.0 * b2.pi,
            "upperAngle": 0,#b2.pi, # 90 degrees
            "enableLimit": True,
            "maxMotorTorque": 100.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0, -0.35)
    },
    {
        "name": "joint_knee",
        "joint_type": "revolute",
        "obj1_name": "leg_upper",
        "obj2_name": "leg_lower",
        "joint_args": {
            "lowerAngle": 0,#-1.0 * b2.pi, # -90 degrees
            "upperAngle": 1.0 * b2.pi, # 90 degrees
            "enableLimit": True,
            "maxMotorTorque": 1000.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0, -0.55)
    },
    {
        "name": "joint_bottom",
        "joint_type": "weld",
        "obj1_name": "leg_lower",
        "obj2_name": "foot",
        "joint_args": {},
        "anchor_offset": (0, -0.6)
    },
    {
        "name": "joint_tail_body1",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "tail1",
        "joint_args": {
            "maxLength": 0.55,
            "localAnchorA": (-0.8, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_body1_rotation",
        "joint_type": "revolute",
        "obj1_name": "body",
        "obj2_name": "tail1",
        "joint_args": {
            "lowerAngle": -(1.0 / 12.0) * b2.pi, # -30 degrees
            "upperAngle": (1.0 / 12.0) * b2.pi, # 30 degrees
            "enableLimit": True,
            "maxMotorTorque": 100.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (-0.8, 0)
    },
    {
        "name": "joint_tail_body2",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "tail2",
        "joint_args": {
            "maxLength": 1.1,
            "localAnchorA": (-0.8, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_body3",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "tail3",
        "joint_args": {
            "maxLength": 1.65,
            "localAnchorA": (-0.8, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_12",
        "joint_type": "rope",
        "obj1_name": "tail1",
        "obj2_name": "tail2",
        "joint_args": {
            "maxLength": 0.55,
            "localAnchorA": (0, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_12_rotation",
        "joint_type": "revolute",
        "obj1_name": "tail1",
        "obj2_name": "tail2",
        "joint_args": {
            "lowerAngle": -(1.0 / 12.0) * b2.pi, # -30 degrees
            "upperAngle": (1.0 / 12.0) * b2.pi, # 30 degrees
            "enableLimit": True,
            "maxMotorTorque": 100.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_23",
        "joint_type": "rope",
        "obj1_name": "tail2",
        "obj2_name": "tail3",
        "joint_args": {
            "maxLength": 0.55,
            "localAnchorA": (0, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_tail_23_rotation",
        "joint_type": "revolute",
        "obj1_name": "tail2",
        "obj2_name": "tail3",
        "joint_args": {
            "lowerAngle": -(1.0 / 12.0) * b2.pi, # -30 degrees
            "upperAngle": (1.0 / 12.0) * b2.pi, # 30 degrees
            "enableLimit": True,
            "maxMotorTorque": 100.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_body_head",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "head",
        "joint_args": {
            "maxLength": 1.7,
            "localAnchorA": (0.8, 0.2),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_body_head2",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "head",
        "joint_args": {
            "maxLength": 1.8,
            "localAnchorA": (0.8, 0.0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_body_head_rotation",
        "joint_type": "revolute",
        "obj1_name": "body",
        "obj2_name": "head",
        "joint_args": {
            "lowerAngle": -0.5 * b2.pi, # -90 degrees
            "upperAngle": 0.5 * b2.pi, # 90 degrees
            "enableLimit": False,
            "maxMotorTorque": 100.0,
            "motorSpeed": 0,
            "enableMotor": True
        },
        "anchor_offset": (0.8, 0)
    },
    {
        "name": "joint_body_legthigh",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "leg_thigh",
        "joint_args": {
            "maxLength": 0.75,
            "localAnchorA": (0.05, 0.1),#(-0.25, 0.1),
            "localAnchorB": (0, -0.4)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_legthigh_legupper",
        "joint_type": "rope",
        "obj1_name": "leg_thigh",
        "obj2_name": "leg_upper",
        "joint_args": {
            "maxLength": 1.05,
            "localAnchorA": (0, -0.3),
            "localAnchorB": (0, -0.45)
        },
        "anchor_offset": (0, 0)
    },
    {
        "name": "joint_legupper_leglower",
        "joint_type": "rope",
        "obj1_name": "leg_upper",
        "obj2_name": "leg_lower",
        "joint_args": {
            "maxLength": 1.15,
            "localAnchorA": (0, -0.40),
            "localAnchorB": (0, -0.45)
        },
        "anchor_offset": (0, 0)
    },
]
'''
    {
        "name": "joint_body_foot",
        "joint_type": "rope",
        "obj1_name": "body",
        "obj2_name": "foot",
        "joint_args": {
            "maxLength": 2.6,
            "localAnchorA": (0.3, 0),
            "localAnchorB": (0, 0)
        },
        "anchor_offset": (0, 0)
    }
]
'''

# ===== CONTROL CONSTANTS =====

FORCE = 100.0
HEAD_FORCE = 50.0
THIGH_FORCE = 200.0

# ===== REMOVE CONSTRAINTS =====

# Remove all joints
def remove_joints(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint_key in joints:
        world.DestroyJoint(joints[joint_key])
        joints[joint_key] = None

# ===== JOINT CONTROLS =====

# Joint counterclockwise
def joint_ccw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed = -1.0 * FORCE

# Joint none
def joint_none(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed = 0

# Joint clockwise
def joint_cw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed = FORCE





# Joint counterclockwise
def joint_h_ccw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed += -1.0 * HEAD_FORCE

# Joint clockwise
def joint_h_cw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed -= HEAD_FORCE




# Joint counterclockwise
def joint_t_ccw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed += -1.0 * THIGH_FORCE

# Joint clockwise
def joint_t_cw(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed -= THIGH_FORCE



# ===== REMOVE JOINT CONTROLS =====

def handle_remove_controls(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            joints[joint].motorSpeed = 0

# ===== RESET =====

def reset(self, world, bodies, body_names, joints, joint_names, custom_dat):
    custom_dat.reset()

# ===== CLICK AND DRAG ROBOT =====

def handle_mousedown(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for body in body_names:
        if body in bodies and bodies[body] is not None:
            for joint in joint_names:
                bodies[body].position = bodies['mouse'].position
                joints[joint] = world.CreateRevoluteJoint(
                    bodyA = bodies[body],
                    bodyB = bodies['mouse'],
                    anchor = bodies[body].worldCenter,
                    collideConnected = False
                )

def handle_mouseup(self, world, bodies, body_names, joints, joint_names, custom_dat):
    for joint in joint_names:
        if joint in joints and joints[joint] is not None:
            world.DestroyJoint(joints[joint])
            joints[joint] = None

key_events = [
    {
        'key': pygame.K_x,
        'type': pygame.KEYDOWN,
        'fn': remove_joints,
        'body_names': [],
        'joint_names': [],
    },
    {
        'key': pygame.K_q,
        'type': pygame.KEYDOWN,
        'fn': joint_ccw,
        'body_names': [],
        'joint_names': ["joint_top"],
    },
    {
        'key': pygame.K_q,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_top"],
    },
    {
        'key': pygame.K_w,
        'type': pygame.KEYDOWN,
        'fn':joint_cw,
        'body_names': [],
        'joint_names': ["joint_top"],
    },
    {
        'key': pygame.K_w,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_top"],
    },
    {
        'key': pygame.K_o,
        'type': pygame.KEYDOWN,
        'fn': joint_ccw,
        'body_names': [],
        'joint_names': ["joint_knee"],
    },
    {
        'key': pygame.K_o,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_knee"],
    },
    {
        'key': pygame.K_p,
        'type': pygame.KEYDOWN,
        'fn': joint_cw,
        'body_names': [],
        'joint_names': ["joint_knee"],
    },
    {
        'key': pygame.K_p,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_knee"],
    },
    {
        'key': pygame.K_e,
        'type': pygame.KEYDOWN,
        'fn': joint_ccw,
        'body_names': [],
        'joint_names': ["joint_thigh"],
    },
    {
        'key': pygame.K_e,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_thigh"],
    },
    {
        'key': pygame.K_i,
        'type': pygame.KEYDOWN,
        'fn': joint_cw,
        'body_names': [],
        'joint_names': ["joint_thigh"],
    },
    {
        'key': pygame.K_i,
        'type': pygame.KEYUP,
        'fn': handle_remove_controls,
        'body_names': [],
        'joint_names': ["joint_thigh"],
    },
    {
        'key': pygame.K_r,
        'type': pygame.KEYDOWN,
        'fn': reset,
        'body_names': [],
        'joint_names': [],
    },
    {
        'key': None,
        'type': pygame.MOUSEBUTTONDOWN,
        'fn': handle_mousedown,
        'body_names': ["body"],
        'joint_names': ["joint_mouse"],
    },
    {
        'key': None,
        'type': pygame.MOUSEBUTTONUP,
        'fn': handle_mouseup,
        'body_names': [],
        'joint_names': ["joint_mouse"],
    }
]

control_events = [
    {
        'event': 'joint_thigh_ccw',
        'fn': joint_h_ccw,
        'body_names': [],
        'joint_names': ['joint_thigh']
    },
    {
        'event': 'joint_thigh_none',
        'fn': joint_none,
        'body_names': [],
        'joint_names': ['joint_thigh']
    },
    {
        'event': 'joint_thigh_cw',
        'fn': joint_h_cw,
        'body_names': [],
        'joint_names': ['joint_thigh']
    },
    {
        'event': 'joint_top_ccw',
        'fn': joint_h_ccw,
        'body_names': [],
        'joint_names': ['joint_top']
    },
    {
        'event': 'joint_top_none',
        'fn': joint_none,
        'body_names': [],
        'joint_names': ['joint_top']
    },
    {
        'event': 'joint_top_cw',
        'fn': joint_h_cw,
        'body_names': [],
        'joint_names': ['joint_top']
    },
    {
        'event': 'joint_knee_ccw',
        'fn': joint_h_ccw,
        'body_names': [],
        'joint_names': ['joint_knee']
    },
    {
        'event': 'joint_knee_none',
        'fn': joint_none,
        'body_names': [],
        'joint_names': ['joint_knee']
    },
    {
        'event': 'joint_knee_cw',
        'fn': joint_h_cw,
        'body_names': [],
        'joint_names': ['joint_knee']
    },
    {
        'event': 'joint_head_ccw',
        'fn': joint_h_ccw,
        'body_names': [],
        'joint_names': ['joint_body_head_rotation']
    },
    {
        'event': 'joint_head_none',
        'fn': joint_none,
        'body_names': [],
        'joint_names': ['joint_body_head_rotation']
    },
    {
        'event': 'joint_head_cw',
        'fn': joint_h_cw,
        'body_names': [],
        'joint_names': ['joint_body_head_rotation']
    },
    {
        'event': 'joint_tail_ccw',
        'fn': joint_h_ccw,
        'body_names': [],
        'joint_names': ['joint_tail_body1_rotation']
    },
    {
        'event': 'joint_tail_none',
        'fn': joint_none,
        'body_names': [],
        'joint_names': ['joint_tail_body1_rotation']
    },
    {
        'event': 'joint_tail_cw',
        'fn': joint_h_cw,
        'body_names': [],
        'joint_names': ['joint_tail_body1_rotation']
    }
]

if __name__ == '__main__':
    import uniped
    up = uniped.Uniped(
        objects, joints, key_events, control_events,
        'body',
        True, False, 'file.ogv'
    )
    while True:
        up.step(None)
        up.render()
        if up._is_done(up._get_state()):
            print('FINISHED!')
            #up.reset()


    '''
    import contact
    eng = engine.Engine(contact.Hit_body_ground())

    for obj in objects:
        eng.add_object(**obj)

    for joint in joints:
        eng.add_joint(**joint)

    eng.loop(key_events)
    '''
