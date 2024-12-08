some examples to use 
        
# Configuration IAM nécessaire : Votre rôle IAM pour Lambda doit disposer des permissions suivantes pour envoyer des journaux à CloudWatch :

# {
#     "Effect": "Allow",
#     "Action": [
#         "logs:CreateLogGroup",
#         "logs:CreateLogStream",
#         "logs:PutLogEvents"
#     ],
#     "Resource": "arn:aws:logs:*:*:*"
# }



# Groupes et flux de journaux :

# Lambda crée automatiquement un groupe de journaux nommé /aws/lambda/<NomDeLaFonction> si celui-ci n'existe pas.


# Comment consulter les logs dans AWS ?
# Via la console AWS :

# Accédez à CloudWatch > Logs.
# Trouvez le groupe de journaux nommé /aws/lambda/<NomDeLaFonction>.
# Sélectionnez un flux de journaux correspondant à une exécution spécifique.
# Avec AWS CLI : Utilisez cette commande pour récupérer les journaux :

# bash
# Copy code
# aws logs filter-log-events --log-group-name "/aws/lambda/<NomDeLaFonction>"
