import time
import schedule
import logging
from django.core.management import BaseCommand, call_command

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Lanceur de tâches automatisées pour les sauvegardes"

    def job(self):
        self.stdout.write(self.style.WARNING("Démarrage de la sauvegarde automatique (DB + Media)..."))
        try:
            # --clean permet de supprimer les anciennes sauvegardes pour n'en garder que 5
            call_command("dbbackup", clean=True)
            self.stdout.write(self.style.SUCCESS("Sauvegarde DB réussie."))
            
            call_command("mediabackup", clean=True)
            self.stdout.write(self.style.SUCCESS("Sauvegarde Media réussie."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erreur lors de la sauvegarde: {e}"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Démarrage du processus de sauvegardes automatiques via Schedule."))
        self.stdout.write("Fréquence: Tous les dimanches à 03:00.")
        
        # On définit la planification :
        # Tous les dimanches à 3h du matin (une fois par semaine)
        schedule.every().sunday.at("03:00").do(self.job)

        # On fait une première sauvegarde immédiate au lancement pour avoir au moins 1 fichier !
        self.job()

        # Boucle infinie qui vérifie si une tâche doit être exécutée
        while True:
            schedule.run_pending()
            time.sleep(60)

