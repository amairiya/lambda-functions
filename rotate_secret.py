import boto3
import json
import logging

# Configurer le logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    # Setup the client
    service_client = boto3.client('secretsmanager')

    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    if not metadata['RotationEnabled']:
        raise ValueError("Secret %s is not enabled for rotation" % arn)
    
    if step == "createSecret":
        create_secret(service_client, arn, token)

    elif step == "setSecret":
        set_secret(service_client, arn, token)

    elif step == "testSecret":
        test_secret(service_client, arn, token)

    elif step == "finishSecret":
        finish_secret(service_client, arn, token)

    else:
        raise ValueError("Invalid step parameter")


def create_secret(service_client, arn, token):

    service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")

    # Load password configuration from JSON file
    config_file_path = 'password_config.json'  # Replace with your file path

    secret_name = arn.split(":")[-1]
    # Check and perform actions based on substrings
    if '_walletkey' in secret_name:
        config_file_path = 'walletkey_config.json'  # Replace with your file path
    elif '_apikey' in secret_name:
        config_file_path = 'apikey_config.json'  # Replace with your file path
    elif 'seed' in secret_name:
        config_file_path = 'seed_config.json'  # Replace with your file path
    else:
        print(f"No specific action for secret: {secret_name}")


    try:
        with open(config_file_path, 'r') as file:
            password_config = json.load(file)
        logger.info("Password configuration loaded: %s", password_config)
    except Exception as e:
        logger.error("Failed to load password configuration: %s", str(e))
        return {
            'statusCode': 500,
            'body': "Error loading password configuration."
        }
    
    # Extract parameters for password generation
    password_params = {
        "PasswordLength": password_config.get("PasswordLength", 32),
        "ExcludeNumbers": password_config.get("ExcludeNumbers", False),
        "ExcludeUppercase": password_config.get("ExcludeUppercase", False),
        "ExcludeLowercase": password_config.get("ExcludeLowercase", False),
        "IncludeSpace": password_config.get("IncludeSpace", False),
        "RequireEachIncludedType": password_config.get("RequireEachIncludedType", True),
    }

    # Now try to get the secret version, if that fails, put a new secret
    try:
        service_client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
    except service_client.exceptions.ResourceNotFoundException:
        # Generate a random password
        passwd  = service_client.get_random_password(**password_params)

        # Create the payload with the specific key
        secret_payload = {
            "key": passwd['RandomPassword']  # Replace "walletkey" with the specific key you want
        }

        # # Put the secret
        # service_client.put_secret_value(SecretId=arn, ClientRequestToken=token, SecretString=passwd['RandomPassword'], VersionStages=['AWSPENDING'])
        # Store the updated secret
        service_client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps(secret_payload),
            VersionStages=['AWSPENDING']
        )

def set_secret(service_client, arn, token):
    print("No database user credentials to update...")


def test_secret(service_client, arn, token):
    print("No need to testing against any service...")


def finish_secret(service_client, arn, token):
   
    # First describe the secret to get the current version
    metadata = service_client.describe_secret(SecretId=arn)

    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                return

            # Finalize by staging the secret version current
            service_client.update_secret_version_stage(SecretId=arn, VersionStage="AWSCURRENT", MoveToVersionId=token, RemoveFromVersionId=version)
            break
