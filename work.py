import boto3
import logging
import time
import os
import botocore
from boto3 import client
logfile=input("로그 파일 이름 뭘로할래 ")

from botocore.exceptions import ClientError
ec2 = boto3.client('ec2')
client = boto3.client('ec2')
response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId','')

############################로그

formatter = logging.Formatter('%(asctime)s %(message)s')
logger = logging.getLogger('myapp5')
hdlr = logging.FileHandler('%s.log'%(logfile))
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

############################로그

####################VPC 10개 만들기
try:
    for i in range(1,11):

        response = ec2.create_security_group(GroupName='HelloBOTO %s'%(i),
                                             Description='Made by boto3 %s'%(i),
                                             VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
        logger.info('%s'%(security_group_id))       ########로거

####################################################################################딜레이
        time.sleep(5)
####################################################################################딜레이

#####################in out 설정
#        data = ec2.authorize_security_group_ingress(
#        GroupId=security_group_id,
#        IpPermissions=[
#            {'IpProtocol':'tcp',
#             'FromPort':80,
#             'Toport': 80,
#             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
#            {'IpProtocol': 'tcp',
#             'FromPort':22,
#             'Toport':22,
#             'IpRanges':[{'CidrIp':'0.0.0.0/0'}]}
#        ])
#    print('Ingress Successfully Set %s' %data)
####################in out 설정
except ClientError as e:
    logger.error('VPC 생성 안돼')
####################VPC만드는 거 끝


######################지우는 거
m=0

result = client. describe_security_groups()
for value in result["SecurityGroups"]:
    try:
        m=m+1
        response = ec2.delete_security_group(GroupId=value["GroupId"])
        print('No. %d'%m, '%s Delete' %value["GroupId"])

        logger.info('No. %d  %s Delete'%(m, value["GroupId"]))
    except ClientError as e:
        logger.error('No. %d  %s DeleteX Default'%(m, value["GroupId"]))
        print("No. %d" %m, "%s DeleteX Default"%value["GroupId"])
#######################지우는 거

#####################버킷의 리스트가져오기
s3 = boto3.client('s3')    # Create an S3 client
# Call S3 to list current buckets
response = s3.list_buckets()
buckets = [bucket['Name'] for bucket in response['Buckets']]   # Get a list of all bucket names from the response
print("Bucket List: %s" % buckets)  # Print out the bucket list
#####################버킷의 리스트가져오기

########################버킷 동일 여부 체크
bucketname=input("만들 버켓 이름 = ")
rename=bucketname
switch=0
while True:
    try:
        s3 = boto3.client('s3', region_name="ap-southeast-1")
        response = s3.create_bucket(
            Bucket='%s' %(rename),
            CreateBucketConfiguration={
                'LocationConstraint': 'ap-southeast-1'
                }
            )
        print("%s으로 만듦" %rename)
        switch=1
    except:
        rename = input("있대 다시 = ")
    if switch==1:
        break
########################버킷 동일 여부 체크

inbucket=[]

s3 = boto3.resource('s3')
my_bucket = s3.Bucket(rename)
for awsfile in my_bucket.objects.all():
    inbucket.append(awsfile.key)

u=0
switch2=0
for u in range(len(inbucket)):
    if '%s.log'%(logfile) == inbucket[u]:
        switch2=1
    else:
        pass

#####################################그냥업로드

if switch2 == 0:
    s3 = boto3.client('s3')
    s3.upload_file('%s.log'%logfile, rename, '%s.log'%logfile)

#####################################그냥업로드

else:
####################################수정으로 내 PC에 다운로드
    BUCKET_NAME = '%s'%rename # replace with your bucket name
    KEY = '%s.log'%logfile # replace with your object key
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, 'log_data_수정.log')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
####################################수정으로 내 PC에 다운로드

####################################다운받은거 삭제
    s3 = boto3.resource('s3')
    s3.Object(rename, '%s.log'%logfile).delete()
####################################다운받은거 삭제

####################################합체
    with open("%s.log"%logfile, "r") as logstr:
        f=logstr.read()
        t = open("log_data_수정.log", 'a', encoding="utf8")
        t.write(f)
        t.close()
####################################합체

####################################다시 업로드
    s3 = boto3.client('s3')
    s3.upload_file( 'log_data_수정.log', rename, '%s.log'%logfile)
####################################다시 업로드
