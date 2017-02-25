"""The GUI Interface for the part maker."""

import os
import random
import tkinter
import tkinter.filedialog
import tkinter.messagebox

from here_the_leafsighaway import config


class VerticalScrolledFrame(tkinter.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    Courtesy of http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    """
    def __init__(self, parent, *args, **kw):
        tkinter.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
        canvas = tkinter.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tkinter.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tkinter.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class InstrumentField:

    def __init__(self, frame, row, column, instrument_name):
        """
        Spinbox & label pairs for use in the instrument selection frame
        :param frame: Tkinter Frame
        :param row: int
        :param column: int
        :param instrument_name: str
        """
        self.instrument_name = instrument_name
        self.label = tkinter.Label(frame, text=self.instrument_name)

        def validate_spinbox(d, i, P, s, S, v, V, W):
            if V=='focusin' or V=='forced':
                return True
            if V == 'focusout' and P == '':
                # This doesn't seem to work...
                return False
            if str(P) == '':
                return True
            if not str(P).isdigit():
                return False
            else:
                if int(P) < 0:
                    return False
                else:
                    return True

        # Register validation function in the frame (How does this work? I have no idea...)
        # http://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        validate_command = (frame.register(validate_spinbox),
                            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.spinbox = tkinter.Spinbox(frame, from_=0, to=9999999999, width=7,
                                       validate='all', validatecommand=validate_command)

        self.spinbox.grid(row=row, column=column, sticky=tkinter.E)
        self.label.grid(row=row, column=column+1, sticky='w')

    def get_value(self):
        return self.spinbox.get()


class Application(tkinter.Frame):
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.master.title('Part Maker')
        self.master.geometry('645x420')
        self.master.maxsize(645, 420)

        self.part_name_pool = ['Flute', 'Alto Flute', 'Oboe', 'Clarinet', 'Bassoon', 'High Horn',
                               'Low Horn', 'Trumpet', 'Tenor Trombone', 'Toy Piano', 'Guitar',
                               'Percussion', 'Violin', 'Viola', 'Cello', 'Bass']
        self.part_and_speaker_name_pool = ['Speaker', 'Audience', 'Flute & Speaker', 'Alto Flute & Speaker',
                                           'Oboe & Speaker', 'Clarinet & Speaker', 'Bassoon & Speaker',
                                           'High Horn & Speaker', 'Low Horn & Speaker', 'Trumpet & Speaker',
                                           'Tenor Trombone & Speaker', 'Toy Piano & Speaker', 'Guitar & Speaker',
                                           'Percussion & Speaker', 'Violin & Speaker', 'Viola & Speaker',
                                           'Cello & Speaker', 'Bass & Speaker']

        self.instrument_fields = []
        self.instrument_and_speaker_fields = []
        self.directory_display = None
        self.directory_button = None
        self.build_instruction_label()
        self.build_selection_frame()
        self.build_page_count_field()
        self.build_directory_field()
        self.build_go_button()
        self.configure_grid_weights()

        self.pack(expand=True, fill='both')


    def configure_grid_weights(self):
        self.grid_rowconfigure(3, weight=10)
        self.columnconfigure(0, weight=10)


    def build_directory_field(self):

        directory_path = tkinter.StringVar(self, config.PartOutputFolder, 'directory variable')
        self.directory_display = tkinter.Label(self, textvariable=directory_path, justify=tkinter.RIGHT,
                                               padx=4, pady=2)

        def directory_button_action():
            new_dir = tkinter.filedialog.askdirectory(initialdir=directory_path)
            if new_dir != '':
                directory_path.set(new_dir)
                config.PartOutputFolder = os.path.abspath(new_dir)

        self.directory_button = tkinter.Button(self, text='Choose a different output folder (Optional)',
                                               command=directory_button_action, padx=2, pady=1)
        self.directory_label = tkinter.Label(self, text='Output folder for new parts', justify=tkinter.LEFT, pady=0)
        self.directory_label.grid(row=4, column=0, sticky='sw', padx=(4, 2))
        self.directory_display.grid(row=5, column=0, sticky='sw', padx=(2, 2))
        self.directory_button.grid(row=6, column=0, sticky='sw', padx=(2, 2))

    def build_go_button(self):
        self.go_button = tkinter.Button(self, text='Make Parts', font='-weight bold', command=self.go_button_action)
        # self.go_button.pack(side=Tkinter.BOTTOM, anchor='se')
        self.go_button.grid(row=5, column=1, rowspan=2, sticky='se')

    def build_instruction_label(self):
        instruction_text = "This is the part making program for 'here, the leafsighaway.' If you don't know what's going on, please check out the documentation in the main folder. To build parts, simply select the number of each type of part you want and press the 'Make Parts' button. If you want, you can edit where the output parts will go or set the approximate number of pages of each part, though this will vary considerably from part to part. It usually takes a couple minutes to make each part, so this may take some time. Please forgive the clumsy interface."
        self.instruction_label_widget = tkinter.Label(self, text=instruction_text,
                                                      anchor='nw', justify=tkinter.LEFT, wraplength=640)
        self.instruction_label_widget.grid(row=0, column=0, columnspan=2, sticky='nw', padx=(4, 4))

    def build_selection_frame(self):
        self.selection_frame = VerticalScrolledFrame(self, borderwidth=4, padx=4, pady=4, relief=tkinter.SUNKEN)
        # self.selection_frame.pack(expand=True, fill='both', anchor='ne')
        self.selection_frame.grid(row=1, column=0, rowspan=3, sticky='nw', padx=(4, 2))

        # Enter fields in two columns - left is instruments, right is instruments + speaker
        for index in range(0, len(self.part_name_pool)):
            self.instrument_fields.append(InstrumentField(self.selection_frame.interior,
                                                          index, 0, self.part_name_pool[index]))
        for index in range(0, len(self.part_and_speaker_name_pool)):
            self.instrument_and_speaker_fields.append(InstrumentField(self.selection_frame.interior,
                                                                      index, 3, self.part_and_speaker_name_pool[index]))
        tkinter.Label(self.selection_frame.interior, text='     '*6).grid(row=0, column=2)
        self.selection_frame.interior.columnconfigure(2, weight=5)

    def build_page_count_field(self):
        page_count_value = tkinter.StringVar(self, '20', 'Page Count Variable')
        self.page_count_label = tkinter.Label(self, text='Approximate target page count\n(This will vary widely)',
                                              justify=tkinter.LEFT)

        def validate_spinbox(d, i, P, s, S, v, V, W):
            if V == 'focusin' or V == 'forced':
                return True
            if V == 'focusout' and P == '':
                # This doesn't seem to work...
                return False
            if str(P) == '':
                return True
            if not str(P).isdigit():
                return False
            else:
                if int(P) <= 0:
                    return False
                else:
                    return True
        # Register validation function in the frame (How does this work? I have no idea...)
        # http://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        validate_command = (self.register(validate_spinbox),
                            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.page_count_spinbox = tkinter.Spinbox(self, from_=0, to=999, width=6, textvariable=page_count_value,
                                                  validate='all', validatecommand=validate_command)

        self.page_count_label.grid(row=1, column=1, sticky='nw', padx=(1, 4))
        self.page_count_spinbox.grid(row=2, column=1, sticky='nw')

    def go_button_action(self):
        # Collate a list of parts in a list of strings
        part_list = []
        for field in self.instrument_fields + self.instrument_and_speaker_fields:
            # Skip empty fields
            field_count = field.get_value()
            if not field_count:
                continue
            field_count = int(field_count)
            for i in range(0, field_count):
                part_list.append(field.instrument_name)
        total_part_count = len(part_list)
        approx_page_count_per_part = int(self.page_count_spinbox.get())
        approx_total_page_count = total_part_count * approx_page_count_per_part

        if approx_page_count_per_part < 1:
            tkinter.messagebox.showwarning('Hmmm....', "Please set the approximate page count to an integer greater than 0")
            return
        # Find an approx time in minutes - a very very rough approximation based on a few tests run on just MY machine
        approx_time = int(approx_total_page_count * 0.25)
        if total_part_count <= 0:
            tkinter.messagebox.showwarning('Hmmm....', "Looks like you don't have any parts selected\n(unless I am confused)")
            return

        confirm_message = ('All set to build ' + str(total_part_count) + ' parts at approximately ' +
                           str(approx_page_count_per_part) + ' pages each. \nBy my totally wild guess, '
                           'this should take somewhere \naround ' + str(approx_time) + ' minutes. Sound good?')
        do_continue = tkinter.messagebox.askokcancel('Confirm', confirm_message, default=tkinter.messagebox.OK)
        if not do_continue:
            return

        self.master.withdraw()

        print('Loading modules...')
        import here_the_leafsighaway.part_maker
        config.PartOutputFolder = os.path.join(config.PartOutputFolder,
                                               str(random.randint(0, 10000)))
        if not os.path.exists(config.PartOutputFolder):
            os.makedirs(config.PartOutputFolder)
        print("Launching the part engine! Hold on to your hats!")
        # Call part_maker and make the parts!
        here_the_leafsighaway.part_maker.make_parts(part_list, target_page_count=approx_page_count_per_part)

        tkinter.messagebox.showinfo('All done!', "Looks like everything went well, woohoo! "
                                    "Your new parts are located in:\n" +
                                    config.PartOutputFolder)
        self.master.quit()
