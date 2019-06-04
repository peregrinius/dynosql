import botocore
import logging

logger = logging.getLogger(__name__)

from dynosql.helper_methods import DYNAMODB_DATATYPES_LOOKUP
from dynosql.helper_methods import DYNAMODB_DATATYPES_LOOKUP2
from dynosql.helper_methods import DYNAMODB_DATATYPES_REVERSE_LOOKUP
from dynosql.helper_methods import UNFLUFF

class DynoRecord(object):
    """ DynoRecord is the wrapper class around each record

    """
    def __init__(self, table, key, attributes=None):
        self.table = table
        self.key = key
        self.__json = { }

        if not attributes:
            # Fetching data
            logger.info('fetching: %s' % str(self.key))

            keys = self._get_keys()
            try:
                response = self.table.client.get_item(
                    TableName=self.table.table_name,
                    Key=keys
                )
                self.__json = UNFLUFF(response)
            except self.table.client.exceptions.ResourceNotFoundException as e:
                # botocore.exceptions.ClientError
                logger.error(e)
                logger.info(self.table.table_name)
                raise KeyError(str(e))
        else:
            # Inserting data
            logger.info('inserting: {%s : %s}' % (str(self.key), attributes))
            items = {
                attribute_name:
                {
                    DYNAMODB_DATATYPES_LOOKUP[type(attribute_value).__name__]: str(attribute_value)
                } for attribute_name, attribute_value in attributes.items()
            }
            items = {**items, **self._get_keys()}
            try:
                self.describe = self.table.client.put_item(
                    TableName=self.table.table_name,
                    Item=items
                )
            except botocore.exceptions.ClientError as e:
                logger.error(e)
                raise KeyError(str(e))

    # def __new__(cls, table, key, attributes=None):
    #     if attributes:
    #         return super(DynoRecord, cls).__new__(cls)
    #     else:
    #          pass


    def __getitem__(self, key):
        """
        """
        try:
            logger.info('getitem: %s' % str(key))
            return self.__json[key]
        except KeyError:
            return self.__json


    def __setitem__(self, key, attributes):
        """
        """
        logger.info('setitem: %s - %s - %s' % (self.__json, str(key), attributes))
        self.table.client.update_item(
            TableName=self.table.table_name,
            Key=self._get_keys(),
            ExpressionAttributeNames={
                '#X': str(key)
            },
            ExpressionAttributeValues={
                ':y': {
                    DYNAMODB_DATATYPES_LOOKUP[type(attributes).__name__]: str(attributes),
                },
            },
            UpdateExpression='SET #X = :y',
        )


    @property
    def json(self):
        return self.__json


    def _get_keys(self):
        try:
            partition_key_value, sort_key_value = self.key
            keys = {
                self.table.partition_key[0]: { DYNAMODB_DATATYPES_LOOKUP[self.table.partition_key[1]]: str(partition_key_value) },
                self.table.sort_key[0]: { DYNAMODB_DATATYPES_LOOKUP[self.table.sort_key[1]]: str(sort_key_value) }
            }
        except ValueError:
            partition_key_value, sort_key_value = (self.key, None,)
            keys = {
                self.table.partition_key[0]: { DYNAMODB_DATATYPES_LOOKUP[self.table.partition_key[1]]: str(partition_key_value) }
            }
        except TypeError:
            raise KeyError('Table was not defined with a sort key')

        return keys
