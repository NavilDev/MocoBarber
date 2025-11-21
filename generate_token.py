from google_auth_oauthlib.flow import InstalledAppFlow

def main():
    # Define los scopes que necesitas
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    # Ruta a tu archivo client_secret.json
    CLIENT_SECRET_FILE = '/Users/navilkabbouch/Documents/ProyectosPython/Barberia/barberia_app/credenciales/client_secret.json'

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES
    )

    creds = flow.run_local_server(port=0)

    # Guarda las credenciales en token.json
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("✅ token.json generado correctamente")

if __name__ == '__main__':
    main()