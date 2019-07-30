
from oef.query import AttributeSchema
from oef.schema import DataModel




class CarParkDataModel (DataModel):

    LATITUDE_ATTR = AttributeSchema(
        "latitude",
        float,
        is_attribute_required=True,
        attribute_description="latitude of parking spaces"
    )
    LONGITUDE_ATTR = AttributeSchema(
        "longitude",
        float,
        is_attribute_required=True,
        attribute_description="longitude of parking spaces"
    )
    UNIQUEID_ATTR = AttributeSchema(
        "unique_id",
        str,
        is_attribute_required=True,
        attribute_description="unique id allowing us to search for this service explicitly"
    )
    def __init__(self):
        super(CarParkDataModel, self).__init__(
            "carpark_data",
            [self.LATITUDE_ATTR, self.LONGITUDE_ATTR, self.UNIQUEID_ATTR],
            "searchable criteria about the parking space service")
