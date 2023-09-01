import numpy as np
import ifcopenshell
from ifcopenshell.api import run


class IFCModelGenerator:
    model = None
    body = None
    storey = None

    def __init__(self):
        self.__create_empty_model()

    def __create_empty_model(self):
        # Create a blank model
        self.model = ifcopenshell.file()
        # All projects must have one IFC Project element
        project = run("root.create_entity", self.model, ifc_class="IfcProject", name="My Project")
        # Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
        # Assigning without arguments defaults to metric units
        run("unit.assign_unit", self.model)
        # Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
        context = run("context.add_context", self.model, context_type="Model")
        # In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
        self.body = run(
            "context.add_context", self.model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
        )
        # Create a site, building, and storey. Many hierarchies are possible.
        site = run("root.create_entity", self.model, ifc_class="IfcSite", name="My Site")
        building = run("root.create_entity", self.model, ifc_class="IfcBuilding", name="Building A")
        self.storey = run("root.create_entity", self.model, ifc_class="IfcBuildingStorey", name="Ground Floor")
        # Since the site is our top level location, assign it to the project
        # Then place our building on the site, and our storey in the building
        run("aggregate.assign_object", self.model, relating_object=project, product=site)
        run("aggregate.assign_object", self.model, relating_object=site, product=building)
        run("aggregate.assign_object", self.model, relating_object=building, product=self.storey)

    def create_wall(self, name, length=5, height=3, thickness=0.2):
        wall = run("root.create_entity", self.model, ifc_class="IfcWall", name=name)

        representation = run("geometry.add_wall_representation", self.model, context=self.body, length=length,
                             height=height, thickness=thickness)
        run("geometry.edit_object_placement", self.model, product=wall)

        run("geometry.assign_representation", self.model, product=wall, representation=representation)
        run("spatial.assign_container", self.model, relating_structure=self.storey, product=wall)
        return wall

    def rotate_wall(self, wall, rotation_matrix):
        run("geometry.edit_object_placement", self.model, product=wall, matrix=rotation_matrix)

    def create_opening(self, name, element, length, height, matrix, thickness=0.4):

        opening = run("root.create_entity", self.model, ifc_class="IfcOpeningElement", name=name)
        representation_open = run("geometry.add_wall_representation", self.model,
                                  context=self.body, length=length, height=height, thickness=thickness)
        run("geometry.assign_representation", self.model,
            product=opening, representation=representation_open)
        run("geometry.edit_object_placement", self.model, product=opening, matrix=matrix)
        run("void.add_opening", self.model, opening=opening, element=element)
        return opening

    def create_door(self, name, opening, width, height, thickness, matrix):
        door = run("root.create_entity", self.model, ifc_class="IfcDoor", name=name)
        run("geometry.edit_object_placement", self.model, product=door, relative_to=opening, matrix=matrix)
        door_representation = run("geometry.add_door_representation", self.model, context=self.body, width=width,
                                  height=height, thickness=thickness)
        run("geometry.assign_representation", self.model, product=door, representation=door_representation)

        return door

    # Establish relationships using IfcRelAggregates
    def create_window(self, name, opening, thickness, matrix):
        window = run("root.create_entity", self.model, ifc_class="IfcWindow", name=name)
        window_representation = run("geometry.add_window_representation", self.model, context=self.body,
                                    thickness=thickness)
        run("geometry.assign_representation", self.model, product=window, representation=window_representation)
        run("geometry.edit_object_placement", self.model, product=window, relative_to=opening, matrix=matrix)

        return window

    def create_relationship_aggregates(self, name, relating_object, related_objects):
        relationship = run("root.create_entity", self.model, ifc_class="IfcRelAggregates", name=name)
        relationship.RelatingObject = relating_object
        relationship.RelatedObjects = related_objects
        return relationship

    def write_to_file(self, file_path):
        self.model.write(file_path)


if __name__ == '__main__':
    model = IFCModelGenerator()

    # wall1
    wall1 = model.create_wall("wall1")

    # opening door
    door_opening_matrix = np.identity(4)
    door_opening_matrix[:, 3] = [3, -.1, 0, 0]

    d_length = .95
    d_height = 2.1

    door_opening = model.create_opening("door_opening", wall1, .95, d_height, matrix=door_opening_matrix)

    # create door
    door = model.create_door("mydoor", door_opening, .9, d_height, 0.05, door_opening_matrix)
    model.create_relationship_aggregates("opening_v_door", door_opening, [door])

    # wall2
    # Rotate our wall along the Y axis by 90 degrees
    rotation_matrix = np.array([
        [0., -1., 0., 0.],
        [1., 0., 0., 0.],
        [0., 0., 1., 0.],
        [0., 0., 0., 1.]
    ])

    coordinates = (5., 0., 0.)
    wall2 = model.create_wall("wall2")
    model.rotate_wall(wall2, rotation_matrix)

    # windows_opening
    window_width, window_height = 0.6, 0.9
    opening_matrix = np.array([
        [0., -1., 0., 0],
        [1., 0., 0., 2],
        [0., 0., 1., 1.5],
        [0., 0., 0., 1.]
    ])
    windows_opening = model.create_opening("windows_opening", wall2, window_width * 2, window_height,
                                           matrix=opening_matrix)

    # windwos
    window1 = model.create_window("window1", windows_opening, 0.05, opening_matrix)
    opening_matrix2 = np.array([
        [0., -1., 0., 0],
        [1., 0., 0., 2 + window_width],
        [0., 0., 1., 1.5],
        [0., 0., 0., 1.]
    ])
    window2 = model.create_window("window2", windows_opening, 0.05, opening_matrix2)
    model.create_relationship_aggregates("Wall Contains window", windows_opening, [window1, window2])
    model.write_to_file("wall_door_window.ifc")
