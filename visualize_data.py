import time
import pickle

import open3d as o3d

from call_programs import kinect_names,kinect_connections,create_initial_dict

if __name__ == "__main__":
    kinect_data = []
    with open('exercise_final.pkl', "rb") as input_file:
        complete_data = pickle.load(input_file)
        kinect_data = [value for key,value in complete_data if key=="kinect"]    

    vis = o3d.visualization.Visualizer()
    vis.create_window()

    
    kinect_json = kinect_data[72]
    kinect_json.pop("completeness")
    kinect_json.pop("instability")
    
    points = [[v["x"], v["y"], v["z"]] for v in kinect_json.values()]
    lines = [[list(kinect_json.keys()).index(a), list(kinect_json.keys()).index(b)] for a, b in kinect_connections]
    
    line_set = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(points),
        lines=o3d.utility.Vector2iVector(lines),
    )
    vis.add_geometry(line_set)

    # coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)
    # vis.add_geometry(coord_frame)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.paint_uniform_color([0, 1, 0])  # Green points

    vis.add_geometry(pcd)

    kinect_data = kinect_data[73:]

    set_camera = False

    for i,kinect_json in enumerate(kinect_data):

        kinect_json.pop("completeness")
        kinect_json.pop("instability")

        points = [[v["x"], v["y"], v["z"]] for v in kinect_json.values()]
        line_set.points = o3d.utility.Vector3dVector(points)
        pcd.points = o3d.utility.Vector3dVector(points)
        vis.update_geometry(line_set)
        vis.update_geometry(pcd)
        # Add a frame to initialize the renderer
        vis.poll_events()
        vis.update_renderer()

        if not set_camera:
            set_camera = True
            # Now safely set the camera
            ctr = vis.get_view_control()

            eye = [4, 1.5, 4]
            lookat = [0, 0, 0]
            up = [0, 1, 0]
            front = [lookat[i] - eye[i] for i in range(3)]

            ctr.set_lookat(lookat)
            ctr.set_front(front)
            ctr.set_up(up)
            ctr.set_zoom(0.5)

        time.sleep(0.25)
        # time.sleep(1.0)