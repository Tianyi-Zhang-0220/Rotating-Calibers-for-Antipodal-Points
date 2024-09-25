import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.collections import PathCollection
from scipy.spatial import ConvexHull
import time
import threading

def main():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    points = []
    adding_points = [True]
    map_of_antipodal_points = {}
    hull_point_objects = []

    # Function to plot the convex hull
    def plot_convex_hull(points):
        if len(points) > 2:  # Convex hull is only valid for more than 2 points
            # Compute the convex hull
            hull = ConvexHull(points)
            # Plot the convex hull
            for simplex in hull.simplices:
                ax.plot(points[simplex, 0], points[simplex, 1], 'b-')

            # Plot the points of the convex hull using scatter()
            hull_points = points[hull.vertices]
            scatter_points = ax.scatter(hull_points[:, 0], hull_points[:, 1], color='black', picker = True)
            return hull.vertices
        else:
            return []

    def onclick(event):
        if adding_points[0]:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None and x > 0 and x < 10 and y > 0 and y < 10:
                point = ax.scatter(x, y, color='black', picker=5)  # Use scatter for points
                points.append((x, y))
                hull_point_objects.append(point)  # Store the scatter plot object
                plt.draw()
                
    def get_four_edges(hull_points, i, j):
        # Find neighbors in the hull for points i and j
        n_i_prev = hull_points[i - 1] if i > 0 else hull_points[-1]
        n_i_next = hull_points[i + 1] if i < len(hull_points) - 1 else hull_points[0]
        n_j_prev = hull_points[j - 1] if j > 0 else hull_points[-1]
        n_j_next = hull_points[j + 1] if j < len(hull_points) - 1 else hull_points[0]

        # Define the edges
        edges = [
            (points[n_i_prev], points[hull_points[i]]),  # Edge from A to its previous neighbor
            (points[hull_points[i]], points[n_i_next]),  # Edge from A to its next neighbor
            (points[n_j_prev], points[hull_points[j]]),  # Edge from B to its previous neighbor
            (points[hull_points[j]], points[n_j_next]),  # Edge from B to its next neighbor
        ]

        return edges
    
    def plot_and_sleep(edge, point1, point2, sleep_time=0.5):
        # x_values = [edge[0][0], edge[1][0]]
        # y_values = [edge[0][1], edge[1][1]]

        slope = (edge[0][1] - edge[1][1]) / (edge[0][0] - edge[1][0])
        if (edge[0][0] == point1[0] and edge[0][1] == point1[1] and edge[1][0] == point2[0] and edge[1][1] == point2[1]):
            return
        if (edge[0][0] == point2[0] and edge[0][1] == point2[1] and edge[1][0] == point1[0] and edge[1][1] == point1[1]):
            return
        
        x_for_P1 = np.linspace(point1[0] - 1, point1[0] + 1, 50)
        x_for_P2 = np.linspace(point2[0] - 1, point2[0] + 1, 50)
        y_for_P1 = slope * (x_for_P1 - point1[0]) + point1[1]
        y_for_P2 = slope * (x_for_P2 - point2[0]) + point2[1]
        line1, = ax.plot(x_for_P1, y_for_P1)
        line2, = ax.plot(x_for_P2, y_for_P2)
        plt.draw()
        plt.pause(sleep_time)
        time.sleep(sleep_time)
        line1.remove()
        line2.remove()
        plt.pause(0.01)
        
    def get_antipodal(antipodal_points, edges, point1, point2):
        good = False
        
        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]

        e1 = np.array([x2 - x1, y2 - y1])
        e2 = np.array([x1 - x2, y1 - y2])
        
        edge_vector1 = np.array([edges[0][1][0] - edges[0][0][0], edges[0][1][1] - edges[0][0][1]])
        edge_vector2 = np.array([edges[1][1][0] - edges[1][0][0], edges[1][1][1] - edges[1][0][1]])
        edge_vector3 = np.array([edges[2][1][0] - edges[2][0][0], edges[2][1][1] - edges[2][0][1]])
        edge_vector4 = np.array([edges[3][1][0] - edges[3][0][0], edges[3][1][1] - edges[3][0][1]])
        
        if np.sign(np.cross(edge_vector1, edge_vector3)) != np.sign(np.cross(edge_vector1, edge_vector4)):
            good = True
        if (edge_vector1 == e1).all() or (edge_vector1 == e2).all():
            good = False
        if good:
            antipodal_points.append(point2)
            return
            
        if np.sign(np.cross(edge_vector2, edge_vector3)) != np.sign(np.cross(edge_vector2, edge_vector4)):
            good = True
        if (edge_vector2 == e1).all() or (edge_vector2 == e2).all():
            good = False
        if good:
            antipodal_points.append(point2)
            return
            
        if np.sign(np.cross(edge_vector3, edge_vector1)) != np.sign(np.cross(edge_vector3, edge_vector2)):
            good = True
        if (edge_vector3 == e1).all() or (edge_vector3 == e2).all():
            good = False
        if good:
            antipodal_points.append(point2)
            return
            
        if np.sign(np.cross(edge_vector4, edge_vector1)) != np.sign(np.cross(edge_vector4, edge_vector2)):
            good = True
        if (edge_vector4 == e1).all() or (edge_vector4 == e2).all():
            good = False
        if good:
            antipodal_points.append(point2)
            return

    def compare_hull_points(hull_points):
        for i in range(len(hull_points)):
            antipodal_points = []
            for j in range(len(hull_points)):
                if i == j:
                    continue
                if adding_points[0]:  # Stop if checkbox is rechecked
                    return
                # print(points[hull_points[i]], " comparing with ", points[hull_points[j]])
                # Placeholder for comparing hull_points[i] and hull_points[j]
                edges = get_four_edges(hull_points, i, j)
                for edge in edges:
                    plot_and_sleep(edge, points[hull_points[i]], points[hull_points[j]])
                
                get_antipodal(antipodal_points, edges, points[hull_points[i]], points[hull_points[j]])
                time.sleep(0.5)
            # print(points[hull_points[i]], antipodal_points)
            map_of_antipodal_points[points[hull_points[i]]] = antipodal_points
        print("Done finding antipodal points!")

    def func(label):
        adding_points[0] = not adding_points[0]
        if not adding_points[0]:
            # Clear the previous convex hull plot
            ax.clear()
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            # Replot all points
            x, y = zip(*points)
            ax.plot(x, y, 'ko')
            map_of_antipodal_points.clear()
            # Plot the convex hull
            hull_points = plot_convex_hull(np.array(points))
            plt.draw()
            fig.canvas.flush_events()
            plt.pause(1)
            compare_hull_points(hull_points)
            
    def onpick(event):
        if isinstance(event.artist, PathCollection):
            ind = event.ind
            point = event.artist.get_offsets()[ind][0]
            point = tuple(point)
            if point in map_of_antipodal_points:
                print("The antipodal points of ", point, " is/are ", map_of_antipodal_points[point])
            print()

    check_ax = plt.axes([0.8, 0.89, 0.18, 0.1])  # Adjust as needed
    check_button = CheckButtons(check_ax, ['Add Points'], [True])
    check_button.on_clicked(func)

    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

    return 0

main()

