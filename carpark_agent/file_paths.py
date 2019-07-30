import os

class FilePaths:
    this_dir = str(os.path.dirname(__file__))
    temp_dir = str(os.path.join(this_dir, '..', "temp_files"))

    mask_image_path = temp_dir + "/mask.tiff"
    mask_ref_image_path = temp_dir + "/mask_ref.tiff"
    raw_image_dir = temp_dir + "/db_raw_images/"
    processed_image_dir = temp_dir + "/db_processed_images/"
    # Note that this path should be under source control
    default_mask_ref_path = this_dir + "/default_mask_ref.png"
    num_digits_time = 12  # need to match this up with the generate functions below
    image_file_ext = ".png"

    def __init__(self):
        pass

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


    # @classmethod
    # def set_this_dir(cls, new_dir):
    #     this_dir = new_dir
    #     cls.mask_image_path = this_dir + "/mask.tiff"
    #     cls.mask_ref_image_path = this_dir + "/mask_ref.tiff"
    #     cls.database_path = this_dir + "/images.db"
    #     cls.raw_image_dir = this_dir + "/db_raw_images/"
    #     cls.processed_image_dir = this_dir + "/db_processed_images/"
    #     # Note that this path should be under source control
    #     cls.default_mask_ref_path = this_dir + "/default_mask_ref.png"
    #     cls.num_digits_time = 12  # need to match this up with the generate functions below
    #     cls.image_file_ext = ".png"
    #

