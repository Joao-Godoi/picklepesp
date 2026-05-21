from django.core.management.base import BaseCommand

from tournament.services import recalculate_tournament


class Command(BaseCommand):
    help = "Recalcula vencedores, propagacoes e classificacoes do campeonato"

    def handle(self, *args, **options):
        self.stdout.write("Recalculando campeonato...")
        recalculate_tournament()
        self.stdout.write(self.style.SUCCESS("Recalculo concluido com sucesso."))
