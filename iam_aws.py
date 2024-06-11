import boto3
from botocore.exceptions import ClientError
from password_generator import PasswordGenerator

client = boto3.client("iam")



def random_password():
    passw= PasswordGenerator()
    passw.minlen = 14
    passw.maxlen = 22
    passw.minuchars = 2
    passwd = passw.generate()
    return passwd

def attach_user_policy(username):
    try: 
        change = client.attach_user_policy(
            UserName=username,
            PolicyArn="arn:aws:iam::aws:policy/IAMUserChangePassword"
        )
        print(f"Policy  IAMUserChangePassword  attached to User {username}" )
    except Exception as e:
        print(f'An error occured : {e}')

def Onboarding(username):
    try:
        client.get_user(UserName=username)
        print(f'User {username} Already Exist ')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"Creating User {username}")
            user = client.create_user(UserName=username,
                              Tags=[
                                  {
                                      'Key': "boto3",
                                      'Value': username
                                  }
                              ])
            print(f"User {username} Created ....\n")
            print("Generating Access and Secret Keys.......")
            keys = client.create_access_key(

                    UserName=username
            )
            print("Keep the Secret key Safe \n")
            print(f"Access keys for user {username} ")
            print(f"Access ID :- {keys['AccessKey']['AccessKeyId']}")
            print(f"Secret Key :- {keys['AccessKey']['SecretAccessKey']}")
            print(f"Status :- {keys['AccessKey']['Status']}")

            print("\nCreating AWS MANAGEMENT Console Profile.....")
            passwd = random_password()
            login_profile = client.create_login_profile(
                UserName=username,
                Password=passwd,
                PasswordResetRequired=True
            )
            print(f"User {username} Created with password  '{passwd}'")
            attach_user_policy(username)



        else:
            print(f"Unexpected error: {e}")

def Deboarding(username):
    client = boto3.client('iam')

    try:
        
        attached_policies_response = client.list_attached_user_policies(UserName=username)
        for policy in attached_policies_response.get('AttachedPolicies', []):
            client.detach_user_policy(UserName=username, PolicyArn=policy['PolicyArn'])
            print(f"Policy {policy['PolicyArn']} detached from user {username}.")

        groups_response = client.list_groups_for_user(UserName=username)
        for group in groups_response.get('Groups', []):
            client.remove_user_from_group(UserName=username, GroupName=group['GroupName'])
            print(f"User {username} removed from group {group['GroupName']}.")

        roles_response = client.list_roles()
        for role in roles_response['Roles']:
            attached_users = client.list_role_tags(RoleName=role['RoleName']).get('Tags', [])
            for user in attached_users:
                if user['Key'] == 'UserName' and user['Value'] == username:
                    client.remove_user_from_role(UserName=username, RoleName=role['RoleName'])
                    print(f"User {username} removed from role {role['RoleName']}.")

        access_keys_response = client.list_access_keys(UserName=username)
        for key_metadata in access_keys_response.get('AccessKeyMetadata', []):
            access_key_id = key_metadata['AccessKeyId']
            client.delete_access_key(UserName=username, AccessKeyId=access_key_id)
            print(f"Access key {access_key_id} deleted for user {username}.")
        try:
            client.delete_login_profile(UserName=username)
            print(f"Login profile deleted for user {username}.")
        except client.exceptions.NoSuchEntityException:
            print("No  Login Profile found")

        
        client.delete_user(UserName=username)
        print(f"IAM user {username} deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")

def list_user():     
    list_user = client.list_users()
    count = 1
    print("Users :- ")
    for x in list_user["Users"]:
        print(count , x['UserName'])
        count+=1
    print('\n')

def main():
    print("Select an Option: ")
    print("1. List  Users ")
    print("2. Onboarding")
    print("3. Deboarding")
    choice = input("Enter your choice (1 ,2 or 3 ): ")

    if choice not in ['1','2','3']:
        print("Invalid choice.Please enter from 1 , 2 or 3")
        return
    
    if choice == '1':
        list_user()
    elif choice == '2':
        username = input("Enter  the username ")
        Onboarding(username)
    elif choice == '3':
        username = input("Enter  the username ")
        Deboarding(username)
    
if __name__== "__main__":
    main()


#Onboarding("Ayush-AWS")
#Deboarding("iam_aws3")