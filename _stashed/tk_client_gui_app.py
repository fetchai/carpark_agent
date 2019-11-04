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


class TkClientGuiApp:

    def __init__(
            self,
            window_title,
            carparkclientagent,
            screen_width_frac=0.9,
            max_num_services=10):

        # Configuration parameters
        self.screen_width_frac = screen_width_frac
        self.max_num_services = max_num_services
        self.have_data = False
        self.have_agents = False
        self.carparkclientagent = carparkclientagent

        # Main window appearance
        self.bg_live_col = "#1c1c2c"
        self.bg_use_col = self.bg_live_col
        self.tk_root = Tk()
        self.screen_width = self.tk_root.winfo_screenwidth()
        self.screen_height = self.tk_root.winfo_screenheight()
        self.tk_root.configure(background=self.bg_use_col)
        self.tk_root.title(window_title)

        # We scale the app to an appropriate size on screen such that it is 75% of the screen width
        self.scaled_total_width = self.screen_width * self.screen_width_frac
        base_width = 1280
        self.scale_factor = self.scaled_total_width / base_width
        base_font_size = 12
        self.use_font_size = -int(base_font_size * self.scale_factor)
        self.use_small_font_size = -int(2 * self.use_font_size / 3)
        unscaled_border_width = 4
        self.border_width = int(unscaled_border_width * self.scale_factor)
        self.small_height = 200 * self.screen_width_frac

        # Set up styles for buttons (as they don't change colour on osx in normal mode!)
        # background="..." doesn't work even using this method
        self.button_style = ttk.Style()
        self.button_style.map(
            'C.TButton',
            foreground=[('disabled', 'grey50'), ('!disabled', 'black')],
        )

        # Create three frames on top of each other to put various bits and bobs
        self.ui_frame = Frame(
            self.tk_root,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)

        self.ui_frame.grid(row=0, column=0)

        self.list_frame = Frame(
            self.tk_root,
            width=self.scaled_total_width,
            height=int(self.scaled_total_width / 4),
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.list_frame.grid(row=1, column=0)
        self.list_frame.pack_propagate(0)

        self.feedback_frame = Frame(
            self.tk_root,
            background=self.bg_use_col,
            borderwidth=0,
            highlightthickness=0)
        self.feedback_frame.grid(row=2, column=0)

        # How much FET do we have?
        self.current_fet_label = Label(
                self.ui_frame,
                borderwidth=self.border_width,
                highlightthickness=0,
                background="black",
                foreground="gray",
                justify=LEFT,
                font=("Arial", self.use_font_size),
                text="Current FET: -")
        self.current_fet_label.grid(row=0, column=0, sticky="NW")

        # Buttons
        button_pos = 1
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
        button_pos += 1

        self.do_search_button = ttk.Button(
            self.ui_frame,
            text="Search",
            style='C.TButton',
            command=self.do_search)
        self.do_search_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.do_cfp_button = ttk.Button(
            self.ui_frame,
            text="CFP",
            style='C.TButton',
            command=self.do_cfp)
        self.do_cfp_button.grid(row=0, column=button_pos)
        button_pos += 1

        self.request_data_button = ttk.Button(
            self.ui_frame,
            text="Request Data",
            style='C.TButton',
            command=self.do_request_data)
        self.request_data_button.grid(row=0, column=button_pos)
        button_pos += 1

        gap = Label(
            self.ui_frame,
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_use_col,
            text=gaps_text)
        gap.grid(row=0, column=button_pos)
        button_pos += 1

        self.generate_fet_button = ttk.Button(
            self.ui_frame,
            text="Generate 0.0001 FET",
            style='C.TButton',
            command=self.do_generate_fet)
        self.generate_fet_button.grid(row=0, column=button_pos)
        self.fet_to_generate = 100000
        button_pos += 1

        self.public_key_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Public Key]")
        self.public_key_text.pack(expand=True, fill='both', side=LEFT)

        self.location_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Location]")
        self.location_text.pack(expand=True, fill='both', side=LEFT)

        self.name_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Name]")
        self.name_text.pack(expand=True, fill='both', side=LEFT)

        self.time_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Last data time]")
        self.time_text.pack(expand=True, fill='both', side=LEFT)

        self.max_spaces_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Max spaces]")
        self.max_spaces_text.pack(expand=True, fill='both', side=LEFT)

        self.fet_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[cost in FET]")
        self.fet_text.pack(expand=True, fill='both', side=LEFT)

        self.is_acceptable_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Matches criteria]")
        self.is_acceptable_text.pack(expand=True, fill='both', side=LEFT)


        self.spaces_text = Label(
            self.list_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_font_size),
            text="[Num spaces available]")
        self.spaces_text.pack(expand=True, fill='both', side=LEFT)

         # Need to make a frame around it in order to specify size in pixels
        self.status_frame = Frame(
            self.feedback_frame,
            width=2*self.scaled_total_width/5,
            height=self.small_height,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0,
            background=self.bg_use_col)
        self.status_frame.grid(row=0, column=0, padx=0, pady=0)
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

        self.message_frame = Frame(
            self.feedback_frame,
            width=3*self.scaled_total_width/5,
            height=self.small_height,
            borderwidth=self.border_width,
            highlightbackground=self.bg_use_col,
            highlightthickness=0,
            background=self.bg_use_col)
        self.message_frame.grid(row=0, column=1, padx=0, pady=0)
        self.message_frame.pack_propagate(0)


        self.msg_title_text = Label(
            self.message_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="OEF Messages:")
        self.msg_title_text.pack(expand=True, fill='both', side=TOP)

        # couldn't get this text box to start at the top without first filling it with \n
        self.msg_main_text = Label(
            self.message_frame,
            borderwidth=0,
            highlightthickness=0,
            background="black",
            foreground="gray",
            anchor=NW,
            justify=LEFT,
            font=("Arial", self.use_small_font_size),
            text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        self.msg_main_text.pack(expand=True, fill='both', side=LEFT)

        # UI stuff
        self.setup_ui_state()

        # Handle Events
        self.tk_root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Make the top-most window
        self.tk_root.lift()
        self.tk_root.attributes("-topmost", 1)
        self.tk_root.attributes("-topmost", 0)

        # Start the window and update loop and
        self.history_update_wait_ms = 200
        self.update_history()
        self.tk_root.mainloop()

    def have_enough_fet(self):
        return True

    def setup_ui_state(self):
        self.do_search_button.state(["!disabled"])

        if self.carparkclientagent.can_do_cfp():
            self.do_cfp_button.state(["!disabled"])
        else:
            self.do_cfp_button.state(["disabled"])

        if self.carparkclientagent.can_do_accept_decline():
            self.request_data_button.state(["!disabled"])
        else:
            self.request_data_button.state(["disabled"])

        self.generate_fet_button.state(["!disabled"])

    def do_search(self):
        self.carparkclientagent.perform_search()
        self.have_data = False
        self.setup_ui_state()


    def do_cfp(self):
        self.carparkclientagent.do_cfp_to_all()
        self.setup_ui_state()

    def do_request_data(self):
        self.carparkclientagent.do_accept_decline_to_all()
        self.setup_ui_state()

    def do_generate_fet(self):
        self.carparkclientagent.generate_wealth(self.fet_to_generate)
        self.setup_ui_state()

    def on_exit(self):
        self.tk_root.destroy()



    def update_history(self):
        public_key_text = "Public key:\n"
        location_text = "Location:\n"
        name_text = "Friendly name:\n"
        time_text = "Time:\n"
        max_spaces_text = "Max capacity:\n"
        fet_text = "FET:\n"
        is_acceptable = "Is acceptable?:\n"
        spaces_text = "Spaces left:\n"


        for data in self.carparkclientagent.agents_data.values():
            if "public_key" in data:
                public_key_text += data["public_key"][:8] + "...\n"
            else:
                public_key_text += "-\n"

            if "lat" in data and "lon" in data:
                location_text += data["lat"] + ", " + data["lon"] + "\n"
            else:
                location_text += "-\n"

            if "friendly_name" in data:
                name_text += data["friendly_name"] + "\n"
            else:
                name_text += "-\n"

            if "last_detection_time" in data:
                time_text += time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["last_detection_time"])) + "\n"
            else:
                time_text += "-\n"

            if "max_spaces" in data:
                max_spaces_text += str(data["max_spaces"]) + "\n"
            else:
                max_spaces_text += "-\n"

            if "price" in data:
                fet_text += self.sdk_fet_to_human_fet(data["price"]) + "\n"
            else:
                fet_text += "-\n"

            if "last_detection_time" in data and  "price" in data:
                if self.carparkclientagent.is_acceptable_proposal(data['price'], data["last_detection_time"]):
                    is_acceptable += "Yes\n"
                else:
                    is_acceptable += "No\n"
            else:
                is_acceptable += "-\n"

            if "num_free_spaces" in data:
                spaces_text += str(data["num_free_spaces"]) + "\n"
            else:
                spaces_text += "-\n"

        self.public_key_text["text"] = public_key_text
        self.location_text["text"] = location_text
        self.name_text["text"] = name_text
        self.time_text["text"] = time_text
        self.max_spaces_text["text"] = max_spaces_text
        self.fet_text["text"] = fet_text
        self.spaces_text["text"] = spaces_text
        self.is_acceptable_text["text"] = is_acceptable

        current_fet = self.carparkclientagent.calc_uncleared_fet()
        self.current_fet_label["text"] = "Current FET: " + self.sdk_fet_to_human_fet(current_fet)

        while self.carparkclientagent.has_log_msgs():
            self.msg_main_text["text"] = self.carparkclientagent.pop_msg() + "\n" + self.msg_main_text["text"]

        status_str = "System status:\n"
        status_str += "OEF public key: {}\n".format(self.carparkclientagent.public_key)
        status_str += "Friendly name: {}\n".format(self.carparkclientagent.friendly_name)
        status_str += "Uncleared FET: {}\n".format(self.carparkclientagent.calc_uncleared_fet())
        status_str += "Cleared FET: {}\n".format(self.carparkclientagent.cleared_fet)
        status_str += "Ledger status: {}:{}: {}\n".format(
            self.carparkclientagent.ledger_ip,
            self.carparkclientagent.ledger_port,
            self.carparkclientagent.ledger_status)
        status_str += "OEF status: {}:{}: {}\n".format(
            self.carparkclientagent.oef_ip,
            self.carparkclientagent.oef_port,
            self.carparkclientagent.oef_status)
        self.status_text["text"] = status_str
        self.setup_ui_state()
        self.tk_root.after(self.history_update_wait_ms, self.update_history)


    # convert fet as used by the SDK into actual fet (not nano-pico fet - or whatever) and display as
    # a human readable string.
    def sdk_fet_to_human_fet(self, fet):
        return "{0:.10f}".format(fet * 0.0000000001)