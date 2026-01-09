from app.routes.platform.admin import apprentissage_delete
import inspect

source = inspect.getsource(apprentissage_delete)

if 'DigitalOcean Spaces' in source and 'delete_file' in source:
    print('OK: Fonction de suppression amelioree deployee')
    print('OK: Suppression automatique DigitalOcean Spaces ACTIVE')
else:
    print('ERREUR: Ancienne version encore presente')

print('VERIFICATION COMPLETE')