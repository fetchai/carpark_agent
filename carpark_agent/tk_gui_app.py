import os

# Need to do this when remote debugging from pycharm (for some reason)
os.environ["DISPLAY"] = ":0.0"
import skimage
import cv2
import PIL.Image
import PIL.ImageTk
import time
import numpy as np

# Us Tkinter to make a gui
from tkinter import *
from tkinter import ttk
from car_detection.circular_list import CircularList


uistate_live_detect = 0
uistate_edit_detection_area = 1

editstate_draw_detected = 0
editstate_draw_nondetected = 1

drawstate_draw_line = 0
drawstate_flood_fill = 1

class TkGuiApp:

    def __init__(
            self,
            window_title,
            image_source,
            database,
            screen_width_frac=0.9,
            num_history=4,
            max_num_undos=5):

        # Configuration parameters
        self.image_source = image_source
        self.num_history = num_history
        self.screen_width_frac = screen_width_frac
        self.db = database
        self.max_num_undos = max_num_undos

        # Main window appearance
        self.bg_live_col = "#1c1c2c"
        self.bg_edit_col = "#204020"
        self.bg_use_col = "pink"
        self.tk_root = Tk()
        self.screen_width = self.tk_root.winfo_screenwidth()
        self.screen_height = self.tk_root.winfo_screenheight()
        self.tk_root.configure(background=self.bg_use_col)
        self.tk_root.title(window_title)


        # temporary images
        self.ui_coloured_mask = None
        self.mask_ref_image = None
        self.load_masks()
        self.adjusted_image = np.zeros((self.image_source.cam_height, self.image_source.cam_width, 3), np.uint8)
        self.show_main_image = np.zeros((self.image_source.cam_height, self.image_source.cam_width, 3), np.uint8)

        # We scale the app to an appropriate size on screen such that it is 75% of the screen width
        unscaled_live_feed_width = image_source.cam_width
        unscaled_small_image_width = unscaled_live_feed_width / self.num_history
        unscaled_border_width = 4
        num_little_fames_on_row = 3     # so we know how many borders we have to consider
        num_little_widths_on_row = 4    # one of the frames is double width
        unscaled_total_width = \
            unscaled_live_feed_width + \
            unscaled_small_image_width * num_little_widths_on_row + \
            2 * unscaled_border_width * (1 + num_little_fames_on_row)

        self.scale_factor = self.screen_width_frac * self.screen_width / unscaled_total_width
        self.scaled_total_width = unscaled_total_width * self.scale_factor

        # calculate sizes of frames we will need
        image_width = int(image_source.cam_width)
        image_height = int(image_source.cam_height)
        self.main_canvas_width = int(image_width * self.scale_factor)
        self.main_canvas_height = int(image_height * self.scale_factor)
        self.small_width = int(self.main_canvas_width / self.num_history)
        self.small_height = int(self.main_canvas_height / self.num_history)
        self.medium_height = int(1.5 * self.small_height)
        self.border_width = unscaled_border_width * self.scale_factor
        num_text_lines_in_frame = 6
        line_spacing_fudge = 1.3
        self.use_font_size = -int(self.small_height / (num_text_lines_in_frame * line_spacing_fudge))
        self.use_small_font_size = int(2 * self.use_font_size / 3)


        # Set up styles for buttons (as they don't change colour on osx in normal mode!)
        # background="..." doesn't work even using this method
        self.button_style = ttk.Style()
        self.button_style.map(
            'C.TButton',
            foreground=[('disabled', 'grey50'), ('!disabled', 'black')],
        )
        self.detect_button_style = ttk.Style()
        self.detect_button_style.map(
            'D.TButton',
            foreground=[('disabled', 'grey50'), ('!disabled', 'blue')],
        )
        self.nondetect_button_style = ttk.Style()
        self.nondetect_button_style.map(
            'E.TButton',
            foreground=[('disabled', 'grey50'), ('!disabled', 'red')],
        )
        self.fill_button_style = ttk.Style()
        self.fill_button_style.map(
            'F.TButton',
            foreground=[('disabled', 'grey50'), ('!disabled', 'black')],
        )

        # Create three frames on top of each other to put various bits and bobs
        self.all_bordered_frames = []
        self.all_bordered_frames.append(self.tk_root)

        self.ui_frame = Frame(
            self.tk_root,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.ui_frame.grid(row=0, column=0)
        self.all_bordered_frames.append(self.ui_frame)

        self.image_frame = Frame(
            self.tk_root,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.image_frame.grid(row=1, column=0)
        self.all_bordered_frames.append(self.image_frame)

        self.feedback_frame = Frame(
            self.tk_root,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.feedback_frame.grid(row=2, column=0)
        self.all_bordered_frames.append(self.feedback_frame)

        # Buttons
        button_pos = 0
        self.quit_button = ttk.Button(
            self.ui_frame,
            text="Quit",
            style='C.TButton',
            command=self.on_exit)
        self.quit_button.grid(row=0, column=button_pos)
        button_pos += 1

        gaps_text = "   "
        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(gap)
        button_pos += 1

        self.live_detect_button = ttk.Button(
            self.ui_frame,
            text="Live Detect",
            style='C.TButton',
            command=self.on_live_detect)
        self.live_detect_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_detection_area_button = ttk.Button(
            self.ui_frame,
            text="Edit detection area",
            style='C.TButton',
            command=self.on_edit_detection_area)
        self.edit_detection_area_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_capture_ref_image_button = ttk.Button(
            self.ui_frame,
            text="Capture ref image",
            style='C.TButton',
            command=self.on_edit_capture_ref_image)
        self.edit_capture_ref_image_button.grid(row=0, column=button_pos)
        button_pos += 1

        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(gap)
        button_pos += 1

        self.edit_draw_detectable_button = ttk.Button(
            self.ui_frame,
            text="Draw detectable",
            style='D.TButton',
            command=self.on_draw_detectable)
        self.edit_draw_detectable_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_draw_undetectable_button = ttk.Button(
            self.ui_frame,
            text="Draw non-detectable",
            style='E.TButton',
            command=self.on_draw_nondetectable)
        self.edit_draw_undetectable_button.grid(row=0, column=button_pos)
        button_pos += 1

        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(gap)
        button_pos += 1

        self.edit_draw_line_button = ttk.Button(
            self.ui_frame,
            text="Draw line",
            style='F.TButton',
            command=self.on_edit_draw_line)
        self.edit_draw_line_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_flood_fill_button = ttk.Button(
            self.ui_frame,
            text="Flood fill",
            style='F.TButton',
            command=self.on_edit_flood_fill)
        self.edit_flood_fill_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_fill_all_button = ttk.Button(
            self.ui_frame,
            text="Fill all",
            style='F.TButton',
            command=self.on_edit_fill_all)
        self.edit_fill_all_button.grid(row=0, column=button_pos)
        button_pos += 1

        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(gap)
        button_pos += 1

        self.edit_undo_button = ttk.Button(
            self.ui_frame,
            text="Undo",
            style='C.TButton',
            command=self.on_edit_undo)
        self.edit_undo_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.edit_redo_button = ttk.Button(
            self.ui_frame,
            text="Redo",
            style='C.TButton',
            command=self.on_edit_redo)
        self.edit_redo_button.grid(row=0, column=button_pos)
        button_pos += 1

        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(gap)
        button_pos += 1

        self.edit_dec_max_capacity = ttk.Button(
            self.ui_frame,
            text="<",
            style='C.TButton',
            command=self.on_dec_capacity)
        self.edit_dec_max_capacity.grid(row=0, column=button_pos)
        button_pos += 1

        self.max_capacity_label = Label(
            self.ui_frame,
            borderwidth=self.border_width ,
            highlightthickness=0,
            background="black",
            foreground="gray",
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="Max capacity: 0")
        self.max_capacity_label.grid(row=0, column=button_pos)
        self.all_bordered_frames.append(self.max_capacity_label)
        button_pos += 1

        self.edit_inc_max_capacity = ttk.Button(
            self.ui_frame,
            text=">",
            style='C.TButton',
            command=self.on_inc_capacity)
        self.edit_inc_max_capacity.grid(row=0, column=button_pos)
        button_pos += 1

        # Create a canvas that can fit the video source
        self.live_feed_canvas = Canvas(
            self.image_frame,
            width=self.main_canvas_width,
            height=self.main_canvas_height,
            background=self.bg_use_col,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0)
        self.live_feed_canvas.grid(row=0, column=0)
        self.all_bordered_frames.append(self.live_feed_canvas)

        self.live_feed_label = Label(
                self.image_frame,
                borderwidth=self.border_width * self.num_history,
                highlightthickness=0,
                background="black",
                foreground="gray",
                justify=LEFT,
                font=("Arial", self.use_font_size),
                text="Live feed window")
        self.live_feed_label.grid(row=0, column=0, sticky="NW")
        self.all_bordered_frames.append(self.live_feed_label)

        # Parent frame of all the history
        self.history_frame = Frame(
            self.image_frame,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.history_frame.grid(row=0, column=1)
        self.all_bordered_frames.append(self.history_frame)

        # frames for each epoch
        self.raw_history_canvases = []
        self.raw_photos = []
        self.processed_history_canvases = []
        self.processed_photos = []
        self.stats_textboxes = []

        for i in range(0, self.num_history):
            raw_canvas = Canvas(
                self.history_frame,
                width=self.small_width,
                height=self.small_height,
                borderwidth=self.border_width,
                highlightbackground=self.bg_use_col,
                highlightthickness=0,
                background=self.bg_use_col)
            raw_canvas.grid(row=i, column=0, padx=0, pady=0)
            self.raw_history_canvases.append(raw_canvas)
            self.all_bordered_frames.append(raw_canvas)
            self.raw_photos.append(None)

            processed_canvas = Canvas(
                self.history_frame,
                width=self.small_width,
                height=self.small_height,
                borderwidth=self.border_width,
                highlightbackground=self.bg_use_col,
                highlightthickness=0,
                background=self.bg_use_col)
            processed_canvas.grid(row=i, column=1, padx=0, pady=0)
            self.processed_history_canvases.append(processed_canvas)
            self.all_bordered_frames.append(processed_canvas)

            # Need to make a frame around it in order to specify size in pixels
            text_frame = Frame(
                self.history_frame,
                width=2*self.small_width,
                height=self.small_height,
                borderwidth=self.border_width,
                highlightbackground=self.bg_use_col,
                highlightthickness=0,
                background=self.bg_use_col)
            text_frame.grid(row=i, column=2, padx=0, pady=0)
            self.all_bordered_frames.append(text_frame)
            text_frame.pack_propagate(0)

            stats_textbox = Label(
                text_frame,
                borderwidth=0,
                highlightthickness=0,
                background="black",
                foreground="gray",
                anchor=NW,
                justify=LEFT,
                font=("Arial", self.use_font_size),
                text="no data for window: " + str(i))
            stats_textbox.pack(expand=True, fill='both')
            self.stats_textboxes.append(stats_textbox)
            # Don't include this as it doesn't have a frame
            # self.all_frames.append(√)

        # Need to make a frame around it in order to specify size in pixels
        self.status_frame = Frame(
            self.feedback_frame,
            width=1*self.scaled_total_width/5,
            height=self.medium_height,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0,
            background=self.bg_use_col)
        self.status_frame.grid(row=0, column=0, padx=0, pady=0)
        self.all_bordered_frames.append(self.status_frame)
        self.status_frame.pack_propagate(0)

        self.status_text = Label(
            self.status_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[Status window]")
        self.status_text.pack(expand=True, fill='both')

        self.dialog_frame = Frame(
            self.feedback_frame,
            width=2*self.scaled_total_width/5,
            height=self.medium_height,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0,
            background=self.bg_use_col)
        self.dialog_frame.grid(row=0, column=1, padx=0, pady=0)
        self.all_bordered_frames.append(self.dialog_frame)
        self.dialog_frame.pack_propagate(0)


        self.dialog_time_text = Label(
            self.dialog_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[OEF Time]")
        self.dialog_time_text.pack(expand=True, fill='both', side=LEFT)


        self.dialog_agent_text = Label(
            self.dialog_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[OEF Agent]")
        self.dialog_agent_text.pack(expand=True, fill='both', side=LEFT)

        self.dialog_received_text = Label(
            self.dialog_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[OEF messages received]")
        self.dialog_received_text.pack(expand=True, fill='both', side=LEFT)

        self.dialog_sent_text = Label(
            self.dialog_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[OEF messages sent]")
        self.dialog_sent_text.pack(expand=True, fill='both', side=LEFT)

        self.transactions_frame = Frame(
            self.feedback_frame,
            width=2 * self.scaled_total_width / 5,
            height=self.medium_height,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0,
            background=self.bg_use_col)
        self.transactions_frame.grid(row=0, column=2, padx=0, pady=0)
        self.all_bordered_frames.append(self.transactions_frame)
        self.transactions_frame.pack_propagate(0)

        self.transactions_text = Label(
            self.transactions_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="[Transactions window]")
        self.transactions_text.pack(expand=True, fill='both')

        # UI stuff
        self.enable_capture = True
        self.uistate = uistate_live_detect
        self.editstate = editstate_draw_nondetected
        self.drawstate = drawstate_draw_line
        self.last_over_frame = None
        self.roi_edit_pen_size = 10
        self.last_draw_pos = None
        self.draw_radius = 5
        self.undo_index = 0
        self.undo_list = CircularList(self.max_num_undos)
        self.undo_list.append(self.ui_coloured_mask.copy())
        self.was_drawing = False
        self.setup_ui_state()

        # Handle Events
        self.tk_root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.tk_root.bind('<Button-1>', self.mouse_down)
        self.tk_root.bind('<ButtonRelease-1>', self.mouse_up)
        self.is_mouse_pressed = False

        # Make the top-most window
        self.tk_root.lift()
        self.tk_root.attributes("-topmost", 1)
        self.tk_root.attributes("-topmost", 0)

        # mostly for debugging
        self.frame_count = 0

        # Start the window and update loop and
        self.live_update_wait_ms = 16
        self.history_update_wait_ms = 200
        self.prev_history_epoch = 0
        self.update_live_feed()
        self.update_history()
        self.tk_root.mainloop()

    def setup_ui_state(self):

        if self.uistate == uistate_live_detect:
            self.live_detect_button.state(["disabled"])
            self.edit_detection_area_button.state(["!disabled"])
            self.edit_capture_ref_image_button.state(["disabled"])
            self.edit_draw_detectable_button.state(["disabled"])
            self.edit_draw_undetectable_button.state(["disabled"])
            self.edit_draw_line_button.state(["disabled"])
            self.edit_flood_fill_button.state(["disabled"])
            self.edit_fill_all_button.state(["disabled"])
            self.edit_undo_button.state(["disabled"])
            self.edit_redo_button.state(["disabled"])
            self.edit_dec_max_capacity.state(["disabled"])
            self.edit_inc_max_capacity.state(["disabled"])

            self.enable_capture = True
            self.bg_use_col = self.bg_live_col
            self.live_feed_label.lift(self.live_feed_canvas)

            self.detect_button_style = ttk.Style()
            self.detect_button_style.map(
                'D.TButton',
                foreground=[('disabled', 'grey50'), ('!disabled', 'blue')],
            )
            self.nondetect_button_style = ttk.Style()
            self.nondetect_button_style.map(
                'E.TButton',
                foreground=[('disabled', 'grey50'), ('!disabled', 'red')],
            )
            self.fill_button_style = ttk.Style()
            self.fill_button_style.map(
                'F.TButton',
                foreground=[('disabled', 'grey50'), ('!disabled', 'black')],
            )


        if self.uistate == uistate_edit_detection_area:
            self.live_detect_button.state(["!disabled"])
            self.edit_detection_area_button.state(["disabled"])
            self.edit_capture_ref_image_button.state(["!disabled"])

            self.edit_fill_all_button.state(["!disabled"])

            self.enable_capture = False
            self.bg_use_col = self.bg_edit_col
            self.live_feed_label.lower(self.live_feed_canvas)

            self.detect_button_style = ttk.Style()
            self.detect_button_style.map(
                'D.TButton',
                foreground=[('disabled', 'light blue'), ('!disabled', 'blue')],
            )
            self.nondetect_button_style = ttk.Style()
            self.nondetect_button_style.map(
                'E.TButton',
                foreground=[('disabled', 'pink'), ('!disabled', 'red')],
            )
            max_cap = self.db.get_max_capacity()
            if max_cap is not None and max_cap > 0:
                self.edit_dec_max_capacity.state(["!disabled"])
            else:
                self.edit_dec_max_capacity.state(["disabled"])
            if max_cap is not None:
                self.edit_inc_max_capacity.state(["!disabled"])
            else:
                self.edit_inc_max_capacity.state(["disabled"])

            if self.editstate == editstate_draw_detected:
                self.edit_draw_detectable_button.state(["disabled"])
                self.edit_draw_undetectable_button.state(["!disabled"])
                self.fill_button_style = ttk.Style()
                self.fill_button_style.map(
                    'F.TButton',
                    foreground=[('disabled', 'light blue'), ('!disabled', 'blue')],
                )

            if self.editstate == editstate_draw_nondetected:
                self.edit_draw_detectable_button.state(["!disabled"])
                self.edit_draw_undetectable_button.state(["disabled"])
                self.fill_button_style = ttk.Style()
                self.fill_button_style.map(
                    'F.TButton',
                    foreground=[('disabled', 'pink'), ('!disabled', 'red')],
                )

            if self.drawstate == drawstate_draw_line:
                self.edit_draw_line_button.state(["disabled"])
                self.edit_flood_fill_button.state(["!disabled"])

            if self.drawstate == drawstate_flood_fill:
                self.edit_draw_line_button.state(["!disabled"])
                self.edit_flood_fill_button.state(["disabled"])

            if self.undo_index == 0:
                self.edit_redo_button.state(["disabled"])
            else:
                self.edit_redo_button.state(["!disabled"])

            if not self.undo_list.has_past_item(self.undo_index + 1):
                self.edit_undo_button.state(["disabled"])
            else:
                self.edit_undo_button.state(["!disabled"])

        for frame in self.all_bordered_frames:
            frame.config(bg=self.bg_use_col)

    def on_live_detect(self):
        self.uistate = uistate_live_detect
        self.setup_ui_state()

    def on_draw_detectable(self):
        self.editstate = editstate_draw_detected
        self.setup_ui_state()

    def on_draw_nondetectable(self):
        self.editstate = editstate_draw_nondetected
        self.setup_ui_state()

    def on_edit_detection_area(self):
        self.uistate = uistate_edit_detection_area
        self.load_masks()
        self.setup_ui_state()

    def on_edit_draw_line(self):
        self.drawstate = drawstate_draw_line
        self.setup_ui_state()

    def on_edit_flood_fill(self):
        self.drawstate = drawstate_flood_fill
        self.setup_ui_state()

    def on_edit_fill_all(self):
        self.ui_coloured_mask[:, :] = self.get_edit_draw_col()
        self.record_undo()
        self.setup_ui_state()

    def on_edit_undo(self):
        self.undo_index += 1
        self.ui_coloured_mask = self.undo_list.get_past_item(self.undo_index).copy()
        self.save_masks()
        self.setup_ui_state()

    def on_edit_redo(self):
        self.undo_index -= 1
        self.ui_coloured_mask = self.undo_list.get_past_item(self.undo_index).copy()
        self.save_masks()
        self.setup_ui_state()

    def on_dec_capacity(self):
        max_cap = self.db.get_max_capacity()
        if max_cap is not None and max_cap > 0:
            self.db.save_max_capacity(max_cap - 1)
        self.setup_ui_state()

    def on_inc_capacity(self):
        max_cap = self.db.get_max_capacity()
        if max_cap is not None:
            self.db.save_max_capacity(max_cap + 1)
        self.setup_ui_state()

    def on_edit_capture_ref_image(self):
        self.mask_ref_image = self.image_source.get_latest_video_image()
        self.save_masks()
        self.setup_ui_state()

    def record_undo(self):
        self.undo_list.roll_back(self.undo_index)
        self.undo_list.append(self.ui_coloured_mask.copy())
        self.undo_index = 0
        self.save_masks()

    def mouse_down(self, event):
        self.is_mouse_pressed = True

    def mouse_up(self, event):
        self.is_mouse_pressed = False


    def get_widget_under(self):
        x, y = self.tk_root.winfo_pointerxy()
        return self.tk_root.winfo_containing(x, y)

    def on_exit(self):
        self.tk_root.destroy()

    def resize_frame_keep_aspect(self, frame, dims):
        src_height, src_width, src_channels = frame.shape
        if dims[0] == src_width and dims[1] == src_height:
            print("no need to resize image")
            return frame

        x_scale = dims[0] / src_width
        y_scale = dims[1] / src_height

        # whichever is scaled the least - use this as scaling factor
        use_scale = x_scale if x_scale < y_scale else y_scale
        use_width = int(src_width * use_scale)
        use_height = int(src_height * use_scale)
        return cv2.resize(frame, (use_width, use_height))

    def screen_to_image_transform(self, screen_pos, frame, image):
        image_height, image_width, image_depth = image.shape
        xpos = (image_width * (screen_pos[0] - frame.winfo_rootx())) / frame.winfo_width()
        ypos = (image_height * (screen_pos[1] - frame.winfo_rooty())) / frame.winfo_height()
        return int(xpos), int(ypos)


    def get_edit_draw_col(self):
        return (0, 0, 255) if self.editstate == editstate_draw_detected else (255, 0, 0)

    def handle_mask_edit(self):
        over_frame = self.get_widget_under()
        do_pen_up = False
        new_draw_pos = self.screen_to_image_transform(
            self.tk_root.winfo_pointerxy(),
            self.live_feed_canvas,
            self.ui_coloured_mask)

        is_drawing = False
        if self.is_mouse_pressed:
            if self.point_is_inside(new_draw_pos, self.ui_coloured_mask) or self.was_drawing:
                is_drawing = True

            col = self.get_edit_draw_col()
            if self.drawstate == drawstate_draw_line:
                if self.last_draw_pos is not None:
                    cv2.line(self.ui_coloured_mask, self.last_draw_pos, new_draw_pos, col, self.draw_radius)
                self.last_draw_pos = new_draw_pos
            else:
                if self.point_is_inside(new_draw_pos, self.ui_coloured_mask):
                    cv2.floodFill(self.ui_coloured_mask, None, new_draw_pos, col)

        else:
            self.last_draw_pos = None

        if self.was_drawing and not is_drawing:
            self.record_undo()
            self.setup_ui_state()

        self.was_drawing = is_drawing

    def point_is_inside(self, pos, image):
        image_height, image_width, image_depth = image.shape
        return pos[0] >=0 and pos[0] < image_width and pos[1] >= 0 and pos[1] < image_height


    def update_live_feed(self):
        #print("{}: Update_live_feed".format(self.frame_count))
        #self.frame_count += 1

        if self.uistate == uistate_edit_detection_area:
            self.handle_mask_edit()


        # Check if the mouse is over any of our images
        override_image = None
        if self.last_over_frame is not None:
            self.last_over_frame.config(bg=self.bg_use_col)

        over_frame = self.get_widget_under()
        self.last_over_frame = over_frame if hasattr(over_frame, 'original_image') else None

        if self.last_over_frame is not None and hasattr(self.last_over_frame, 'original_image'):
            if self.is_mouse_pressed:
                self.last_over_frame.config(bg="RoyalBlue2")
            else:
                self.last_over_frame.config(bg="RoyalBlue4")


        if self.is_mouse_pressed and self.last_over_frame is not None and hasattr(self.last_over_frame, 'original_image'):
            override_image = self.last_over_frame.original_image

        if override_image is None:
            if self.uistate == uistate_live_detect:
                frame = self.image_source.get_latest_video_image()
            else:
                frame = self.mask_ref_image
        else:
            frame = override_image

        if frame is not None:
            show_frame = self.process_main_image(frame)
            if self.scale_factor != 1:
                show_frame = self.resize_frame_keep_aspect(show_frame, (self.main_canvas_width, self.main_canvas_height))
            self.live_feed_canvas.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(show_frame))
            self.live_feed_canvas.create_image(
                self.main_canvas_width / 2,
                self.main_canvas_height / 2,
                image=self.live_feed_canvas.photo,
                anchor=CENTER)

        self.live_feed_label.config(text="Current FET: " + self.sdk_fet_to_human_fet(self.db.calc_uncleared_fet()))
        self.max_capacity_label["text"] = "Max capacity: {}".format(self.db.get_max_capacity())

        self.tk_root.after(self.live_update_wait_ms, self.update_live_feed)

    # convert fet as used by the SDK into actual fet (not nano-pico fet - or whatever) and display as
    # a human readable string.
    def sdk_fet_to_human_fet(self, fet):
        return " {0:.10f}".format(fet * 0.0000000001)


    def update_history(self):
        # Udate dialog lists
        results = self.db.get_dialogue_statuses()
        time_text = "Time:\n"
        agent_text = "Other agent:\n"
        received_text = "Received messages:\n"
        sent_text = "Sent messages:\n"
        for result in results:
            whole_sec, frac_sec = divmod(result["epoch"], 1)
            time_text += time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(whole_sec)) + "." + str(frac_sec)[2:5] + "\n"
            agent_text += self.lookup_friendly_name(result['other_agent_key']) + "\n"
            received_text += result['received_msg'] + "\n"
            sent_text += result['sent_msg'] + "\n"

        self.dialog_time_text['text'] = time_text
        self.dialog_agent_text['text'] = agent_text
        self.dialog_received_text['text'] = received_text
        self.dialog_sent_text['text'] = sent_text

        # Update transaction lists
        incomplete_tx_text = "Ledger transactions:\n"
        in_progress_transations = self.db.get_n_transactions(20)
        for transaction in in_progress_transations:
            incomplete_tx_text += "{}: Transaction_id: {} of {} fet from {} to {} : status is {}\n".format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(transaction["epoch"])),
                transaction['tx_hash'][:4] + "...",
                transaction['amount'],
                self.lookup_friendly_name(transaction['oef_key_payer']),
                self.lookup_friendly_name(transaction['oef_key_payee']),
                transaction['status'])

        self.transactions_text["text"] = incomplete_tx_text

        cleared_fet = self.sdk_fet_to_human_fet(self.db.get_fet())
        uncleared_fet = self.sdk_fet_to_human_fet(self.db.calc_uncleared_fet())

        public_key, friendly_name = self.db.lookup_self_names()
        status_str = "System status:\n"
        status_str += "OEF public key: {}\n".format(public_key)
        status_str += "Friendly name: {}\n".format(friendly_name)
        status_str += "Uncleared FET: {}\n".format(uncleared_fet)
        status_str += "Cleared FET: {}\n".format(cleared_fet)
        status_str += "Ledger status: {}:{}: {}\n".format(
            self.db.get_system_status("ledger-ip"),
            self.db.get_system_status("ledger-port"),
            self.db.get_system_status("ledger-status"))
        status_str += "OEF status: {}:{}: {}\n".format(
            self.db.get_system_status("oef-ip"),
            self.db.get_system_status("oef-port"),
            self.db.get_system_status("oef-status"))
        status_str += "GPS source: {}\n".format(self.db.get_system_status("gps_source"))
        status_str += "GPS Location: {}\n".format(self.db.get_lat_lon())

        self.status_text["text"] = status_str

        data_list = self.db.get_latest_detection_data(self.num_history)
        this_epoch = data_list[0]["epoch"] if len(data_list) > 0 else 0

        if this_epoch != self.prev_history_epoch:
            self.prev_history_epoch = this_epoch

            print("Debug: Update history")
            for i in range(0, self.num_history):
                if i < len(data_list):
                    data = data_list[i]
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["epoch"]))
                    self.stats_textboxes[i]["text"] \
                        = "timestamp: {}\n" \
                          "vehicle count: {}\n" \
                          "moving count: {}\n" \
                          "free-space count: {}\n" \
                          "latitude: {}\n" \
                          "longitude: {}".format(
                            time_str,
                            data["total_count"],
                            data["moving_count"],
                            data["free_spaces"],
                            data["lat"],
                            data["lon"])

                    # Load images
                    if os.path.isfile(data["raw_image_path"]):
                        raw_image = skimage.io.imread(data["raw_image_path"])
                    else:
                        raw_image = None

                    if os.path.isfile(data["processed_image_path"]):
                        processed_image = skimage.io.imread(data["processed_image_path"])
                    else:
                        processed_image = None


                    if raw_image is not None:

                        raw_image_small = self.resize_frame_keep_aspect(raw_image, (self.small_width, self.small_height))
                        self.raw_history_canvases[i].original_image = raw_image
                        self.raw_history_canvases[i].photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(raw_image_small))
                        self.raw_history_canvases[i].create_image(
                            self.small_width / 2,
                            self.small_height / 2,
                            image=self.raw_history_canvases[i].photo,
                            anchor=CENTER)
                    else:
                        self.raw_history_canvases[i].delete("all")
                        self.raw_history_canvases[i].original_image = None
                        self.raw_history_canvases[i].photo = None

                    if processed_image is not None:
                        processed_image_small = self.resize_frame_keep_aspect(processed_image, (self.small_width, self.small_height))
                        self.processed_history_canvases[i].original_image = processed_image
                        self.processed_history_canvases[i].photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(processed_image_small))
                        self.processed_history_canvases[i].create_image(
                            self.small_width / 2,
                            self.small_height / 2,
                            image=self.processed_history_canvases[i].photo,
                            anchor=CENTER)
                    else:
                        self.processed_history_canvases[i].delete("all")
                        self.processed_history_canvases[i].original_image = None
                        self.processed_history_canvases[i].photo = None

                else:
                    self.stats_textboxes[i]["text"] = "no data for window: " + str(i)
                    self.raw_history_canvases[i].delete("all")
                    self.raw_history_canvases[i].original_image = None
                    self.raw_history_canvases[i].photo = None
                    self.processed_history_canvases[i].delete("all")
                    self.processed_history_canvases[i].original_image = None
                    self.processed_history_canvases[i].photo = None

        self.tk_root.after(self.history_update_wait_ms, self.update_history)


    def save_masks(self):
        red, green, blue = cv2.split(self.ui_coloured_mask)
        mask_image = cv2.cvtColor(blue, cv2.COLOR_GRAY2RGB)
        skimage.io.imsave(self.db.mask_image_path, mask_image)
        skimage.io.imsave(self.db.mask_ref_image_path, self.mask_ref_image)


    def load_masks(self):
        if os.path.isfile(self.db.mask_image_path):
            mask_bw = skimage.io.imread(self.db.mask_image_path)
        else:
            mask_bw = np.full(
                (self.image_source.cam_height, self.image_source.cam_width, 3),
                (255, 255, 255),
                np.uint8)

        if os.path.isfile(self.db.mask_ref_image_path):
            self.mask_ref_image = skimage.io.imread(self.db.mask_ref_image_path)
        else:
            self.mask_ref_image = skimage.io.imread(self.db.default_mask_ref_path)
            self.mask_ref_image = cv2.cvtColor(self.mask_ref_image, cv2.COLOR_RGBA2RGB)

        inverted_image = cv2.bitwise_not(mask_bw)
        red_image = np.full((self.image_source.cam_height, self.image_source.cam_width, 3), (1, 0, 0), np.uint8)
        blue_image = np.full((self.image_source.cam_height, self.image_source.cam_width, 3), (0, 0, 1), np.uint8)
        cv2.multiply(mask_bw, blue_image,  blue_image)
        cv2.multiply(inverted_image, red_image, red_image)
        save_this = False
        self.ui_coloured_mask = cv2.add(red_image, blue_image)

    def process_main_image(self, frame):
        if self.uistate == uistate_live_detect:
            return frame
        else:
            # convert the main image to black and white (and back to colour)
            # cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY, self.bw_image)
            # cv2.cvtColor(self.bw_image, cv2.COLOR_GRAY2RGB, self.bw_image_col)

            # reduce contrast + add brightness
            cv2.convertScaleAbs(frame, self.adjusted_image, 0.75, 64)
            cv2.multiply(self.adjusted_image, self.ui_coloured_mask, self.show_main_image, 1/255.0)

            # this should not be done every frame
            return self.show_main_image


    def lookup_friendly_name(self, oef_key):
        name = self.db.lookup_friendly_name(oef_key)
        if name is None:
            return oef_key
        else:
            return name