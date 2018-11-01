import Box2D
import Box2D.b2 as b2

# =====
# Contacts
# =====

# Detect if object 'body' hit object 'ground'
class Hit_body_ground(b2.contactListener):
    def __init__(self):
        b2.contactListener.__init__(self)

    def BeginContact(self, contact):
        pass

    def EndContact(self, contact):
        pass

    def PreSolve(self, contact, oldManifold):
        pass

    def PostSolve(self, contact, impulse):
        nameA = contact.fixtureA.body.userData['name']
        nameB = contact.fixtureB.body.userData['name']
        case1 = (nameA == 'ground')
        case2 = (nameB == 'ground')
        if case1:
            contact.fixtureB.body.userData['hit_ground'] = True
        elif case2:
            contact.fixtureA.body.userData['hit_ground'] = True
