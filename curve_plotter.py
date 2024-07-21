import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, simpledialog
import mplcursors
from scipy.optimize import curve_fit

# Create initial data
data = {
    'x': np.random.rand(10),
    'y': np.random.rand(10)
}
df = pd.DataFrame(data)

# functions for interpolation


def quadratic_function(x, a, b, c):
    return a * x**2 + b * x + c


class InteractivePlot:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.selected_points = []
        self.new_points = pd.DataFrame(columns=['x', 'y'])
        self.fit_curve_line = None
        self.extrapolate_curve_line = None
        self.edit_mode = False
        self.rect = None
        self.start_x = None
        self.start_y = None
        # メインフレームの作成
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # キャンバスフレームの作成
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # ボタンフレームの作成
        self.button_frame = tk.Frame(main_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.fig, self.ax = plt.subplots(figsize=(1, 1))
        self.sc = self.ax.scatter(self.df['x'], self.df['y'], picker=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.create_initial_buttons()

        self.delete_mode = False
        self.add_point_mode = False
        self.select_mode = False

        self.canvas.mpl_connect("pick_event", self.on_pick)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)

        self.update_plot()

    def create_initial_buttons(self):
        self.clear_buttons()

        self.file_entry = tk.Entry(self.button_frame)
        self.file_entry.pack(side=tk.LEFT)

        self.load_button = tk.Button(
            self.button_frame, text="Load Data", command=self.load_data)
        self.load_button.pack(side=tk.LEFT)

        self.fit_button = tk.Button(
            self.button_frame, text="Fit Curve", command=self.fit_curve)
        self.fit_button.pack(side=tk.LEFT)

        self.add_point_button = tk.Button(
            self.button_frame, text="Add Point Mode", command=self.activate_add_point_mode)
        self.add_point_button.pack(side=tk.LEFT)

        self.delete_point_button = tk.Button(
            self.button_frame, text="Activate Delete Mode", command=self.activate_delete_mode)
        self.delete_point_button.pack(side=tk.LEFT)

        self.deactivate_delete_button = tk.Button(
            self.button_frame, text="Deactivate Delete Mode", command=self.deactivate_delete_mode)
        self.deactivate_delete_button.pack(side=tk.LEFT)

        self.edit_point_button = tk.Button(
            self.button_frame, text="EditPoint", command=self.activate_edit_mode)
        self.edit_point_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(
            self.button_frame, text="Save to Excel", command=self.save_to_excel)
        self.save_button.pack(side=tk.LEFT)

    def load_data(self):
        file_path = self.file_entry.get()
        if file_path:
            self.df = pd.read_excel(file_path)
            self.update_plot()

    def on_pick(self, event):
        if self.select_mode:
            ind = event.ind[0]
            if ind in self.selected_points:
                self.selected_points.remove(ind)

            else:
                self.selected_points.append(ind)

            self.update_plot()

        elif self.delete_mode:
            ind = event.ind[0]
            self.df = self.df.drop(ind).reset_index(drop=True)
            self.update_plot()

        elif self.edit_mode:
            ind = event.ind[0]
            self.edit_point(ind)

    def on_press(self, event):
        if (self.select_mode or self.delete_mode) and event.inaxes == self.ax:
            self.start_x = event.xdata
            self.start_y = event.ydata
            if self.rect is None:
                self.rect = plt.Rectangle((self.start_x, self.start_y), 0, 0, fill=False, color='black', linestyle='dashed')
                self.ax.add_patch(self.rect)

    def on_motion(self, event):
        if (self.select_mode or self.delete_mode) and self.rect is not None and event.inaxes == self.ax:
            cur_x, cur_y = event.xdata, event.ydata
            width = cur_x - self.start_x
            height = cur_y - self.start_y
            self.rect.set_width(width)
            self.rect.set_height(height)
            self.rect.set_xy((self.start_x, self.start_y))
            self.canvas.draw()

    def on_release(self, event):
        if self.select_mode and self.rect is not None:
            selected_points = []
            for i, (x, y) in enumerate(zip(self.df['x'], self.df['y'])):
                if (self.start_x <= x <= event.xdata or self.start_x >= x >= event.xdata) and \
                (self.start_y <= y <= event.ydata or self.start_y >= y >= event.ydata):
                    selected_points.append(i)

            set_select_points_db = set(self.selected_points)
            set_new_select_points = set(selected_points)
            self.selected_points = list(set_select_points_db.union(set_new_select_points))

            self.rect.remove()
            self.rect = None
            self.update_plot()

        elif self.delete_mode and self.rect is not None:
            selected_points = []
            for i, (x, y) in enumerate(zip(self.df['x'], self.df['y'])):
                if (self.start_x <= x <= event.xdata or self.start_x >= x >= event.xdata) and \
                (self.start_y <= y <= event.ydata or self.start_y >= y >= event.ydata):
                    selected_points.append(i)

            if len(selected_points) > 0:
                selected_points.reverse()
                for ind in selected_points:
                    self.df = self.df.drop(ind).reset_index(drop=True)

            self.rect.remove()
            self.rect = None
            self.update_plot()

    def update_plot(self):
        self.ax.clear()
        colors = [
            'red' if i in self.selected_points else 'blue' for i in range(len(self.df))]
        self.sc = self.ax.scatter(
            self.df['x'], self.df['y'], c=colors, picker=True)
        if not self.new_points.empty:
            self.ax.scatter(self.new_points['x'],
                            self.new_points['y'], color='green')
        if self.fit_curve_line is not None:
            self.ax.plot(
                self.fit_curve_line[0], self.fit_curve_line[1], color='purple')

        if self.extrapolate_curve_line is not None:
            self.ax.plot(
                self.extrapolate_curve_line[0], self.extrapolate_curve_line[1], color='green')

        if not self.new_points.empty:
            min_x = min(min(self.df["x"]), min(self.new_points["x"]))
            max_x = max(max(self.df["x"]), max(self.new_points["x"]))

            min_y = min(min(self.df["y"]), min(self.new_points["y"]))
            max_y = max(max(self.df["y"]), max(self.new_points["y"]))
        else:
            min_x = min(self.df["x"])
            max_x = max(self.df["x"])

            min_y = min(self.df["y"])
            max_y = max(self.df["y"])

        # Align axis limitations
        fig_white_room_x = (max_x - min_x)*0.1
        fig_white_room_y = (max_y - min_y)*0.1
        self.ax.set_xlim(min_x - fig_white_room_x,
                         max_x + fig_white_room_x)
        self.ax.set_ylim(min_y - fig_white_room_y,
                         max_y + fig_white_room_y)

        self.canvas.draw()

    def fit_curve(self):
        self.clear_buttons()

        self.select_plots_button = tk.Button(
            self.button_frame, text="SelectPlots", command=self.activate_select_mode)
        self.select_plots_button.pack(side=tk.LEFT)

        self.fit_curve_button = tk.Button(
            self.button_frame, text="FitCurve", command=self.perform_fit)
        self.fit_curve_button.pack(side=tk.LEFT)

        self.extrapolate_button = tk.Button(
            self.button_frame, text="Extrapolate", command=self.extrapolate_points)
        self.extrapolate_button.pack(side=tk.LEFT)

        self.store_plots_button = tk.Button(
            self.button_frame, text="StorePlots", command=self.store_new_points)
        self.store_plots_button.pack(side=tk.LEFT)

        self.exit_button = tk.Button(
            self.button_frame, text="Exit w/o Save", command=self.exit_without_save)
        self.exit_button.pack(side=tk.LEFT)

        self.activate_select_mode()

    def perform_fit(self):
        if self.selected_points is not None and len(self.selected_points) > 2:
            selected_df = self.df.iloc[self.selected_points].sort_values(
                by='x')
            x = selected_df['x']
            y = selected_df['y']
            popt, _ = curve_fit(quadratic_function, x, y)
            self.a, self.b, self.c = popt

            # optimize curve using selected points
            x_fit = np.linspace(min(x), max(x), 100)
            y_fit = quadratic_function(x_fit, self.a, self.b, self.c)
            self.fit_curve_line = (x_fit, y_fit)

            # calculate mid-points
            x_midpoints = np.array(
                [(x.iloc[i] + x.iloc[i + 1]) / 2 for i in range(len(x) - 1)])
            y_midpoints = quadratic_function(x_midpoints, self.a, self.b, self.c)

            new_points_df = pd.DataFrame({'x': x_midpoints, 'y': y_midpoints})

            self.new_points = new_points_df
            self.update_plot()
        else:
            # Plase select more than 3 points
            pass

    def extrapolate_points_in_range(self, x_range, extrapolate_by):
        num_exterpolate_points = (x_range[1] - x_range[0]) // extrapolate_by

        x_new  = np.concatenate([np.linspace(x_range[0], x_range[0] + extrapolate_by * int(num_exterpolate_points), int(num_exterpolate_points)+1), np.array([x_range[1]])])
        y_new = quadratic_function(x_new, self.a, self.b, self.c)

        self.extrapolate_curve_line = (x_new, y_new)

        return pd.DataFrame({'x': x_new, 'y': y_new})

    def extrapolate_points(self):
        # temp
        extrapolate_from = simpledialog.askfloat("extrapolate_from", f"\nEnter extrapolate from:", parent=self.root)
        extrapolate_until  = simpledialog.askfloat("extrapolate_until", f"\nEnter extrapolate_until:", parent=self.root)
        extrapolate_by = simpledialog.askfloat("extrapolate_by", f"\nEnter extrapolate_by:", parent=self.root)

        exterpolated_df = self.extrapolate_points_in_range([extrapolate_from, extrapolate_until], extrapolate_by)

        self.new_points = exterpolated_df
        self.update_plot()


    def store_new_points(self):
        if not self.new_points.empty:
            self.df = pd.concat([self.df, self.new_points], ignore_index=True)
            self.new_points = pd.DataFrame(columns=['x', 'y'])
            self.fit_curve_line = None
            self.extrapolate_curve_line = None

            self.select_mode = False
            self.selected_points = []

            self.update_plot()
            self.create_initial_buttons()

    def exit_without_save(self):
        self.new_points = pd.DataFrame(columns=['x', 'y'])
        self.fit_curve_line = None
        self.extrapolate_curve_line = None

        self.select_mode = False
        self.selected_points = []

        self.update_plot()

        self.create_initial_buttons()

    def save_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            sorted_df = self.df.sort_values(by='x')
            sorted_df.to_excel(file_path, index=False)
            print(f"Data saved to {file_path}")

    def edit_point(self, ind):
        x_old, y_old = self.df.loc[ind, ['x', 'y']]
        x_new = simpledialog.askfloat("Edit x", f"Current x: {
                                      x_old}\nEnter new x:", parent=self.root, initialvalue=x_old)
        y_new = simpledialog.askfloat("Edit y", f"Current y: {
                                      y_old}\nEnter new y:", parent=self.root, initialvalue=y_old)
        if x_new is not None and y_new is not None:
            self.df.at[ind, 'x'] = x_new
            self.df.at[ind, 'y'] = y_new
            self.update_plot()
        self.edit_mode = False

    def activate_add_point_mode(self):
        self.add_point_mode = True
        self.delete_mode = False
        self.select_mode = False

    def activate_delete_mode(self):
        self.delete_mode = True
        self.add_point_mode = False
        self.select_mode = False

    def deactivate_delete_mode(self):
        self.delete_mode = False

    def activate_edit_mode(self):
        self.edit_mode = True
        self.select_mode = False
        self.add_point_mode = False
        self.delete_mode = False

    def activate_select_mode(self):
        self.select_mode = True
        self.delete_mode = False
        self.add_point_mode = False
        self.selected_points = []
        self.update_plot()

    def on_canvas_click(self, event):
        if self.add_point_mode and event.inaxes == self.ax:
            new_point = pd.DataFrame({'x': [event.xdata], 'y': [event.ydata]})
            self.df = pd.concat([self.df, new_point], ignore_index=True)
            self.update_plot()

    def clear_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()


root = tk.Tk()
window_height = 600
window_width = 800
root.geometry(str(window_width) + "x" + str(window_height))
app = InteractivePlot(root, df)
root.mainloop()
