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
    team_number = models.PositiveIntegerField("Numero da dupla", default=0)
    player1_name = models.CharField("Jogador 1", max_length=100)
    player2_name = models.CharField("Jogador 2", max_length=100)

    class Meta:
        verbose_name = "Dupla"
        verbose_name_plural = "Duplas"
        ordering = ["team_number"]
        unique_together = [["player1_name", "player2_name", "group"]]

    def __str__(self):
        return f"Dupla {self.team_number}"

    def display_name(self, show_names=False):
        if show_names:
            return f"Dupla {self.team_number} - {self.player1_name} / {self.player2_name}"
        return f"Dupla {self.team_number}"


class Match(models.Model):
    PHASE_GROUP = "group"
    PHASE_QUARTERFINAL = "quarterfinal"
    PHASE_SEMIFINAL = "semifinal"
    PHASE_THIRD_PLACE = "third_place"
    PHASE_FINAL = "final"
    PHASE_FIFTH_TO_EIGHTH = "fifth_to_eighth"
    PHASE_SEVENTH_PLACE = "seventh_place"
    PHASE_FIFTH_PLACE = "fifth_place"
    PHASE_TWELFTH_TO_FOURTEENTH = "twelfth_to_fourteenth"
    PHASE_NINTH_TO_ELEVENTH = "ninth_to_eleventh"

    PHASE_CHOICES = [
        (PHASE_GROUP, "Fase de grupos"),
        (PHASE_QUARTERFINAL, "Quartas de final"),
        (PHASE_SEMIFINAL, "Semifinal"),
        (PHASE_THIRD_PLACE, "Disputa de 3\u00b0 lugar"),
        (PHASE_FINAL, "Final"),
        (PHASE_FIFTH_TO_EIGHTH, "Disputa de 5\u00b0 ao 8\u00b0"),
        (PHASE_SEVENTH_PLACE, "Disputa de 7\u00b0 e 8\u00b0"),
        (PHASE_FIFTH_PLACE, "Disputa de 5\u00b0 e 6\u00b0"),
        (PHASE_TWELFTH_TO_FOURTEENTH, "Disputa do 12\u00b0 ao 14\u00b0"),
        (PHASE_NINTH_TO_ELEVENTH, "Disputa do 9\u00b0 ao 11\u00b0"),
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
    STATUS_READY = "ready"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FINISHED = "finished"
    STATUS_BLOCKED = "blocked"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_READY, "Pronta"),
        (STATUS_IN_PROGRESS, "Em andamento"),
        (STATUS_FINISHED, "Finalizada"),
        (STATUS_BLOCKED, "Bloqueada"),
    ]

    phase = models.CharField("Fase", max_length=30, choices=PHASE_CHOICES)
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
    source_match_a = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_as_team_a",
        verbose_name="Jogo de origem time A",
        help_text="Partida que define o time A desta partida",
    )
    source_match_a_is_winner = models.BooleanField(
        "Time A e vencedor do jogo de origem",
        null=True,
        blank=True,
        help_text="True se time A vem do vencedor, False se do perdedor",
    )
    source_match_b = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_as_team_b",
        verbose_name="Jogo de origem time B",
        help_text="Partida que define o time B desta partida",
    )
    source_match_b_is_winner = models.BooleanField(
        "Time B e vencedor do jogo de origem",
        null=True,
        blank=True,
        help_text="True se time B vem do vencedor, False se do perdedor",
    )
    source_team_a = models.CharField(
        "Descricao origem time A", max_length=100, blank=True, default=""
    )
    source_team_b = models.CharField(
        "Descricao origem time B", max_length=100, blank=True, default=""
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
        if self.status == self.STATUS_READY:
            if not self.team_a_id:
                errors["team_a"] = "Time A e obrigatorio para partida pronta."
            if not self.team_b_id:
                errors["team_b"] = "Time B e obrigatorio para partida pronta."
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
        else:
            if self.team_a_points < 11 and self.team_b_points < 11:
                errors["team_a_points"] = "Pelo menos um lado deve atingir 11 pontos."
                errors["team_b_points"] = "Pelo menos um lado deve atingir 11 pontos."
            if self.team_a_points > 11 or self.team_b_points > 11:
                errors["team_a_points"] = "Pontuacao maxima por set e 11 pontos."
                errors["team_b_points"] = "Pontuacao maxima por set e 11 pontos."
        if self.match_id:
            best_of = self.match.best_of
            if self.set_number < 1 or self.set_number > best_of:
                errors["set_number"] = (
                    f"Numero do set deve estar entre 1 e {best_of}."
                )
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