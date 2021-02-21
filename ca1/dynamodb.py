def get_data_from_dynamodb():
    try:
            import boto3
            from boto3.dynamodb.conditions import Key, Attr

            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('ButtonPress')

            startdate = '2021-02'
            
            response = table.query(
                KeyConditionExpression=Key('id').eq('assignment')& Key('datetimeinfo').begins_with(startdate),
                ScanIndexForward=False
            )

            items = response['Items']
            
            n=10 # limit to last 10 items
            data = items[:n]
            data_reversed = data[::-1]

            return data_reversed

    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])


if __name__ == "__main__":
    get_data_from_dynamodb()

