import os

class FilePaths:


    def __init__(self, root_dir):
        self.this_dir = str(os.path.dirname(__file__))
        self.run_dir = root_dir
        self.temp_dir = str(os.path.join(self.run_dir, '..', "temp_files"))

        self.mask_image_path = self.temp_dir + "/mask.tiff"
        self.mask_ref_image_path =self. temp_dir + "/mask_ref.tiff"
        self.raw_image_dir = self.temp_dir + "/db_raw_images/"
        self.processed_image_dir = self.temp_dir + "/db_processed_images/"
        # Note that this path should be under source control
        self.default_mask_ref_path = self.this_dir + "/default_mask_ref.png"
        self.num_digits_time = 12  # need to match this up with the generate functions below
        self.image_file_ext = ".png"

    @classmethod
    def ensure_dirs_exist(cls):
        if not os.path.isdir(cls.temp_dir):
            os.mkdir(cls.temp_dir)
        if not os.path.isdir(cls.raw_image_dir):
            os.mkdir(cls.raw_image_dir)
        if not os.path.isdir(cls.processed_image_dir):
            os.mkdir(cls.processed_image_dir)

    @classmethod
    def generate_raw_image_path(cls, t):
        return cls.raw_image_dir + "{0:012d}".format(t) + "_raw_image" + cls.image_file_ext

    @classmethod
    def generate_processed_path(cls, t):
        return cls.processed_image_dir + "{0:012d}".format(t)+ "_processed_image" + cls.image_file_ext

    @classmethod
    def generate_processed_from_raw_path(cls, raw_name):
        return raw_name.replace("_raw_image.", "_processed_image.").replace(cls.raw_image_dir, cls.processed_image_dir)

    @classmethod
    def extract_time_from_raw_path(cls, raw_name):
        start_index = len(cls.raw_image_dir)
        extracted_num = raw_name[start_index:start_index + cls.num_digits_time]
        return int(extracted_num)
