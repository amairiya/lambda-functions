import boto3
import json
import logging
# Configurer le logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    logger.info("La fonction Lambda a démarré.")
    logger.debug("Détails de l'événement : %s", event)
    
    # Initialise le client Secrets Manager
    secrets_manager_client = boto3.client('secretsmanager')
    
    # Nom du secret à créer
    secret_name = "my-new-secret"
    # Valeur du secret
    secret_value = {
        "username": "example_user",
        "password": "example_password"
    }
    
    try:
        # Créer un secret
        response = secrets_manager_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value)
        )
        
        # Votre logique ici
        result = {"message": "Succès"}
        logger.info("Traitement réussi : %s", result)
        
        return {
            'statusCode': 200,
            'body': f"Secret created successfully: {response}"
        }
    except secrets_manager_client.exceptions.ResourceExistsException:
        
        logger.info(f"Secret with the name '{secret_name}' already exists.")
        
        return {
            'statusCode': 400,
            'body': f"Secret with the name '{secret_name}' already exists."
        }
        
    except Exception as e:
        
        logger.error("Une erreur est survenue : %s", str(e))
    
        return {
            'statusCode': 500,
            'body': f"An error occurred: {str(e)}"
        }
        
