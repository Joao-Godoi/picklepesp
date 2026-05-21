from django.db import models
from django.core.exceptions import ValidationError


class Group(models.Model):
    name = models.CharField("Nome", max_length=10, unique=True)

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ["name"]

    def __str__(self):
        return f"Grupo {self.name}"


class Team(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="teams",
        verbose_name="Grupo",
    )
    player1_name = models.CharField("Jogador 1", max_length=100)
    player2_name = models.CharField("Jogador 2", max_length=100)

    class Meta:
        verbose_name = "Dupla"
        verbose_name_plural = "Duplas"
        ordering = ["group", "pk"]
        unique_together = [["player1_name", "player2_name", "group"]]

    def __str__(self):
        return f"{self.player1_name} / {self.player2_name}"


class Match(models.Model):
    PHASE_GROUP = "group"
    PHASE_QUARTERFINAL = "quarterfinal"
    PHASE_SEMIFINAL = "semifinal"
    PHASE_THIRD_PLACE = "third_place"
    PHASE_FINAL = "final"
    PHASE_FIFTH_TO_EIGHTH = "fifth_to_eighth"
    PHASE_PLACEMENT_9_14 = "placement_9_14"

    PHASE_CHOICES = [
        (PHASE_GROUP, "Fase de grupos"),
        (PHASE_QUARTERFINAL, "Quartas de final"),
        (PHASE_SEMIFINAL, "Semifinal"),
        (PHASE_THIRD_PLACE, "Disputa de 3o lugar"),
        (PHASE_FINAL, "Final"),
        (PHASE_FIFTH_TO_EIGHTH, "Disputa de 5o ao 8o"),
        (PHASE_PLACEMENT_9_14, "Disputa de 9o ao 14o"),
    ]

    BRACKET_GROUP = "group"
    BRACKET_MAIN = "main"
    BRACKET_PLACEMENT = "placement"

    BRACKET_CHOICES = [
        (BRACKET_GROUP, "Grupo"),
        (BRACKET_MAIN, "Mata-mata principal"),
        (BRACKET_PLACEMENT, "Disputa de posicoes"),
    ]

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FINISHED = "finished"
    STATUS_BLOCKED = "blocked"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_IN_PROGRESS, "Em andamento"),
        (STATUS_FINISHED, "Finalizada"),
        (STATUS_BLOCKED, "Bloqueada"),
    ]

    phase = models.CharField("Fase", max_length=20, choices=PHASE_CHOICES)
    match_number = models.PositiveIntegerField("Numero do jogo")
    bracket_type = models.CharField(
        "Tipo de bracket", max_length=10, choices=BRACKET_CHOICES
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
        verbose_name="Grupo",
    )
    team_a = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_as_team_a",
        verbose_name="Time A",
    )
    team_b = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_as_team_b",
        verbose_name="Time B",
    )
    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_won",
        verbose_name="Vencedor",
    )
    status = models.CharField(
        "Status", max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    best_of = models.PositiveIntegerField("Melhor de", default=3)
    source_team_a = models.CharField(
        "Origem time A", max_length=100, blank=True, default=""
    )
    source_team_b = models.CharField(
        "Origem time B", max_length=100, blank=True, default=""
    )
    final_position_winner = models.PositiveIntegerField(
        "Posicao vencedor", null=True, blank=True
    )
    final_position_loser = models.PositiveIntegerField(
        "Posicao perdedor", null=True, blank=True
    )
    sort_order = models.PositiveIntegerField("Ordem", default=0)
    scheduled_date = models.DateTimeField("Data planejada", null=True, blank=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["sort_order", "match_number"]
        unique_together = [["match_number", "bracket_type"]]

    def __str__(self):
        team_a = self.source_team_a or str(self.team_a) if self.team_a else "A definir"
        team_b = self.source_team_b or str(self.team_b) if self.team_b else "A definir"
        return f"Jogo {self.match_number}: {team_a} vs {team_b}"

    def clean(self):
        errors = {}
        if self.best_of not in (1, 3):
            errors["best_of"] = "best_of deve ser 1 ou 3."
        if self.team_a_id and self.team_b_id and self.team_a_id == self.team_b_id:
            errors["team_b"] = "Time B deve ser diferente de Time A."
        if self.status == self.STATUS_FINISHED:
            if not self.team_a_id:
                errors["team_a"] = "Time A e obrigatorio para partida finalizada."
            if not self.team_b_id:
                errors["team_b"] = "Time B e obrigatorio para partida finalizada."
            if not self.winner_id:
                errors["winner"] = "Vencedor e obrigatorio para partida finalizada."
            elif self.winner_id not in (self.team_a_id, self.team_b_id):
                errors["winner"] = "Vencedor deve ser Time A ou Time B."
        if errors:
            raise ValidationError(errors)


class MatchSet(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="sets",
        verbose_name="Partida",
    )
    set_number = models.PositiveIntegerField("Set")
    team_a_points = models.PositiveIntegerField("Pontos time A", default=0)
    team_b_points = models.PositiveIntegerField("Pontos time B", default=0)

    class Meta:
        verbose_name = "Set"
        verbose_name_plural = "Sets"
        ordering = ["match", "set_number"]
        unique_together = [["match", "set_number"]]

    def __str__(self):
        return f"Set {self.set_number} - Jogo {self.match.match_number}: {self.team_a_points}x{self.team_b_points}"

    def clean(self):
        errors = {}
        if self.team_a_points == self.team_b_points:
            errors["team_a_points"] = "Set nao pode terminar empatado."
            errors["team_b_points"] = "Set nao pode terminar empatado."
        has_11 = self.team_a_points >= 11 or self.team_b_points >= 11
        if not has_11 and self.match_id and self.match.status == Match.STATUS_FINISHED:
            errors["team_a_points"] = "Pelo menos um lado deve atingir 11 pontos."
        if self.match_id:
            existing_count = MatchSet.objects.filter(match=self.match).exclude(
                pk=self.pk
            ).count()
            if existing_count + 1 > self.match.best_of:
                errors["set_number"] = (
                    f"Partida melhor de {self.match.best_of} permite no maximo "
                    f"{self.match.best_of} set(s)."
                )
        if errors:
            raise ValidationError(errors)