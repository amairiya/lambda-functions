import boto3
import json
import logging

# Configurer le logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("La fonction Lambda a démarré.")
    logger.debug("Détails de l'événement : %s", event)
    
    # Vérifie si le paramètre 'secret_name' est fourni dans l'événement
    secret_name = event.get('secret_name')
    if not secret_name:
        logger.error("Le paramètre 'secret_name' est manquant.")
        return {
            'statusCode': 400,
            'body': "Erreur : le paramètre 'secret_name' est requis."
        }
    
    # Initialise le client Secrets Manager
    secrets_manager_client = boto3.client('secretsmanager')
    
    # Liste des noms de secrets à créer
    secret_suffixes = ['_apikey', '_walletkey', '_seed']
    results = []
    
    for suffix in secret_suffixes:
        full_secret_name = f"{secret_name}{suffix}"
        secret_value = {"key": "Ceci est une variable provisoire "}
        
        try:
            # Créer un secret
            response = secrets_manager_client.create_secret(
                Name=full_secret_name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Secret '{full_secret_name}' créé avec succès : {response}")
            results.append({
                'status': 'success',
                'response': response,
                'secret_name': full_secret_name
            })
        except secrets_manager_client.exceptions.ResourceExistsException:
            logger.info(f"Le secret avec le nom '{full_secret_name}' existe déjà.")
            results.append({
                'status': 'failed',
                'reason': f"Le secret avec le nom '{full_secret_name}' existe déjà.",
                'secret_name': full_secret_name
            })
        except Exception as e:
            logger.error("Une erreur est survenue pour '%s': %s", full_secret_name, str(e))
            results.append({
                'status': 'failed',
                'reason': str(e),
                'secret_name': full_secret_name
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
