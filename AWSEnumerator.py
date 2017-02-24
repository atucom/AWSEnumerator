#!/usr/local/bin/python
import boto3
from botocore.exceptions import ClientError
import sys
import argparse
from IPython import embed

class AWSEnumerator():
  def __init__(self, access_key, secret_key):
    self.access_key = access_key
    self.secret_key = secret_key
    self.session = boto3.session.Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

  def list_s3(self):
    print("Checking for S3 buckets")
    s3_client = self.session.client("s3")
    try:
      buckets = s3_client.list_buckets()
    except ClientError as e:
      print("  Failure Reason: %s" %e.response['Error']['Code'])
      return
    print("  Total # of S3 buckets: %s" % len(buckets['Buckets']))
    for bucket in buckets['Buckets']:
      try:
        objectlist = s3_client.list_objects(Bucket=bucket['Name'])
        print("    Bucket: %s [%i objects]" % (bucket['Name'], len(objectlist['Contents'])))
      except KeyError: #Catch if no objects in bucket object listing
        print("    Bucket: %s [empty]" % (bucket['Name']))
      except ClientError as e: #Errors a lot if in region that requires AWS4-HMAC-SHA256
        print("    Bucket: %s Failure Reason: %s" % (bucket['Name'],e.response['Error']['Code']))


  def list_ec2(self):
    #list out count, name, public DNS, IP,
    print("Checking for EC2 Instances")
    try:
      ec2_resource = self.session.resource("ec2")
      ec2_client = self.session.client("ec2")
      instance_ids = []
      for i in ec2_resource.instances.all():
          instance_ids.append(i.id)
      print("  Total # of EC2 Instances: %s" % len(instance_ids))
      for id in instance_ids:
        response = ec2_client.describe_instances(InstanceIds=instance_ids, Filters=[{'Name':"instance-id", 'Values':[id] }])
        status =         response['Reservations'][0]['Instances'][0]['State']['Name']
        instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']
        if status == "running":
          public_ip =   response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
          print("    Instance: %s - %s - %s " %(instance_type, public_ip, status))
        else:
          print("    Instance: %s - %s" %(instance_type, status))
    except ClientError as e:
      print("    Failure Reason: %s" %e.response['Error']['Code'])
      return

  def list_lightsail(self):
    print("Checking for Lightsail Instances")
    lightsail_client = self.session.client("lightsail")
    try:
      instances = lightsail_client.get_instances()
      print("  Total # of Lightsail instances: %s" % len(instances['instances']))
      for i in instances['instances']:
          print("    Name: %s, Username: %s, IP: %s, State: %s" % (i['name'], i['username'],i['publicIpAddress'],i['state']['name']))
    except ClientError as e:
      print("    Failure Reason: %s" %e.response['Error']['Code'])
      return

  def list_dynamoDB(self):
    print("Checking for DynamoDB Tables")
    dynamo_client = self.session.client("dynamodb")
    try:
      response = dynamo_client.list_tables()
      print("  Total # of DynamoDB Tables: %s" % len(response['TableNames']))
      for table in response['TableNames']:
        print("    Table Name: %s" % table)
    except ClientError as e:
      print("    Failure Reason: %s" %e.response['Error']['Code'])

  def list_route53():
    pass



def main():
  """Main Execution"""
  parser = argparse.ArgumentParser(description='AWS API Key Enumerator',
                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                  epilog="Example: \n\t %s A95AIP7DU586PRYEASDYQ 5BoKxK4gqweIFqu5O94950VR2CqbJASJDI5S "%sys.argv[0])

  parser.add_argument('access',action="store",
            help='The AWS Access Key')
  parser.add_argument('secret', action="store",
            help='The AWS Secret Key')

  args = parser.parse_args() #reference args with args.argument_name
  access_key = args.access
  secret_key = args.secret

  a = AWSEnumerator(access_key, secret_key)
  a.list_s3()
  a.list_ec2()
  a.list_lightsail()
  a.list_dynamoDB()

if __name__ == '__main__':
  sys.exit(main())